"""
Flaechenzuordnungen
Diverse Tools zur QKan-Datenbank
"""

import os
from typing import Optional, cast

from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface

from qkan import QKan, enums, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_database import qgs_version
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
    meldung,
    warnung,
)
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
from .dialogs.dbAdapt import DbAdaptDialog
from .dialogs.empty_db import EmptyDBDialog
from .dialogs.filepath import QgsFileDialog
from .dialogs.help import QgsHelpDialog
from .dialogs.layersadapt import LayersAdaptDialog
from .dialogs.qgsadapt import QgsAdaptDialog
from .dialogs.qkanoptions import QKanOptionsDialog
from .dialogs.read_data import ReadData
from .dialogs.runoffparams import RunoffParamsDialog
from .k_dbAdapt import dbAdapt
from .k_filepath import setfilepath
from .k_layersadapt import layersadapt
from .k_qgsadapt import qgsadapt
from .k_runoffparams import setRunoffparams


class QKanTools(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.database_name: Optional[str] = None

        self.dlgla = LayersAdaptDialog(self)
        self.dlgop = QKanOptionsDialog(self)
        self.dlgpr = QgsAdaptDialog(self)
        self.dlgro = RunoffParamsDialog(self)
        self.dlged = EmptyDBDialog(self)
        self.dlgrd = ReadData(self, proceed=True)
        self.dlgrc = ReadData(self, proceed=False)
        self.dlgdb = DbAdaptDialog(self)
        self.dlghp = QgsHelpDialog(self)
        self.dlgfp = QgsFileDialog(self)
        self.iface = iface

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_qgsadapt_path = ":/plugins/qkan/tools/res/icon_qgsadapt.png"
        QKan.instance.add_action(
            icon_qgsadapt_path,
            text=self.tr("QKan-Projektdatei übertragen"),
            callback=self.run_qgsadapt,
            parent=self.iface.mainWindow(),
        )

        icon_layersadapt_path = ":/plugins/qkan/tools/res/icon_layersadapt.png"
        QKan.instance.add_action(
            icon_layersadapt_path,
            text=self.tr("QKan-Projekt aktualisieren"),
            callback=self.run_layersadapt,
            parent=self.iface.mainWindow(),
        )

        icon_qkanoptions_path = ":/plugins/qkan/tools/res/icon_qkanoptions.png"
        QKan.instance.add_action(
            icon_qkanoptions_path,
            text=self.tr("Allgemeine Optionen"),
            callback=self.run_qkanoptions,
            parent=self.iface.mainWindow(),
        )

        icon_runoffparams_path = ":/plugins/qkan/tools/res/icon_runoffparams.png"
        QKan.instance.add_action(
            icon_runoffparams_path,
            text=self.tr("Oberflächenabflussparameter eintragen"),
            callback=self.run_runoffparams,
            parent=self.iface.mainWindow(),
        )

        # TODO: Translations
        icon_emptyDB_path = ":/plugins/qkan/tools/res/icon_emptyDB.png"
        QKan.instance.add_action(
            icon_emptyDB_path,
            text=self.tr("Neue QKan-Datenbank erstellen"),
            callback=self.dlged.run,
            parent=self.iface.mainWindow(),
        )

        icon_readCheck_path = ":/plugins/qkan/tools/res/icon_readCheck.png"
        QKan.instance.add_action(
            icon_readCheck_path,
            text=self.tr("Tabellendaten aus Clipboard: Zuordnung anzeigen"),
            callback=self.dlgrc.run,
            parent=self.iface.mainWindow(),
        )

        icon_readData_path = ":/plugins/qkan/tools/res/icon_readData.png"
        QKan.instance.add_action(
            icon_readData_path,
            text=self.tr("Tabellendaten aus Clipboard einfügen"),
            callback=self.dlgrd.run,
            parent=self.iface.mainWindow(),
        )

        icon_dbAdapt_path = ":/plugins/qkan/tools/res/icon_dbAdapt.png"
        QKan.instance.add_action(
            icon_dbAdapt_path,
            text=self.tr("QKan-Datenbank aktualisieren"),
            callback=self.run_dbAdapt,
            parent=self.iface.mainWindow(),
        )

        icon_file_path = ":/plugins/qkan/tools/res/icon_filepath.png"
        QKan.instance.add_action(
            icon_file_path,
            text=self.tr("Dateipfade suchen"),
            callback=self.run_filepath,
            parent=self.iface.mainWindow(),
        )

        icon_help_path = ":/plugins/qkan/tools/res/icon_help.png"
        QKan.instance.add_action(
            icon_help_path,
            text=self.tr("Über QKan"),
            callback=self.run_help,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlgla.close()
        self.dlgop.close()
        self.dlgpr.close()
        self.dlgro.close()
        self.dlged.close()
        self.dlghp.close()
        # self.dlgrd.close()                    # doesn't use a form
        self.dlgdb.close()
        self.dlgfp.close()

    def run_qgsadapt(self) -> None:
        """Erstellen einer Projektdatei aus einer Vorlage"""

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.database_name, epsg = get_database_QKan(silent=True)

        if self.database_name:
            self.default_dir = os.path.dirname(
                self.database_name
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.database_name = QKan.config.database.qkan
            self.default_dir = os.path.dirname(self.database_name)
        self.dlgpr.tf_qkanDB.setText(self.database_name)

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgpr.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # Status initialisieren
        self.dlgpr.click_apply_template()

        # show the dialog
        self.dlgpr.show()
        # Run the dialog event loop
        result = self.dlgpr.exec_()

        # See if OK was pressed
        if result:
            # Inhalte aus Formular lesen --------------------------------------------------------------

            self.database_name = self.dlgpr.tf_qkanDB.text()
            project_file: str = self.dlgpr.tf_projectFile.text()
            self.apply_qkan_template = self.dlgpr.cb_applyQKanTemplate.isChecked()

            # QKanTemplate nur, wenn nicht Option "QKan_Standard_anwenden" gewählt
            if self.apply_qkan_template:
                project_template: str = os.path.join(QKan.template_dir, "Projekt.qgs")
            else:
                project_template = self.dlgpr.tf_projectTemplate.text()

            # Konfigurationsdaten schreiben -----------------------------
            if self.database_name:
                QKan.config.database.qkan = self.database_name
            QKan.config.project.file = project_file
            QKan.config.project.template = project_template
            QKan.config.tools.apply_qkan_template = self.apply_qkan_template

            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                qgsadapt(
                    "{project_template}",
                    "{self.database_name}",
                    N/A,
                    "{project_file}",
                    epsg = {epsg}, 
                )"""
            )

            # ------------------------------------------------------------------------------
            # Datenbankverbindungen
            if not self.database_name:
                return

            with DBConnection(dbname=self.database_name) as db_qkan:
                if not db_qkan.connected:
                    fehlermeldung(
                        "Fehler in k_qgsadapt:\n",
                        "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                            self.database_name
                        ),
                    )
                    return None

                qgsadapt(
                    self.database_name,
                    db_qkan,
                    project_file,
                    project_template,
                    epsg=epsg,
                )

            # ------------------------------------------------------------------------------
            # Abschluss: Ggfs. Protokoll schreiben

            self.iface.mainWindow().statusBar().clearMessage()
            self.iface.messageBar().pushMessage(
            "Information",
            "Projektdatei ist angepasst und muss neu geladen werden!",
            level=Qgis.Info,
            )

            # Importiertes Projekt laden
            # project = QgsProject.instance()
            # canvas = QgsMapCanvas(None)
            # bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(),
            # canvas)  # synchronise the loaded project with the canvas
            # project.read(QFileInfo(projectfile))  # read the new project file
            # logger.debug(u'Geladene Projektdatei: {}   ({})'.format(project.fileName()))

    def run_qkanoptions(self) -> None:
        """Bearbeitung allgemeiner QKan-Optionen"""

        # Formularfelder setzen -------------------------------------------------------------------------

        # Fangradius für Anfang der Anbindungslinie
        self.dlgop.tf_fangradius.setText(str(QKan.config.fangradius))

        # Abstand zwischen Zustandstexten
        self.dlgop.tf_abstand_zustandstexte.setText(str(QKan.config.zustand.abstand_zustandstexte))

        # Abstand zwischen Blöcken von Zustandstexten
        self.dlgop.tf_abstand_zustandsbloecke.setText(str(QKan.config.zustand.abstand_zustandsbloecke))

        # Stützstellen der Verbindungslinie zum Zustandstext
        self.dlgop.tf_abstand_knoten_anf.setText(str(QKan.config.zustand.abstand_knoten_anf))
        self.dlgop.tf_abstand_knoten_1.setText(str(QKan.config.zustand.abstand_knoten_1))
        self.dlgop.tf_abstand_knoten_2.setText(str(QKan.config.zustand.abstand_knoten_2))
        self.dlgop.tf_abstand_knoten_end.setText(str(QKan.config.zustand.abstand_knoten_end))

        # Mindestflächengröße
        self.dlgop.tf_mindestflaeche.setText(str(QKan.config.mindestflaeche))

        # Maximalzahl Schleifendurchläufe
        self.dlgop.tf_max_loops.setText(str(QKan.config.max_loops))

        # Optionen zum Typ der QKan-Datenbank
        datenbanktyp = QKan.config.database.type

        if datenbanktyp == enums.QKanDBChoice.SPATIALITE:
            self.dlgop.rb_spatialite.setChecked(True)
        # elif datenbanktyp == enums.QKanDBChoice.POSTGIS:
        # self.dlgop.rb_postgis.setChecked(True)

        epsg = QKan.config.epsg
        # noinspection PyCallByClass,PyArgumentList
        self.dlgop.qsw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(epsg))

        self.dlgop.tf_logeditor.setText(QKan.config.tools.logeditor)

        # Textfeld für Editor deaktivieren, falls leer:
        status_logeditor = QKan.config.tools.logeditor == ""
        self.dlgop.tf_logeditor.setEnabled(status_logeditor)

        self.dlgop.tf_panoramoplayer.setText(QKan.config.tools.panoramoplayer)

        # Textfeld für Editor deaktivieren, falls leer:
        status_panoramoplayer = QKan.config.tools.logeditor == ""
        self.dlgop.tf_panoramoplayer.setEnabled(status_panoramoplayer)

        # show the dialog
        self.dlgop.show()
        # Run the dialog event loop
        result = self.dlgop.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            fangradius: float = float(self.dlgop.tf_fangradius.text())
            abstand_zustandstexte: float = float(self.dlgop.tf_abstand_zustandstexte.text())
            abstand_zustandsbloecke: float = float(self.dlgop.tf_abstand_zustandsbloecke.text())
            abstand_knoten_anf: float = float(self.dlgop.tf_abstand_knoten_anf.text())
            abstand_knoten_1: float = float(self.dlgop.tf_abstand_knoten_1.text())
            abstand_knoten_2: float = float(self.dlgop.tf_abstand_knoten_2.text())
            abstand_knoten_end: float = float(self.dlgop.tf_abstand_knoten_end.text())
            mindestflaeche: float = float(self.dlgop.tf_mindestflaeche.text())
            max_loops: int = int(self.dlgop.tf_max_loops.text())
            logeditor: str = self.dlgop.tf_logeditor.text().strip()
            panoramoplayer: str = self.dlgop.tf_panoramoplayer.text().strip()
            if self.dlgop.rb_spatialite.isChecked():
                datenbanktyp = enums.QKanDBChoice.SPATIALITE
            # elif self.dlgop.rb_postgis.isChecked():
            # datenbanktyp = enums.QKanDBChoice.POSTGIS
            else:
                fehlermeldung(
                    "tools.application.run",
                    f"Fehlerhafte Option: \ndatenbanktyp = {datenbanktyp}",
                )
            epsg = int(self.dlgop.qsw_epsg.crs().postgisSrid())

            QKan.config.database.type = datenbanktyp
            if epsg:
                QKan.config.epsg = epsg
            QKan.config.fangradius = fangradius
            QKan.config.zustand.abstand_zustandstexte = abstand_zustandstexte
            QKan.config.zustand.abstand_zustandsbloecke = abstand_zustandsbloecke
            QKan.config.zustand.abstand_knoten_anf = abstand_knoten_anf
            QKan.config.zustand.abstand_knoten_1 = abstand_knoten_1
            QKan.config.zustand.abstand_knoten_2 = abstand_knoten_2
            QKan.config.zustand.abstand_knoten_end = abstand_knoten_end
            QKan.config.max_loops = max_loops
            QKan.config.mindestflaeche = mindestflaeche
            QKan.config.tools.logeditor = logeditor
            QKan.config.tools.panoramoplayer = panoramoplayer
            QKan.config.save()

    def run_runoffparams(self) -> None:
        """Berechnen und Eintragen der Oberflächenabflussparameter in die Tabelle flaechen"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({"flaechen"} & get_editable_layers()) > 0:
            warnung(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
            )
            return

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            self.log.error(
                "tools.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return
        self.dlgro.tf_qkanDB.setText(database_qkan)

        with DBConnection(dbname=database_qkan) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung(
                    "Fehler in tools.application.runoffparams:\n",
                    "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                        database_qkan
                    ),
                )
                return None

            # Check, ob alle Teilgebiete in Flächen auch in Tabelle "teilgebiete" enthalten
            sql = """INSERT INTO teilgebiete (tgnam)
                    SELECT teilgebiet FROM flaechen 
                    WHERE teilgebiet IS NOT NULL AND
                    teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                    GROUP BY teilgebiet"""
            if not db_qkan.sql(sql, "QKan_Tools.application.run (1) "):
                return

            # Check, ob alle Abflussparameter in Flächen auch in Tabelle "abflussparameter" enthalten
            sql = """INSERT INTO abflussparameter (apnam)
                    SELECT abflussparameter FROM flaechen 
                    WHERE abflussparameter IS NOT NULL AND
                    abflussparameter NOT IN (SELECT apnam FROM abflussparameter)
                    GROUP BY abflussparameter"""
            if not db_qkan.sql(sql, "QKan_Tools.application.run (2) "):
                return

            db_qkan.commit()

            # Anlegen der Tabelle zur Auswahl der Teilgebiete

            # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
            liste_teilgebiete = QKan.config.selections.teilgebiete

            # Abfragen der Tabelle teilgebiete nach Teilgebieten
            if not db_qkan.sql(
                'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"',
                "QKan_Tools.application.run (4) ",
            ):
                return
            daten = db_qkan.fetchall()

            self.dlgro.lw_teilgebiete.clear()

            for ielem, elem in enumerate(daten):
                self.dlgro.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                try:
                    if elem[0] in liste_teilgebiete:
                        self.dlgro.lw_teilgebiete.setCurrentRow(ielem)
                        self.dlgro.cb_selTgbActive.setChecked(True)
                except BaseException as err:
                    fehlermeldung(
                        "QKan_Tools (6), Fehler in elem = {}\n".format(elem), repr(err)
                    )
                    # if len(daten) == 1:
                    # self.dlgro.lw_teilgebiete.setCurrentRow(0)

            # Anlegen der Tabelle zur Auswahl der Abflussparameter

            # Zunächst wird die Liste der beim letzten Mal gewählten Abflussparameter aus config gelesen
            liste_abflussparameter = QKan.config.selections.abflussparameter

            # Abfragen der Tabelle abflussparameter nach Abflussparametern
            if not db_qkan.sql(
                'SELECT "apnam" FROM "abflussparameter" GROUP BY "apnam"',
                "QKan_Tools.application.run (4) ",
            ):
                return

            daten = db_qkan.fetchall()
            self.dlgro.lw_abflussparameter.clear()

            for ielem, elem in enumerate(daten):
                self.dlgro.lw_abflussparameter.addItem(QListWidgetItem(elem[0]))
                try:
                    if elem[0] in liste_abflussparameter:
                        self.dlgro.lw_abflussparameter.setCurrentRow(ielem)
                        self.dlgro.cb_selParActive.setChecked(True)
                except BaseException as err:
                    fehlermeldung(
                        "QKan_Tools (6), Fehler in elem = {}\n".format(elem), repr(err)
                    )
                    # if len(daten) == 1:
                    # self.dlgro.lw_abflussparameter.setCurrentRow(0)

            self.dlgro.db_qkan = db_qkan

            self.dlgro.count_selection()

            # Funktionen zur Berechnung des Oberflächenabflusses
            # Werden nur gelesen
            runoffparamsfunctions = QKan.config.tools.runoffparamsfunctions

            # Optionen zur Berechnung des Oberflächenabflusses
            runoffparamstype_choice = QKan.config.tools.runoffparamstype_choice

            if runoffparamstype_choice == enums.RunOffParamsType.ITWH:
                self.dlgro.rb_itwh.setChecked(True)
            elif runoffparamstype_choice == enums.RunOffParamsType.DYNA:
                self.dlgro.rb_dyna.setChecked(True)
            elif runoffparamstype_choice == enums.RunOffParamsType.MANIAK:
                self.dlgro.rb_maniak.setChecked(True)

            runoffmodeltype_choice = QKan.config.tools.runoffmodeltype_choice

            if runoffmodeltype_choice == enums.RunOffModelType.SPEICHERKASKADE:
                self.dlgro.rb_kaskade.setChecked(True)
            elif runoffmodeltype_choice == enums.RunOffModelType.FLIESSZEITEN:
                self.dlgro.rb_fliesszeiten.setChecked(True)
            elif runoffmodeltype_choice == enums.RunOffModelType.SCHWERPUNKTLAUFZEIT:
                self.dlgro.rb_schwerpunktlaufzeit.setChecked(True)

            # Status Radiobuttons initialisieren
            self.dlgro.toggle_itwh()

            # Formular anzeigen
            self.dlgro.show()
            # Run the dialog event loop
            result = self.dlgro.exec_()
            # See if OK was pressed

            if result:

                # Abrufen der ausgewählten Elemente in den Listen
                liste_teilgebiete = list_selected_items(self.dlgro.lw_teilgebiete)
                liste_abflussparameter = list_selected_items(self.dlgro.lw_abflussparameter)

                # Eingaben aus Formular übernehmen
                database_qkan = self.dlgro.tf_qkanDB.text()
                if self.dlgro.rb_itwh.isChecked():
                    runoffparamstype_choice = enums.RunOffParamsType.ITWH
                elif self.dlgro.rb_dyna.isChecked():
                    runoffparamstype_choice = enums.RunOffParamsType.DYNA
                elif self.dlgro.rb_maniak.isChecked():
                    runoffparamstype_choice = enums.RunOffParamsType.MANIAK
                else:
                    fehlermeldung(
                        "tools.runoffparams.run_runoffparams",
                        "Fehlerhafte Option: runoffparamstype_choice",
                    )
                if self.dlgro.rb_kaskade.isChecked():
                    runoffmodeltype_choice = enums.RunOffModelType.SPEICHERKASKADE
                elif self.dlgro.rb_fliesszeiten.isChecked():
                    runoffmodeltype_choice = enums.RunOffModelType.FLIESSZEITEN
                elif self.dlgro.rb_schwerpunktlaufzeit.isChecked():
                    runoffmodeltype_choice = enums.RunOffModelType.SCHWERPUNKTLAUFZEIT
                else:
                    fehlermeldung(
                        "tools.runoffparams.run_runoffparams",
                        "Fehlerhafte Option: runoffmodeltype_choice",
                    )

                # Konfigurationsdaten schreiben
                QKan.config.selections.abflussparameter = liste_abflussparameter
                QKan.config.selections.teilgebiete = liste_teilgebiete
                if database_qkan:
                    QKan.config.database.qkan = database_qkan
                QKan.config.tools.runoffmodeltype_choice = runoffmodeltype_choice
                QKan.config.tools.runoffparamstype_choice = runoffparamstype_choice

                QKan.config.save()

                # Modulaufruf in Logdatei schreiben
                self.log.debug(
                    f"""QKan-Modul Aufruf
                    setRunoffparams(
                        self.dbQK,
                        {runoffparamstype_choice},
                        {runoffmodeltype_choice},
                        {runoffparamsfunctions},
                        {liste_teilgebiete},
                        {liste_abflussparameter},
                    )"""
                )

                setRunoffparams(
                    db_qkan,
                    runoffparamstype_choice,
                    runoffmodeltype_choice,
                    runoffparamsfunctions,
                    liste_teilgebiete,
                    liste_abflussparameter,
                )

    def run_layersadapt(self) -> None:
        """Anpassen oder Ergänzen von Layern entsprechend der QKan-Datenstrukturen"""

        # QKan-Projekt
        # noinspection PyArgumentList
        project = QgsProject.instance()

        if project.count() == 0:
            warnung("Benutzerfehler: ", "Es ist kein Projekt geladen.")
            return

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.database_name, epsg = get_database_QKan(silent=True)

        if self.database_name:
            self.default_dir = os.path.dirname(
                self.database_name
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.database_name = QKan.config.database.qkan
            self.dlgla.tf_qkanDB.setText(self.database_name)
            self.default_dir = os.path.dirname(self.database_name)
        self.dlgla.tf_qkanDB.setText(self.database_name)

        with DBConnection(dbname=self.database_name) as db_qkan:
            # Falls die Datenbank nicht aktuell ist (self.dbIsUptodate = False), werden alle Elemente im Formular
            # deaktiviert. Nur der Checkbutton zur Aktualisierung der Datenbank bleibt aktiv und es erscheint
            # eine Information.
            self.db_is_uptodate = db_qkan.isCurrentVersion

        if not self.db_is_uptodate:
            fehlermeldung("Versionskontrolle", "Die QKan-Datenbank ist nicht aktuell")
            return

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgla.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # GGfs. Standardvorlage schon eintragen
        if self.apply_qkan_template:
            self.projectTemplate = os.path.join(QKan.template_dir, "Projekt.qgs")
            self.dlgla.tf_projectTemplate.setText(self.projectTemplate)

        # Groupbox "Layer anpassen" ---------------------------------------------------------------------------

        # Checkbox "Projektmakros"
        adapt_macros = QKan.config.adapt.macros
        self.dlgla.cb_adaptMacros.setChecked(adapt_macros)

        # Checkbox "Datenbankanbindung"
        adapt_db = QKan.config.adapt.database
        self.dlgla.cb_adaptDB.setChecked(adapt_db)

        # Checkbox "Projektionssystem anpassen"
        adapt_kbs = QKan.config.adapt.kbs
        self.dlgla.cb_adaptKBS.setChecked(adapt_kbs)

        # Checkbox "Wertbeziehungungen in Tabellen"
        adapt_table_lookups = QKan.config.adapt.table_lookups
        self.dlgla.cb_adaptTableLookups.setChecked(adapt_table_lookups)

        # Checkbox "Formularanbindungen"
        adapt_forms = QKan.config.adapt.forms
        self.dlgla.cb_adaptForms.setChecked(adapt_forms)

        # Groupbox "QKan-Layer" ---------------------------------------------------------------------------

        # Optionen zur Berücksichtigung der vorhandenen Tabellen
        adapt_selected = QKan.config.adapt.selected_layers
        if adapt_selected == enums.SelectedLayers.SELECTED:
            self.dlgla.rb_adaptSelected.setChecked(True)
        elif adapt_selected == enums.SelectedLayers.ALL:
            self.dlgla.rb_adaptAll.setChecked(True)
        else:
            fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
            return

        # Checkbox: Fehlende QKan-Layer ergänzen
        fehlende_layer_ergaenzen = QKan.config.adapt.add_missing_layers
        self.dlgla.cb_completeLayers.setChecked(fehlende_layer_ergaenzen)

        # Weitere Formularfelder ---------------------------------------------------------------------------

        # Checkbox: Knotentype per Abfrage ermitteln und in "schaechte.knotentyp" eintragen
        update_node_type = QKan.config.adapt.update_node_type
        self.dlgla.cb_updateNodetype.setChecked(update_node_type)

        # Checkbox: Nach Aktualisierung auf alle Layer zoomen
        self.dlgla.cb_zoomAll.setChecked(QKan.config.adapt.zoom_all)

        # Checkbox: QKan-Standard anwenden
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgla.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # Status initialisieren
        self.dlgla.click_apply_template()
        self.dlgla.enable_project_template_group()

        # -----------------------------------------------------------------------------------------------------
        # show the dialog
        self.dlgla.show()
        # Run the dialog event loop
        result = self.dlgla.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            self.database_name = self.dlgla.tf_qkanDB.text()
            adapt_db = self.dlgla.cb_adaptDB.isChecked()
            adapt_macros = self.dlgla.cb_adaptMacros.isChecked()
            adapt_table_lookups = self.dlgla.cb_adaptTableLookups.isChecked()
            adapt_forms = self.dlgla.cb_adaptForms.isChecked()
            adapt_kbs = self.dlgla.cb_adaptKBS.isChecked()
            update_node_type = self.dlgla.cb_updateNodetype.isChecked()
            zoom_alles = self.dlgla.cb_zoomAll.isChecked()
            self.apply_qkan_template = self.dlgla.cb_applyQKanTemplate.isChecked()
            if self.apply_qkan_template:
                self.projectTemplate = ""
            else:
                self.projectTemplate = self.dlgla.tf_projectTemplate.text()

            # Optionen zur Berücksichtigung der vorhandenen Tabellen
            fehlende_layer_ergaenzen = self.dlgla.cb_completeLayers.isChecked()
            if self.dlgla.rb_adaptAll.isChecked():
                adapt_selected = enums.SelectedLayers.ALL
            elif self.dlgla.rb_adaptSelected.isChecked():
                adapt_selected = enums.SelectedLayers.SELECTED
            else:
                fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
                return

            # Konfigurationsdaten schreiben -----------------------------------------------------------

            QKan.config.adapt.add_missing_layers = fehlende_layer_ergaenzen
            QKan.config.adapt.database = adapt_db
            QKan.config.adapt.forms = adapt_forms
            QKan.config.adapt.kbs = adapt_kbs
            QKan.config.adapt.selected_layers = adapt_selected
            QKan.config.adapt.macros = adapt_macros
            QKan.config.adapt.table_lookups = adapt_table_lookups
            QKan.config.adapt.update_node_type = update_node_type
            QKan.config.adapt.zoom_all = zoom_alles
            QKan.config.database.qkan = cast(str, self.database_name)
            QKan.config.tools.apply_qkan_template = self.apply_qkan_template
            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                layersadapt(
                    "{self.database_name}",
                    "{self.projectTemplate}",
                    {adapt_macros},
                    {adapt_db},
                    {adapt_table_lookups},
                    {adapt_forms},
                    {adapt_kbs},
                    {update_node_type},
                    {zoom_alles},
                    {fehlende_layer_ergaenzen},
                    {adapt_selected},
                )"""
            )

            layersadapt(
                cast(str, self.database_name),
                self.projectTemplate,
                adapt_macros,
                adapt_db,
                adapt_table_lookups,
                adapt_forms,
                adapt_kbs,
                update_node_type,
                zoom_alles,
                fehlende_layer_ergaenzen,
                adapt_selected,
            )

    def run_dbAdapt(self) -> None:
        """Aktualisiert die QKan-Datenbank"""

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.database_name, epsg = get_database_QKan(silent=True)

        if self.database_name:
            self.default_dir = os.path.dirname(
                self.database_name
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.database_name = QKan.config.database.qkan
            self.default_dir = os.path.dirname(self.database_name)
        self.dlgdb.tf_qkanDB.setText(self.database_name)

        with DBConnection(dbname=self.database_name) as db_qkan:
            if db_qkan.isCurrentVersion:
                db_qkan.sql("SELECT RecoverSpatialIndex()")  # Geometrie-Indizes bereinigen
                self.iface.mapCanvas().refresh()  # Grafik aktualisieren
                meldung("Information", "Spatial Index wurde bereinigt...")
                meldung("Information", "QKan-Datenbank ist aktuell")
                return

        # Falls Projektdatei geändert wurde, Gruppe zum Speichern der Projektdatei anzeigen
        # noinspection PyArgumentList
        project = QgsProject.instance()
        project_is_dirty = project.isDirty()
        self.dlgdb.gb_updateQkanDB.setEnabled(project_is_dirty)

        self.log.debug("QKan.tools.application.run_dbAdapt: before dlgdb.show()")

        # show the dialog
        self.dlgdb.show()

        self.log.debug("QKan.tools.application.run_dbAdapt: before dlgdb.exec_()")

        # Run the dialog event loop
        result = self.dlgdb.exec_()

        self.log.debug("QKan.tools.application.run_dbAdapt: after dlgdb.exec_()")

        # See if OK was pressed
        if result:

            self.database_name = self.dlgdb.tf_qkanDB.text()
            project_file: str = self.dlgdb.tf_projectFile.text()

            # Konfigurationsdaten schreiben -----------------------------
            QKan.config.database.qkan = cast(str, self.database_name)

            if project_is_dirty:
                QKan.config.project.file = project_file
            else:
                project_file = ""

            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                dbAdapt(
                    "{self.database_name}",
                    "{project_file}",
                    "{project}", 
                )"""
            )

            dbAdapt(
                cast(str, self.database_name),
                project_file,
                project,
            )

    def run_help(self) -> None:

        version = qgs_version()

        self.dlghp.textBrowser_2.setText(str(version))

        # show the dialog
        self.dlghp.show()
        # Run the dialog event loop
        result = self.dlghp.exec_()


    def run_filepath(self) -> None:
        self.database_name, epsg = get_database_QKan(silent=True)

        # with DBConnection(dbname=self.database_name) as db_qkan:
        #     if not db_qkan.connected:
        #         fehlermeldung(
        #             "Fehler Info",
        #             f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
        #         )
        #         self.iface.messageBar().pushMessage(
        #             "Fehler Info",
        #             f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
        #             level=Qgis.Critical,
        #         )
        #         return False

        # show the dialog
        self.dlgfp.show()

        # Run the dialog event loop
        result = self.dlgfp.exec()

        # See if OK was pressed
        if result:

            # Abrufen der ausgewählten Elemente in den Listen
            videopath = self.dlgfp.lineEdit.text()
            fotopath = self.dlgfp.lineEdit_2.text()
            fotopath_2 = self.dlgfp.lineEdit_3.text()
            ausw_haltung = self.dlgfp.checkBox.isChecked()
            ausw_schacht = self.dlgfp.checkBox_2.isChecked()

            #QKan.config.save()

            setfilepath(
                self.database_name,
                videopath,
                fotopath,
                fotopath_2,
                ausw_haltung,
                ausw_schacht,
            )




