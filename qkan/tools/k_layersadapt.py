"""

  Adapt QKan-Layers to QKan-Standard
  ==============

  Für ein bestehendes Projekt werden alle oder ausgewählte Layer auf den QKan-Standard
  (zurück-) gesetzt. Dabei können optional der Layerstil, die Werteanbindungen, die
  Formularverknüpfung sowie die Datenbankanbindung bearbeitet werden.

  | Dateiname            : k_layersadapt.py
  | Date                 : September 2018
  | Copyright            : (C) 2018 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

"""

import os
from typing import cast
from xml.etree import ElementTree

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsDataSourceUri,
    QgsProject,
    QgsVectorLayer,
    QgsAction,
)
from qgis.utils import pluginDirectory

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_database import qgs_actual_version, qgs_version
from qkan.database.qkan_utils import (
    eval_node_types,
    fehlermeldung,
    list_qkan_layers,
    meldung,
    warnung,
)
from qkan.utils import get_logger

__author__ = "Joerg Hoettges"
__date__ = "September 2018"
__copyright__ = "(C) 2018, Joerg Hoettges"


logger = get_logger("QKan.tools.k_layersadapt")

progress_bar = None

def load_plausisql(dbQK):
    """Lädt die Standardplausibilitätsprüfungen in die Tabelle 'pruefsql'"""
    templateDir = os.path.join(pluginDirectory("qkan"), "templates")
    filenam = os.path.join(templateDir, 'Plausibilitaetspruefungen.sql')
    if dbQK.executefile(filenam):
        logger.debug(f"Plausibilitätsabfragen aus Datei {filenam} eingelesen")
    else:
        fehlermeldung("Fehler beim Lesen der Plausibilitätsabfragen:",
                      f"Die Datei {filenam} konnten nicht gelesen werden!")
        return False
    dbQK.commit()
    return True


def load_plausiaction(layer):
    """Lädt für den Layer 'Fehlerliste' die Aktion zum Aktivieren und Zoomen auf das fehlerhaft Objekt"""
    iconPath = os.path.join(pluginDirectory("qkan"), "datacheck/res/jump.png")
    acManager = layer.actions()

    code = """from qgis.PyQt import QtWidgets
    from qgis.core import Qgis

    obj = '[%objname%]'
    attr = '[%attrname%]'

    activeproject = QgsProject().instance()
    layername = '[%layername%]'
    clayers = activeproject.mapLayersByName(layername)
    if not clayers:
        QtWidgets.QMessageBox.information(None, "Fehler im Programmcode der Aktion", 
                                          f'Layer "{layername}"nicht definiert'
        )
    else:
        clayer = clayers[0]
        clayer.selectByExpression(f"{attr} = '{obj}'")
        qgis.utils.iface.setActiveLayer(clayer)
        qgis.utils.iface.actionZoomToSelected().trigger()
    """
    acActor = QgsAction(QgsAction.GenericPython, "Objekt Aktivieren und Zoom/Pan zum Objekt", code,
                        iconPath, False, "Zoom/Pan zum Objekt",
                        actionScopes={'Feature'}, notificationMessage='Meldung')
    acManager.addAction(acActor)


def layersadapt(
    database_QKan: [str, None],
    projectTemplate: str,
    anpassen_ProjektMakros: bool,
    anpassen_Datenbankanbindung: bool,
    anpassen_Layerstile: bool,
    anpassen_Formulare: bool,
    anpassen_Projektionssystem: bool,
    aktualisieren_Schachttypen: bool,
    zoom_alles: bool,
    fehlende_layer_ergaenzen: bool,
    anpassen_auswahl: enums.SelectedLayers,
) -> None:
    """Projektlayer werden an den QKan-Standard angepasst.
    Voraussetzungen: Geladenes QKan-Projekt oder Einstellung, dass nur Formulare angepasst werden.

    :database_QKan:                                 Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :projectTemplate:                               Vorlage-Projektdatei für die anzupassenden Layereigenschaften
    :anpassen_ProjektMakros:                        Projektmakros werden angepasst
    :anpassen_Datenbankanbindung:                   Datenbankanbindungen werden angepasst
    :anpassen_Layerstile:                           Layerstile werden mit den qml-Dateien aus dem Verzeichnis templates/qml aktualisiert
    :anpassen_Formulare:                            Formulare werden anpasst
    :anpassen_Projektionssystem:                    Projektionssystem wird angepasst
    :aktualisieren_Schachttypen:                    Knotentypen in schaechte.knotentyp setzen
    :zoom_alles:                                    Nach der Bearbeitung die Karte auf gesamte Gebiet zoomen
    :fehlende_layer_ergaenzen:                      Fehlende QKan-Layer werden ergänzt
    :anpassen_auswahl:                              Wahl der anzupassenden Layer

    :returns: void
    """

    # -----------------------------------------------------------------------------------------------------
    # Datenbankverbindungen

    iface = QKan.instance.iface

    if database_QKan is not None:
        dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank

        if not dbQK.connected:
            errormsg = "Programmfehler in QKan.tools.k_layersadapt.layersadapt()\n" + \
            f"Datenbank {database_QKan} konnte nicht verbunden werden"
            logger.error(errormsg)
            raise Exception(f"{__name__}: {errormsg}")

        actversion = dbQK.actDbVersion
        logger.debug("actversion: {}".format(actversion))
    else:
        if (anpassen_ProjektMakros
            or anpassen_Datenbankanbindung
            or anpassen_Projektionssystem
            or aktualisieren_Schachttypen
            or zoom_alles
            or fehlende_layer_ergaenzen
        ):
            errormsg = "Interner Fehler: Aufruf von k_layersadapt ohne Anpassung der Datenbankanbindung darf nur " + \
                       "Formularanbindung und/oder Layeranpassung durchführen"
            logger.error(errormsg)
            raise Exception(f"{__name__}: {errormsg}")
        dbQK = None                                # Bei Korrektur der Formularanbindung keine Datenbankanbindung

    # -----------------------------------------------------------------------------------------------------
    # QKan-Projekt

    # noinspection PyArgumentList
    project = QgsProject.instance()

    # Vorlage-Projektdatei. Falls Standard oder keine Vorgabe, wird die Standard-Projektdatei verwendet

    templateDir = os.path.join(pluginDirectory("qkan"), "templates")
    if projectTemplate is None or projectTemplate == "":
        projectTemplate = os.path.join(templateDir, "Projekt.qgs")

    logger.debug("Projekttemplate: {}".format(projectTemplate))

    # Liste aller QKan-Layernamen aus gewählter QGS-Vorlage.
    # Dabei wird trotzdem geprüft, ob es sich um einen QKan-Layer handelt; es könnte sich ja um eine
    # vom Benutzer angepasste Vorlage handeln.

    qkanLayers = list_qkan_layers(
        projectTemplate
    )  # Liste aller Layernamen aus gewählter QGS-Vorlage
    # logger.debug(u'qkanLayers: {}'.format(qkanLayers))

    # Fehlende Layer ergänzen. Unabhängig von der Auswahl werden die fehlenden Referenztabellen
    # auf jeden Fall ergänzt.

    layersRoot = project.layerTreeRoot()
    for layername in qkanLayers:
        layer = None
        if len(project.mapLayersByName(layername)) == 0:
            # layername fehlt in aktuellem Projekt
            isVector = (
                qkanLayers[layername][1] != ""
            )  # Test, ob Vorlage-Layer spatial ist
            if not isVector or fehlende_layer_ergaenzen:
                # Referenzlisten werden auf jeden Fall ergänzt.
                table, geom, sql, group = qkanLayers[layername]
                uri = QgsDataSourceUri()
                uri.setDatabase(database_QKan)
                uri.setDataSource(sql, table, geom)
                try:
                    layer = QgsVectorLayer(
                        uri.uri(), layername, enums.QKanDBChoice.SPATIALITE.value
                    )
                except BaseException as err:
                    fehlermeldung(
                        "Fehler in k_layersadapt (1): {}".format(err),
                        "layername: {}".format(layername),
                    )
                    del dbQK
                    return
                project.addMapLayer(layer, False)
                atcGroup = layersRoot.findGroup(group)
                if atcGroup is None:
                    atcGroup = layersRoot.addGroup(group)
                atcGroup.addLayer(layer)

                layer_exists = True
                logger.debug("k_layersadapt: Layer ergänzt: {}".format(layername))
            else:
                logger.debug("k_layersadapt: Layer nicht ergänzt: {}".format(layername))

    # Dictionary, das alle LayerIDs aus der Template-Projektdatei den entsprechenden (QKan-) LayerIDs
    # des aktuell geladenen Projekts zuordnet. Diese Liste wird bei der Korrektur der Wertelisten
    # benötigt.

    qgsxml = ElementTree.ElementTree()
    qgsxml.parse(projectTemplate)

    layerNotInProjektMeldung = False
    rltext = "projectlayers/maplayer"
    nodes_refLayerTemplate = qgsxml.findall(rltext)
    layerIdList = {}
    for node in nodes_refLayerTemplate:
        refLayerName = node.findtext("layername")
        refLayerId = node.findtext("id")
        layerobjects = project.mapLayersByName(refLayerName)
        for layer in layerobjects:
            layerId = layer.id()
            logger.debug("layerId: {}".format(layerId))
            layerIdList[refLayerId] = layerId
            # if len(layerobjects) > 1:
            #     warnung(
            #         "Layername doppelt: {}".format(refLayerName),
            #         "Es wird nur ein Layer bearbeitet.",
            #     )
        # else:
        #     layerNotInProjektMeldung = (
        #         not fehlende_layer_ergaenzen
        #     )  # nur setzen, wenn keine Ergänzung gewählt
        #     logger.info(
        #         "k_layersadapt: QKan-Layer nicht in Projekt: {}".format(refLayerName)
        #     )
    logger.debug("Refliste Layer-Ids: \n{}".format(layerIdList))

    selectedLayerNames = []
    # Liste der zu bearbeitenden Layer
    if anpassen_auswahl == enums.SelectedLayers.SELECTED:
        # Im Formular wurde "nur ausgewählte Layer" angeklickt

        selectedLayers = iface.layerTreeCanvasBridge().rootGroup().checkedLayers()
        selectedLayerNames = [lay.name() for lay in selectedLayers]
    elif anpassen_auswahl == enums.SelectedLayers.ALL:
        legendLayers = iface.layerTreeCanvasBridge().rootGroup().findLayers()
        selectedLayerNames = [lay.name() for lay in legendLayers]
    elif anpassen_auswahl == enums.SelectedLayers.NONE:
        selectedLayerNames = []
    else:
        logger.error(
            "Fehler in anpassen_auswahl: %s\nWert ist nicht definiert (enums.py)",
            anpassen_auswahl,
        )

    logger.debug("k_layersadapt (2), selectedLayerNames: %s", selectedLayerNames)
    logger.debug(f"k_layersadapt (5), qkanLayers: {qkanLayers}")

    layerNotQkanMeldung = False  # Am Schluss erscheint ggfs. eine Meldung, dass Nicht-QKan-Layer gefunden wurden.

    # Alle (ausgewählten) Layer werden jetzt anhand der entsprechenden Layer des Template-Projektes angepasst

    formsDir = os.path.join(pluginDirectory("qkan"), "forms")

    for layername in selectedLayerNames:
        # Nur Layer behandeln, die in der Vorlage-Projektdatei enthalten sind, d.h. QKan-Layer sind.
        if layername not in qkanLayers:
            logger.debug(
                f"k_layersadapt (4): layername nicht in qkanLayers: {layername}"
            )
            continue

        logger.debug(f"k_layersadapt (3), layername: {layername}")

        layerobjects = project.mapLayersByName(layername)
        if len(layerobjects) == 0:
            logger.error(
                f"QKan-Fehler: Projektlayer {layername} konnte im Projekt nicht gefunden werden"
            )
            return

        for layer in layerobjects:
            # Mehrere Layer mit gleichem Namen werden gleich behandelt

            # Nachfolgende Variable werden an verschiedenen Stellen benötigt
            table, geom, sql, _ = qkanLayers[layername]

            if anpassen_Layerstile:
                qlsnam = os.path.join(templateDir, "qml",
                                      "{}.qml".format(layername.replace('/', '_')))
                if os.path.exists(qlsnam):
                    layer.loadNamedStyle(qlsnam)
                    layer.triggerRepaint()
                    logger.debug("Layerstil geladen (2): {}".format(qlsnam))
                if layer.name() == 'Plausibilitätsprüfungen' and dbQK is not None:
                    load_plausisql(dbQK)
                    logger.debug("Plausibilitätsprüfungen mit Datei 'Plausibilitaetspruefungen.sql' ergänzt.")

                # nachfolgende Zeilen sind nicht notwendig, da in Projektdatei schon enthalten:
                # elif layer.name() == 'Fehlerliste':
                #     load_plausiaction(layer)
                #     logger.debug("Aktion 'Zoom zum Objekt' für Layer 'Fehlerliste' ergänzt")

            if anpassen_Datenbankanbindung:
                if geom != "":
                    # Vektorlayer
                    newdatasource = (
                        "dbname='{dbname}' table=\"{table}\" ({geom}) sql={sql}".format(
                            dbname=database_QKan, table=table, geom=geom, sql=sql
                        )
                    )
                else:
                    # Tabellenlayer
                    newdatasource = "dbname='{dbname}' table=\"{table}\" sql={sql}".format(
                        dbname=database_QKan, table=table, sql=sql
                    )
                layer.setDataSource(
                    newdatasource, layername, enums.QKanDBChoice.SPATIALITE.value
                )
                logger.debug("\nAnbindung neue QKanDB: {}\n".format(newdatasource))

            if anpassen_Projektionssystem:
                # epsg-Code des Layers an angebundene Tabelle anpassen
                logger.debug("anpassen_Projektionssystem...")
                logger.debug("Prüfe KBS von Tabelle {}".format(table))
                if geom != "":
                    # Nur für Vektorlayer
                    sql = """SELECT srid
                            FROM geom_cols_ref_sys
                            WHERE Lower(f_table_name) = Lower(?)
                            AND Lower(f_geometry_column) = Lower(?)"""
                    if not dbQK.sql(
                        sql, "db_qkan: k_layersadapt (3)", parameters=(table, geom)
                    ):
                        del dbQK
                        return

                    data = dbQK.fetchone()
                    if data is not None:
                        epsg = data[0]
                    else:
                        logger.debug("\nTabelle hat kein KBS: {}\n".format(table))

                    crs = QgsCoordinateReferenceSystem.fromEpsgId(epsg)
                    if crs.isValid():
                        layer.setCrs(crs)
                        logger.debug(
                            'KBS angepasst für Tabelle "{0:} auf {1:}"'.format(
                                table, crs.postgisSrid()
                            )
                        )
                    else:
                        fehlermeldung(
                            "Fehler bei Festlegung des Koordinatensystems!",
                            "Layer {}".format(layername),
                        )

            if anpassen_Formulare:
                tagLayer = (
                    f"projectlayers/maplayer[layername='{layername}'][provider='spatialite']"
                )
                qgsLayers = qgsxml.findall(tagLayer)
                if len(qgsLayers) == 0:
                    logger.info(
                        "In der Vorlage-Projektdatei wurden kein Layer {} gefunden".format(
                            layername
                        )
                    )
                    continue  # Layer ist in Projekt-Templatenicht vorhanden...
                else:
                    logger.debug(f"In Vorlage-Projektdatei gefundener Layer: {layername}")

                for qgslay in qgsLayers:
                    formpath = qgslay.findtext("./editform") or ""
                    form = cast(str, os.path.basename(formpath))
                    editFormConfig = layer.editFormConfig()
                    editFormConfig.setUiForm(os.path.join(formsDir, form))
                    layer.setEditFormConfig(editFormConfig)
                    logger.debug(
                        f"k_layersadapt\nformpath: {formpath}\nform: {form}\nformsDir: {formsDir}\n"
                    )

    if layerNotInProjektMeldung:
        meldung(
            "Information zu den Layern",
            "Es fehlten Layer, die zum QKan-Standard gehörten. Eine Liste steht in der LOG-Datei...",
        )
    # if layerNotQkanMeldung:
    # meldung(u'Information zu den Layern', u'Es wurden Layer gefunden, die nicht zum QKan-Standard gehörten. Eine Liste steht in der LOG-Datei...')

    # Projektmakros
    if anpassen_ProjektMakros:
        nodes = qgsxml.findall("properties/Macros")
        for node in nodes:
            macros = node.findtext("pythonCode")
        project.writeEntry("Macros", "/pythonCode", macros)

    # Code war doppeot:
    # rltext = "properties/Macros/pythonCode"
    # macrotext = qgsxml.findtext(rltext)
    # project.writeEntry("Macros", "/pythonCode", macrotext)

    if aktualisieren_Schachttypen:
        # Schachttypen auswerten
        eval_node_types(dbQK)  # in qkan.database.qkan_utils

    # Wenn noch kein Titel vergeben, dann QKan mit Versionsnummer setzen
    if not project.title():
        project.setTitle("QKan Version {}".format(qgs_version()))

    # if status_neustart:
    # meldung("Achtung! Benutzerhinweis!", "Die Datenbank wurde geändert. Bitte QGIS-Projekt neu laden...")
    # return False

    # Zoom auf alles
    if zoom_alles:
        # Tabellenstatistik aktualisieren, damit Zoom alles richtig funktioniert ...
        if not dbQK.sql("SELECT UpdateLayerStatistics()", "db_qkan: k_layersadapt (5)"):
            del dbQK
            return

        canvas = iface.mapCanvas()
        canvas.zoomToFullExtent()

    del qgsxml
    del dbQK

    # Projekt auf aktuelle Version setzen. Es werden keine Layer geändert.
    # qgs_actual_version()

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(
        "Information",
        "Projektdatei ist angepasst und muss noch gespeichert werden!",
        level=Qgis.Info,
    )

    return

