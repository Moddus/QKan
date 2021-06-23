# -*- coding: utf-8 -*-

"""

  Datenbankmanagement der QKan-Datenbank
  ======================================

  Erstellt eine leere QKan-Datenbank und legt die Referenztabellen an.

  | Dateiname            : qkan_database.py
  | Date                 : October 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

"""

__author__ = "Joerg Hoettges"
__date__ = "August 2019"
__copyright__ = "(C) 2016, Joerg Hoettges"
__dbVersion__ = "3.2.8"  # Version der QKan-Datenbank
__qgsVersion__ = "3.2.8"  # Version des Projektes und der Projektdatei. Kann höher als die der QKan-Datenbank sein


import logging
import os
import traceback
from sqlite3.dbapi2 import Connection, Cursor

from qgis.core import Qgis, QgsProject
from qgis.PyQt import Qt
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import iface, spatialite_connect

from .qkan_utils import fehlermeldung, fortschritt, meldung

logger = logging.getLogger("QKan.database.qkan_database")


def db_version() -> str:
    """Returns actual version of the QKan database"""
    return __dbVersion__


def qgs_version() -> str:
    """Returns actual project version"""
    return __qgsVersion__


def qgs_actual_version(update: bool = True, warning: bool = False) -> bool:
    """Prüft die Version des aktiven Projektes und aktualisiert die Layer gegebenenfalls

    :param warning: Aktiviert Warnung in QGIS-Meldungsleiste

    Prüft im Vergleich zur Version der QKan-Datenbank, ob das geladene Projekt die gleiche oder höhere
    Versionsnummer aufweist.
    """

    layers = iface.layerTreeCanvasBridge().rootGroup().findLayers()
    if len(layers) == 0 and warning:
        logger.error("qkan_database.qgs_actual_version: Keine Layer vorhanden...")
        meldung("Fehler: ", "Kein QKan-Projekt geladen!")
        return False

    # noinspection PyArgumentList
    act_qgs_version = QgsProject.instance().title().replace("QKan Version ", "")
    if act_qgs_version == "":
        if len(layers) == 0:
            meldung("Benutzerfehler: ", "Es ist kein Projekt geladen")
        else:
            act_qgs_version = "2.5.3"  # davor wurde die Version der Projektdatei noch nicht verwaltet.
    cur_qgs_version = qgs_version()
    try:
        act_qgs_version_lis = [
            int(el.replace("a", "").replace("b", "").replace("c", ""))
            for el in act_qgs_version.split(".")
        ]
    except BaseException as err:
        logger.error(
            "\nqkan_database.qgs_actual_version: {}\nVersionsstring fehlerhaft: {}".format(
                err, act_qgs_version
            )
        )
        act_qgs_version = (
            "2.5.3"  # davor wurde die Version der Projektdatei noch nicht verwaltet.
        )
        act_qgs_version_lis = [
            int(el.replace("a", "").replace("b", "").replace("c", ""))
            for el in act_qgs_version.split(".")
        ]

    cur_qgs_version_lis = [
        int(el.replace("a", "").replace("b", "").replace("c", ""))
        for el in cur_qgs_version.split(".")
    ]

    logger.debug("act_qgs_version: {}".format(act_qgs_version))
    logger.debug("cur_qgs_version: {}".format(cur_qgs_version))

    # Änderungen an den Layern werden nur in layersadapt vorgenommen.

    #
    # isActual = not versionolder(act_qgs_version_lis, cur_qgs_version_lis)
    # if not isActual:
    #     if warning:
    #         meldung(
    #             "Warnung: ",
    #             "Das geladene Projekt entspricht nicht der aktuellen Version. ",
    #         )
    #     if update:
    #
    #         # Bis Version 2.5.11
    #         if versionolder(act_qgs_version_lis, [2, 5, 12]):
    #             wlayers = [la for la in layers if la.name() == "Abflussparameter"]
    #             if len(wlayers) != 1:
    #                 logger.debug(
    #                     'Fehler in Layerliste: Es gibt mehr als einen Layer "Abflussparameter"'
    #                 )
    #                 layerList = [la.name() for la in layers]
    #                 logger.debug("layerList: {}".format(layerList))
    #                 return False
    #             wlayer = wlayers[0]
    #             logger.debug("vorher: wlayer.name(): {}".format(wlayer.name()))
    #             wlayer.setName("Abflussparameter HE")
    #             logger.debug("nachher: wlayer.name(): {}".format(wlayer.name()))
    #
    #             project = QgsProject.instance()
    #             project.setTitle("QKan Version {}".format(qgs_version()))
    #
    #         isActual = True
    # return isActual

    return True


# Erzeuge QKan-Tabellen


def createdbtables(
    consl: Connection, cursl: Cursor, version: str = __dbVersion__, epsg: int = 25832
) -> bool:
    """Erstellt fuer eine neue QKan-Datenbank die benötigten Tabellen.

    :param consl: Datenbankobjekt der SpatiaLite-QKan-Datenbank
    :param cursl: Zugriffsobjekt der SpatiaLite-QKan-Datenbank
    :param version: Database version
    :param epsg: EPSG ID

    :returns: Testergebnis: True = alles o.k.
    """

    # Haltungen ----------------------------------------------------------------

    sql = """CREATE TABLE haltungen (
    pk INTEGER PRIMARY KEY,
    haltnam TEXT,
    schoben TEXT,
    schunten TEXT,
    hoehe REAL,
    breite REAL,
    laenge REAL,
    sohleoben REAL,
    sohleunten REAL,
    deckeloben REAL,
    deckelunten REAL,
    teilgebiet TEXT,
    qzu REAL,
    profilnam TEXT DEFAULT 'Kreisquerschnitt',
    entwart TEXT DEFAULT 'Regenwasser',
    rohrtyp TEXT,
    ks REAL DEFAULT 1.5,
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')),
    xschob REAL,
    yschob REAL,
    xschun REAL,
    yschun REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Haltungen" konnte nicht erstellt werden',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('haltungen','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Haltungen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS haltungen_data AS
          SELECT 
            haltnam, schoben, schunten, 
            hoehe, breite, laenge, 
            sohleoben, sohleunten, 
            deckeloben, deckelunten, 
            teilgebiet, qzu, profilnam, 
            entwart, rohrtyp, ks,
            simstatus, kommentar, createdat, 
            xschob, yschob, xschun, yschun
          FROM haltungen;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "schaechte_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS haltungen_insert_clipboard
            INSTEAD OF INSERT ON haltungen_data FOR EACH ROW
          BEGIN
            INSERT INTO haltungen
              (haltnam, schoben, schunten,
               hoehe, breite, laenge,
               sohleoben, sohleunten,
               deckeloben, deckelunten, 
               teilgebiet, qzu, profilnam, 
               entwart, rohrtyp, ks,
               simstatus, kommentar, createdat,  
               geom)
            SELECT 
              new.haltnam, new.schoben, new.schunten, 
              CASE WHEN new.hoehe > 20 THEN new.hoehe/1000 ELSE new.hoehe END, 
              CASE WHEN new.breite > 20 THEN new.breite/1000 ELSE new.breite END,
              new.laenge, 
              new.sohleoben, new.sohleunten, 
              new.deckeloben, new.deckelunten, 
              new.teilgebiet, new.qzu, coalesce(new.profilnam, 'Kreisquerschnitt'), 
              coalesce(new.entwart, 'Regenwasser'), new.rohrtyp, coalesce(new.ks, 1.5), 
              coalesce(new.simstatus, 'vorhanden'), new.kommentar, 
              coalesce(new.createdat, datetime('now')), 
              MakeLine(
                coalesce(
                  MakePoint(new.xschob, new.yschob, {epsg}),
                  schob.geop
                ), 
                coalesce(
                  MakePoint(new.xschun, new.yschun, {epsg}),
                  schun.geop
                )
              )
            FROM
              schaechte AS schob,
              schaechte AS schun
            WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
          END;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Schaechte" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    # sql = """-- Haltungsgeoobjekt anlegen beim Einfügen neuer Datensätze aus Schachtobjekten
    #     CREATE TRIGGER IF NOT EXISTS create_missing_geoobject_haltungen
    #         AFTER INSERT ON haltungen FOR EACH ROW
    #     WHEN
    #         new.geom IS NULL
    #     BEGIN
    #         UPDATE haltungen SET geom =
    #         (   SELECT MakeLine(schob.geop, schun.geop)
    #             FROM schaechte AS schob,
    #                  schaechte AS schun
    #             WHERE schob.schnam = new.schoben AND
    #                   schun.schnam = new.schunten)
    #         WHERE haltungen.pk = new.pk;
    #     END;"""
    # try:
    #     cursl.execute(sql)
    # except BaseException as err:
    #     fehlermeldung(
    #         "qkan_database.createdbtables: {}".format(err),
    #         'In der Tabelle "Haltungen" konnte ein Trigger nicht angelegt werden.',
    #     )
    #     consl.close()
    #     return False

    consl.commit()

    # Haltungen_untersucht ----------------------------------------------------------------

    sql = """CREATE TABLE haltungen_untersucht (
        pk INTEGER PRIMARY KEY,
        haltnam TEXT,
        schoben TEXT,
        schunten TEXT,
        hoehe REAL,
        breite REAL,
        laenge REAL,
        kommentar TEXT,
        createdat TEXT DEFAULT (datetime('now')),
        untersuchtag TEXT, 
        untersucher TEXT, 
        wetter INTEGER DEFAULT 0, 
        bewertungsart INTEGER DEFAULT 0, 
        bewertungstag TEXT,
        xschob REAL,
        yschob REAL,
        xschun REAL,
        yschun REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Haltungen" konnte nicht erstellt werden',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('haltungen_untersucht','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('haltungen_untersucht','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Haltungen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS haltungen_untersucht_data AS
              SELECT 
                haltnam, schoben, schunten, 
                hoehe, breite, laenge,
                kommentar, createdat, untersuchtag, untersucher, wetter, bewertungsart, bewertungstag,
                xschob, yschob, xschun, yschun
              FROM haltungen_untersucht;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "haltung_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS haltungen_untersucht_insert_clipboard
                INSTEAD OF INSERT ON haltungen_untersucht_data FOR EACH ROW
              BEGIN
                INSERT INTO haltungen_untersucht
                  (haltnam, schoben, schunten,
                   hoehe, breite, laenge,
                   kommentar, createdat,  
                   geom, untersuchtag, untersucher, wetter, bewertungsart, bewertungstag)
                SELECT 
                  new.haltnam, new.schoben, new.schunten, 
                  CASE WHEN new.hoehe > 20 THEN new.hoehe/1000 ELSE new.hoehe END, 
                  CASE WHEN new.breite > 20 THEN new.breite/1000 ELSE new.breite END,
                  new.laenge, new.kommentar, 
                  coalesce(new.createdat, datetime('now')), 
                  MakeLine(
                    coalesce(
                      MakePoint(new.xschob, new.yschob, {epsg}),
                      schob.geop
                    ), 
                    coalesce(
                      MakePoint(new.xschun, new.yschun, {epsg}),
                      schun.geop
                    )
                  ), new.untersuchtag, new.untersucher, new.wetter, new.bewertungsart, new.bewertungstag
                FROM
                  schaechte AS schob,
                  schaechte AS schun
                WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
              END;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "haltung_unterucht_data" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    # untersuchungsdaten Haltung

    sql = """CREATE TABLE Untersuchdat_haltung (
            pk INTEGER PRIMARY KEY,
            untersuchhal TEXT,
            untersuchrichtung TEXT,
            schoben TEXT, 
            schunten TEXT,
            id INTEGER,
            videozaehler INTEGER,
            inspektionslaenge REAL,
            station REAL,
            timecode INTEGER,
            kuerzel TEXT,
            charakt1 TEXT,
            charakt2 TEXT,
            quantnr1 REAL, 
            quantnr2 REAL, 
            streckenschaden TEXT,
            pos_von INTEGER, 
            pos_bis INTEGER,
            foto_dateiname TEXT,
            film_dateiname TEXT,
            richtung TEXT
        )"""

    try:
            cursl.execute(sql)
    except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "Untersuchdat_Haltungen" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    sql = "SELECT AddGeometryColumn('Untersuchdat_haltung','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('Untersuchdat_haltung','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'In der Tabelle "Haltungen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS untersuchdat_haltung_data AS 
                  SELECT
                    untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler, inspektionslaenge, station, timecode, kuerzel, 
                        charakt1, charakt2, quantnr1, quantnr2, streckenschaden, pos_von, pos_bis, foto_dateiname, film_dateiname, richtung
                  FROM Untersuchdat_haltung;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'View "haltung_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS Untersuchdat_haltung_insert_clipboard
                    INSTEAD OF INSERT ON untersuchdat_haltung_data FOR EACH ROW
                  BEGIN
                    INSERT INTO untersuchdat_haltung
                      (untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler, inspektionslaenge, station, timecode, kuerzel, 
                        charakt1, charakt2, quantnr1, quantnr2, streckenschaden, pos_von, pos_bis, foto_dateiname, film_dateiname, richtung, geom)
                    SELECT
                      new.untersuchhal, new.untersuchrichtung, new.schoben,new.schunten, 
                        new.id, new.videozaehler, new.inspektionslaenge , new.station, new.timecode, new.kuerzel, 
                        new.charakt1, new.charakt2, new.quantnr1, new.quantnr2, new.streckenschaden, new.pos_von, new.pos_bis, new.foto_dateiname, new.film_dateiname, new.richtung,
                        CASE
                        WHEN new.inspektionslaenge > haltung.laenge
                        THEN
                        CASE
                        WHEN new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten
                        THEN

                        CASE
                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))+2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))*new.inspektionslaenge/haltung.laenge/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))-2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))-2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR 
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))+2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        ELSE NULL
                        END
                        WHEN new.schoben = haltung.schoben AND new.schunten = haltung.schunten
                        THEN

                        CASE

                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))-2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))+2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))+2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR 
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*haltung.laenge/new.inspektionslaenge*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))-2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        ELSE NULL
                        END
                        END

                        WHEN new.inspektionslaenge < haltung.laenge
                        THEN
                        CASE
                        WHEN new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten
                        THEN

                        CASE

                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))+2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))-2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))-2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR 
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))+2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        ELSE NULL
                        END
                        WHEN new.schoben = haltung.schoben AND new.schunten = haltung.schunten
                        THEN

                        CASE

                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))-2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "in Fließrichtung" AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schob.geop)+(new.station*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))+2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(((-1)*(-1))+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))+2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))+2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        WHEN (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR 
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = "fließrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung") OR
                                (new.untersuchrichtung = "gegen Fließrichtung" AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = "untersuchungsrichtung")
                        THEN 
                        MakeLine(
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {epsg}),
                                schob.geop
                            ), 
                            coalesce(
                            MakePoint((ST_X(schun.geop)+(new.station*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))-2*((-1)/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))-2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(((-1)*(-1))+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {epsg}),
                                schun.geop
                            )
                        )
                        ELSE NULL
                        END
                        END
                        END 
                    FROM
                    schaechte AS schob,
                    schaechte AS schun,
                    haltungen AS haltung
                    WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten AND haltung.haltnam = new.untersuchhal;
                  END"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'In der Tabelle "untersuchhal" konnte ein Trigger nicht angelegt werden.',
            )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS untersuchdat_haltung_data AS 
                      SELECT
                        untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler, station, timecode, kuerzel, 
                        charakt1, charakt2, quantnr1, quantnr2, streckenschaden, pos_von, pos_bis, foto_dateiname, film_dateiname
                      FROM untersuchdat_haltung;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'View "untersuchdat_haltung_data" konnte nicht erstellt werden.',
            )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS untersuchdat_haltung_insert_clipboard
                        INSTEAD OF INSERT ON untersuchdat_haltung_data FOR EACH ROW
                      BEGIN
                        INSERT INTO untersuchdat_haltung
                          (untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler, inspektionslaenge, station, timecode, kuerzel, 
                        charakt1, charakt2, quantnr1, quantnr2, streckenschaden, pos_von, pos_bis, foto_dateiname, film_dateiname, richtung)
                        VALUES (
                          new.untersuchhal, new.untersuchrichtung, new.schoben, new.schunten, new.id, new.videozaehler, new.inspektionslaenge, new.station, new.timecode, new.kuerzel, 
                        new.charakt1, new.charakt2, new.quantnr1, new.quantnr2, new.streckenschaden, new.pos_von, new.pos_bis, new.foto_dateiname, new.film_dateiname, new.richtung
                        );
                      END"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'In der Tabelle "Haltung" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    # Schaechte ----------------------------------------------------------------
    # [knotentyp]: Typ der Verknüpfung (kommt aus Kanal++)

    sql = """CREATE TABLE schaechte (
    pk INTEGER PRIMARY KEY,
    schnam TEXT,
    sohlhoehe REAL,
    deckelhoehe REAL,
    durchm REAL,
    druckdicht INTEGER DEFAULT 0, 
    ueberstauflaeche REAL DEFAULT 0,
    entwart TEXT DEFAULT 'Regenwasser',
    strasse TEXT,
    teilgebiet TEXT,
    knotentyp TEXT,
    auslasstyp TEXT,
    schachttyp TEXT DEFAULT 'Schacht', 
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')),
    xsch REAL, 
    ysch REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Schaechte" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = """SELECT AddGeometryColumn('schaechte','geop',{},'POINT',2);""".format(epsg)
    sql2 = (
        """SELECT AddGeometryColumn('schaechte','geom',{},'MULTIPOLYGON',2);""".format(
            epsg
        )
    )
    sqlindex1 = """SELECT CreateSpatialIndex('schaechte','geom')"""
    sqlindex2 = """SELECT CreateSpatialIndex('schaechte','geop')"""
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sqlindex1)
        cursl.execute(sqlindex2)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Schaechte" konnten die Attribute "geop" und "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS schaechte_data AS 
          SELECT
            schnam, 
            xsch, ysch, 
            sohlhoehe, 
            deckelhoehe, durchm, 
            druckdicht, ueberstauflaeche, 
            entwart, strasse, teilgebiet, 
            knotentyp, auslasstyp, schachttyp, 
            simstatus, 
            kommentar, createdat
          FROM schaechte;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "schaechte_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS schaechte_insert_clipboard
            INSTEAD OF INSERT ON schaechte_data FOR EACH ROW
          BEGIN
            INSERT INTO schaechte
              (schnam, sohlhoehe, 
               deckelhoehe, durchm, 
               druckdicht, ueberstauflaeche, 
               entwart, strasse, teilgebiet, 
               knotentyp, auslasstyp, schachttyp, 
               simstatus, 
               kommentar, createdat, 
               geop, geom)
            VALUES (
              new.schnam, new.sohlhoehe,
              new.deckelhoehe, 
              CASE WHEN new.durchm > 200 THEN new.durchm/1000 ELSE new.durchm END, 
              coalesce(new.druckdicht, 0), coalesce(new.ueberstauflaeche, 0), 
              coalesce(new.entwart, 'Regenwasser'), new.strasse, new.teilgebiet, 
              new.knotentyp, new.auslasstyp, coalesce(new.schachttyp, 'Schacht'), 
              coalesce(new.simstatus, 'vorhanden'),
              new.kommentar, coalesce(new.createdat, datetime('now')),
              MakePoint(new.xsch, new.ysch, {epsg}),
              CastToMultiPolygon(
                MakePolygon(
                  MakeCircle(
                    new.xsch,
                    new.ysch,
                    coalesce(new.durchm/2, 0.5), {epsg}
                  )
                )
              )
            );
          END"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Schaechte" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Schaechte_untersucht ----------------------------------------------------------------
    # [knotentyp]: Typ der Verknüpfung (kommt aus Kanal++)

    sql = """CREATE TABLE schaechte_untersucht (
            pk INTEGER PRIMARY KEY,
            schnam TEXT, 
            durchm REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT (datetime('now')),
            untersuchtag TEXT, 
            untersucher TEXT, 
            wetter INTEGER DEFAULT 0, 
            bewertungsart INTEGER DEFAULT 0, 
            bewertungstag TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "schaechte_untersucht" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = """SELECT AddGeometryColumn('schaechte_untersucht','geop',{},'POINT',2);""".format(epsg)

    sqlindex2 = """SELECT CreateSpatialIndex('schaechte_untersucht','geop')"""
    try:
        cursl.execute(sql1)
        cursl.execute(sqlindex2)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "schaechte_untersucht" konnten die Attribute "geop" und "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS schaechte_untersucht_data AS 
                  SELECT
                    schnam, durchm, 
                    kommentar, createdat, untersuchtag, untersucher, wetter, bewertungsart, bewertungstag
                  FROM schaechte_untersucht;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "schaechte_untersucht_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS schaechte_untersucht_insert_clipboard
                    INSTEAD OF INSERT ON schaechte_untersucht_data FOR EACH ROW
                  BEGIN
                    INSERT INTO schaechte_untersucht
                      (schnam, durchm,  
                       kommentar, createdat, 
                       geop, untersuchtag, untersucher, wetter, bewertungsart, bewertungstag)
                    SELECT
                      new.schnam, 
                      CASE WHEN new.durchm > 200 THEN new.durchm/1000 ELSE new.durchm END, 
                      new.kommentar, coalesce(new.createdat, datetime('now')),
                      sch.geop,
                      new.untersuchtag, new.untersucher, new.wetter, new.bewertungsart, new.bewertungstag
                    FROM
                        schaechte AS sch
                        WHERE sch.schnam = new.schnam;
                  END"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "schaechte_untersucht" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    sql = f"""CREATE VIEW IF NOT EXISTS schaechte_untersucht_data AS 
                      SELECT
                        schnam, durchm, 
                        kommentar, createdat, untersuchtag, untersucher, wetter, bewertungsart, bewertungstag
                      FROM schaechte_untersucht;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "schaechte_untersucht_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS schaechte_untersucht_insert_clipboard
                        INSTEAD OF INSERT ON schaechte_untersucht_data FOR EACH ROW
                      BEGIN
                        INSERT INTO schaechte_untersucht
                          (schnam, durchm,  
                           kommentar, createdat, 
                           geop, untersuchtag, untersucher, wetter, bewertungsart, bewertungstag)
                        SELECT
                          new.schnam,
                          CASE WHEN new.durchm > 200 THEN new.durchm/1000 ELSE new.durchm END, 
                          new.kommentar, coalesce(new.createdat, datetime('now')),
                          sch.geop,
                          new.untersuchtag, new.untersucher, new.wetter, new.bewertungsart, new.bewertungstag
                        FROM
                        schaechte AS sch
                        WHERE sch.schnam = new.schnam;
                      END"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "schaechte_untersucht" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # untersuchungsdaten Schaechte

    sql = """CREATE TABLE Untersuchdat_schacht (
        pk INTEGER PRIMARY KEY,
        untersuchsch TEXT,
        id INTEGER,
        videozaehler INTEGER,
        timecode INTEGER,
        kuerzel TEXT,
        charakt1 TEXT,
        charakt2 TEXT,
        quantnr1 REAL,
        quantnr2 REAL,
        streckenschaden TEXT,
        pos_von INTEGER,
        pos_bis INTEGER,
        bereich TEXT,
        foto_dateiname TEXT
        )"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Untersuchdat_Schächte" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = """SELECT AddGeometryColumn('Untersuchdat_schacht','geop',{},'POINT',2);""".format(epsg)

    sqlindex2 = """SELECT CreateSpatialIndex('Untersuchdat_schacht','geop')"""
    try:
        cursl.execute(sql1)

        cursl.execute(sqlindex2)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Untersuchdat_Schächte" konnten die Attribute "geop" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    sql = f"""CREATE VIEW IF NOT EXISTS untersuchdat_schacht_data AS 
              SELECT
                untersuchsch, id, videozaehler, timecode, kuerzel, 
                    charakt1, charakt2, quantnr1, quantnr2, streckenschaden, pos_von, pos_bis, bereich, foto_dateiname 
              FROM Untersuchdat_schacht;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "schaechte_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS Untersuchdat_schacht_insert_clipboard
                INSTEAD OF INSERT ON untersuchdat_schacht_data FOR EACH ROW
              BEGIN
                INSERT INTO Untersuchdat_schacht
                  (untersuchsch, id, videozaehler, timecode, kuerzel, 
                    charakt1, charakt2, quantnr1, quantnr2, streckenschaden, pos_von, pos_bis, bereich, foto_dateiname, geop)
                SELECT 
                  new.untersuchsch, new.id, new.videozaehler, new.timecode, new.kuerzel, 
                    new.charakt1, new.charakt2, new.quantnr1, new.quantnr2, new.streckenschaden, new.pos_von, new.pos_bis, 
                    new.bereich, new.foto_dateiname, sch.geop
                FROM
                    schaechte AS sch
                    WHERE sch.schnam = new.untersuchsch;
              END"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "untersuchsch" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    # consl.commit()

    sql = f"""CREATE VIEW IF NOT EXISTS untersuchdat_schacht_data AS 
                  SELECT
                    untersuchsch, id, videozaehler, timecode, kuerzel, 
                    charakt1, charakt2, streckenschaden, pos_von, pos_bis, bereich, foto_dateiname
                  FROM untersuchdat_schacht;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "untersuchdat_schacht_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS untersuchdat_schacht_insert_clipboard
                    INSTEAD OF INSERT ON untersuchdat_schacht_data FOR EACH ROW
                  BEGIN
                    INSERT INTO untersuchdat_schacht
                      (untersuchsch, id, videozaehler, timecode, kuerzel, 
                    charakt1, charakt2, quantnr1, quantnr2, streckenschaden, pos_von, pos_bis, bereich, foto_dateiname)
                    VALUES (
                      new.untersuchsch, new.id, new.videozaehler, new.timecode, new.kuerzel, 
                    new.charakt1, new.charakt2, new.quantnr1, new.quantnr2, new.streckenschaden, new.pos_von, new.pos_bis, 
                    new.bereich, new.foto_dateiname
                    );
                  END"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Schaechte" konnte ein Trigger nicht angelegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Profile ------------------------------------------------------------------

    sql = """CREATE TABLE profile (
    pk INTEGER PRIMARY KEY,
    profilnam TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_key TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Profile" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'Kreis', 1, 1, NULL",
            "'Rechteck (geschlossen)', 2, 3, NULL",
            "'Ei (B:H = 2:3)', 3, 5, NULL",
            "'Maul (B:H = 2:1,66)', 4, 4, NULL",
            "'Halbschale (offen) (B:H = 2:1)', 5, NULL, NULL",
            "'Kreis gestreckt (B:H=2:2.5)', 6, NULL, NULL",
            "'Kreis überhöht (B:H=2:3)', 7, NULL, NULL",
            "'Ei überhöht (B:H=2:3.5)', 8, NULL, NULL",
            "'Ei breit (B:H=2:2.5)', 9, NULL, NULL",
            "'Ei gedrückt (B:H=2:2)', 10, NULL, NULL",
            "'Drachen (B:H=2:2)', 11, NULL, NULL",
            "'Maul (DIN) (B:H=2:1.5)', 12, NULL, NULL",
            "'Maul überhöht (B:H=2:2)', 13, NULL, NULL",
            "'Maul gedrückt (B:H=2:1.25)', 14, NULL, NULL",
            "'Maul gestreckt (B:H=2:1.75)', 15, NULL, NULL",
            "'Maul gestaucht (B:H=2:1)', 16, NULL, NULL",
            "'Haube (B:H=2:2.5)', 17, NULL, NULL",
            "'Parabel (B:H=2:2)', 18, NULL, NULL",
            "'Rechteck mit geneigter Sohle (B:H=2:1)', 19, NULL, NULL",
            "'Rechteck mit geneigter Sohle (B:H=1:1)', 20, NULL, NULL",
            "'Rechteck mit geneigter Sohle (B:H=1:2)', 21, NULL, NULL",
            "'Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.2B)', 22, NULL, NULL",
            "'Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.2B)', 23, NULL, NULL",
            "'Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.2B)', 24, NULL, NULL",
            "'Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.4B)', 25, NULL, NULL",
            "'Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.4B)', 26, NULL, NULL",
            "'Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.4B)', 27, NULL, NULL",
            "'Druckrohrleitung', 50, NULL, NULL",
            "'Sonderprofil', 68, 2, NULL",
            "'Gerinne', 69, NULL, NULL",
            "'Trapez (offen)', 900, NULL, NULL",
            "'Doppeltrapez (offen)', 901, NULL, NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO profile (profilnam, he_nr, mu_nr, kp_key) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "Profile" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Geometrie Sonderprofile --------------------------------------------------

    sql = """CREATE TABLE profildaten (
    pk INTEGER PRIMARY KEY, 
    profilnam TEXT, 
    wspiegel REAL, 
    wbreite REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "profildaten" konnte nicht erstellt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Entwaesserungssysteme ----------------------------------------------------

    sql = """CREATE TABLE entwaesserungsarten (
    pk INTEGER PRIMARY KEY, 
    kuerzel TEXT, 
    bezeichnung TEXT, 
    bemerkung TEXT, 
    he_nr INTEGER, 
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "entwaesserungsarten" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'MW', 'Mischwasser', NULL, 0, 0",
            "'RW', 'Regenwasser', NULL, 1, 2",
            "'SW', 'Schmutzwasser', NULL, 2, 1",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO entwaesserungsarten (kuerzel, bezeichnung, bemerkung, he_nr, kp_nr) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "entwaesserungsarten" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Untersuchungsrichtung ----------------------------------------------------

    sql = """CREATE TABLE untersuchrichtung (
        pk INTEGER PRIMARY KEY, 
        kuerzel TEXT, 
        bezeichnung TEXT, 
        bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "untersuchrichtung" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'O', 'in Fließrichtung', NULL",
            "'U', 'gegen Fließrichtung', NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO untersuchrichtung (kuerzel, bezeichnung, bemerkung) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "untersuchrichtung" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # wetter ----------------------------------------------------

    sql = """CREATE TABLE wetter (
            pk INTEGER PRIMARY KEY, 
            kuerzel INTEGER, 
            bezeichnung TEXT, 
            bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "wetter" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "0, 'keine Angabe', NULL",
            "1, 'kein Niederschlag', NULL",
            "2, 'Regen', NULL",
            "3, 'Schnee- oder Eisschmelzwasser', NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO wetter (kuerzel, bezeichnung, bemerkung) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "wetter" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # bewertungsart ----------------------------------------------------

    sql = """CREATE TABLE bewertungsart (
            pk INTEGER PRIMARY KEY, 
            kuerzel INTEGER, 
            bezeichnung TEXT, 
            bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "bewertungsart" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "0, 'keine Angabe', NULL",
            "1, 'ISYBAU 2006/DIN-EN 13508-2:2011', NULL",
            "2, 'ISYBAU 2001', NULL",
            "3, 'ISYBAU 1996', NULL",
            "4, 'Anderes Verfahren', NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO bewertungsart (kuerzel, bezeichnung, bemerkung) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "bewertungsart" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # druckdicht ----------------------------------------------------

    sql = """CREATE TABLE druckdicht (
                pk INTEGER PRIMARY KEY, 
                kuerzel INTEGER, 
                bezeichnung TEXT, 
                bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "druckdicht" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "0, 'keine Angabe', NULL",
            "1, 'vorhanden', NULL",
            "2, 'nicht vorhanden', NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO druckdicht (kuerzel, bezeichnung, bemerkung) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "druckdicht" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Pumpentypen --------------------------------------------------------------

    sql = """CREATE TABLE pumpentypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT, 
    he_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "pumpentypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'Offline', 1",
            "'Online Schaltstufen', 2",
            "'Online Kennlinie', 3",
            "'Online Wasserstandsdifferenz', 4",
            "'Ideal', 5",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO pumpentypen (bezeichnung, he_nr) VALUES ({})".format(ds)
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "pumpentypen" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Pumpen -------------------------------------------------------------------

    sql = """CREATE TABLE pumpen (
    pk INTEGER PRIMARY KEY,
    pnam TEXT,
    schoben TEXT,
    schunten TEXT,
    pumpentyp TEXT,
    volanf REAL,
    volges REAL,
    sohle REAL,
    steuersch TEXT,
    einschalthoehe REAL,
    ausschalthoehe REAL,
    teilgebiet TEXT,
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "pumpen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('pumpen','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('pumpen','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "pumpen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS pumpen_data AS
          SELECT 
            pnam, schoben, schunten, 
            pumpentyp, volanf, volges, 
            sohle, steuersch, 
            einschalthoehe, ausschalthoehe,
            teilgebiet, simstatus, 
            kommentar, createdat
          FROM pumpen;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "pumpen_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS pumpen_insert_clipboard
            INSTEAD OF INSERT ON pumpen_data FOR EACH ROW
          BEGIN
            INSERT INTO pumpen
              (pnam, schoben, schunten, 
               pumpentyp, volanf, volges, 
               sohle, steuersch, 
               einschalthoehe, ausschalthoehe,
               teilgebiet, simstatus, 
               kommentar, createdat, 
               geom)
            SELECT 
              new.pnam, new.schoben, new.schunten, 
              new.pumpentyp, new.volanf, new.volges, 
              new.sohle, new.steuersch, 
              new.einschalthoehe, new.ausschalthoehe,
              new.teilgebiet, coalesce(new.simstatus, 'vorhanden'), 
              new.kommentar, new.createdat,
              MakeLine(schob.geop, schun.geop)
            FROM
              schaechte AS schob,
              schaechte AS schun
            WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
          END;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "pumpen_insert_clipboard" konnte nicht erstellt werden',
        )
        consl.close()
        return False

    consl.commit()

    # Wehre --------------------------------------------------------------------

    sql = """CREATE TABLE wehre (
    pk INTEGER PRIMARY KEY,
    wnam TEXT,
    schoben TEXT,
    schunten TEXT,
    wehrtyp TEXT,
    schwellenhoehe REAL,
    kammerhoehe REAL,
    laenge REAL,
    uebeiwert REAL,
    aussentyp TEXT,
    aussenwsp REAL,
    teilgebiet TEXT,
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "wehre" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('wehre','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('wehre','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "wehre" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE VIEW IF NOT EXISTS wehre_data AS
          SELECT 
            wnam, schoben, schunten, 
            wehrtyp, schwellenhoehe, kammerhoehe, 
            laenge, uebeiwert, aussentyp, aussenwsp, 
            teilgebiet, simstatus, 
            kommentar, createdat
          FROM wehre;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "wehre_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = f"""CREATE TRIGGER IF NOT EXISTS wehre_insert_clipboard
            INSTEAD OF INSERT ON wehre_data FOR EACH ROW
          BEGIN
            INSERT INTO wehre
              (wnam, schoben, schunten, 
               wehrtyp, schwellenhoehe, kammerhoehe, 
               laenge, uebeiwert, aussentyp, aussenwsp, 
               teilgebiet, simstatus, 
               kommentar, createdat, 
               geom)
            SELECT 
              new.wnam, new.schoben, new.schunten, 
              new.wehrtyp, new.schwellenhoehe, new.kammerhoehe, 
              new.laenge, new.uebeiwert, new.aussentyp, new.aussenwsp, 
              new.teilgebiet, coalesce(new.simstatus, 'vorhanden'), 
              new.kommentar, new.createdat,
              MakeLine(schob.geop, schun.geop)
            FROM
              schaechte AS schob,
              schaechte AS schun
            WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
          END;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "wehre_insert_clipboard" konnte nicht erstellt werden',
        )
        consl.close()
        return False

    consl.commit()

    # Einzugsgebiete ------------------------------------------------------------------
    # Entsprechen in HYSTEM-EXTRAN 7.x den Siedlungstypen
    # "flaeche" wird nur für den Import benötigt, wenn keine Flächenobjekte vorhanden sind
    # Verwendung:
    # Spezifische Verbrauchsdaten in Verbindung mit "einwohner"
    # Einheiten:
    #  - ewdichte: EW/ha
    #  - wverbrauch: l/(EW·d)
    #  - stdmittel: h/d
    #  - fremdwas: %
    #  - flaeche: ha

    sql = """CREATE TABLE einzugsgebiete (
    pk INTEGER PRIMARY KEY,
    tgnam TEXT,
    ewdichte REAL,
    wverbrauch REAL,
    stdmittel REAL,
    fremdwas REAL,
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Einzugsgebiete" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = (
        "SELECT AddGeometryColumn('einzugsgebiete','geom',{},'MULTIPOLYGON',2)".format(
            epsg
        )
    )
    sqlindex = "SELECT CreateSpatialIndex('einzugsgebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Einzugsgebiete" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Teilgebiete ------------------------------------------------------------------
    #  Verwendung:
    # Auswahl von Objekten in verschiedenen Tabellen für verschiedene Aufgaben (z. B.
    # automatische Verknüpfung von befestigten Flächen und direkten Einleitungen).

    sql = """CREATE TABLE teilgebiete (
    pk INTEGER PRIMARY KEY,
    tgnam TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Teilgebiete" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('teilgebiete','geom',{},'MULTIPOLYGON',2)".format(
        epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('teilgebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Teilgebiete" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Gruppen ------------------------------------------------------------------
    # Bearbeitungen, die auf Auswahlen basieren, verwenden ausschließlich die
    # Tabelle "Teilgebiete". Diese Zuordnung ist sozusagen aktiv, im Gegensatz
    # zu inaktiven Zuordnungen, die in der Tabelle "gruppen" gespeichert werden.
    # Mit einem plugin "Zuordnung zu Teilgebieten" können gespeicherte
    # Zuordnungen gespeichert und geladen werden. Dabei werden die
    # Zuordnungen für folgende Tabellen verwaltet:
    #  - "haltungen"
    #  - "schaechte"
    #  - "flaechen"
    #  - "linkfl"
    #  - "linksw"
    #  - "tezg"
    #  - "einleit"
    #  - "swgebaeude"

    sql = """CREATE TABLE gruppen (
    pk INTEGER PRIMARY KEY,
    pktab INTEGER,
    grnam TEXT,
    teilgebiet TEXT,
    tabelle TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "gruppen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Befestigte und unbefestigte Flächen ------------------------------------------------------

    sql = """CREATE TABLE flaechen (
    pk INTEGER PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,
    schnam TEXT,
    neigkl INTEGER DEFAULT 1,
    neigung REAL,               -- absolute Neigung (%)
    teilgebiet TEXT,
    regenschreiber TEXT,
    abflussparameter TEXT,
    aufteilen TEXT DEFAULT 'nein',
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "flaechen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = """SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2)""".format(
        epsg
    )
    sqlindex = """SELECT CreateSpatialIndex('flaechen','geom')"""
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "flaechen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Anbindung Flächen
    # Die Tabelle linkfl verwaltet die Anbindung von Flächen an Haltungen. Diese Anbindung
    # wird ausschließlich grafisch verwaltet und beim Export direkt verwendet.
    # Flächen, bei denen das Attribut "aufteilen" den Wert 'ja' hat, werden mit dem
    # Werkzeug "QKan_Link_Flaechen" mit allen durch die Verschneidung mit tezg entstehenden
    # Anteilen zugeordnet.

    sql = """CREATE TABLE linkfl (
    pk INTEGER PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,
    schnam TEXT,
    tezgnam TEXT,
    teilgebiet TEXT,
    abflusstyp TEXT,
    speicherzahl INTEGER,
    speicherkonst REAL,
    fliesszeitkanal REAL,
    fliesszeitflaeche REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "linkfl" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = (
        """SELECT AddGeometryColumn('linkfl','geom',{epsg},'MULTIPOLYGON',2)""".format(
            epsg=epsg
        )
    )
    sql2 = (
        """SELECT AddGeometryColumn('linkfl','gbuf',{epsg},'MULTIPOLYGON',2)""".format(
            epsg=epsg
        )
    )
    sql3 = (
        """SELECT AddGeometryColumn('linkfl','glink',{epsg},'LINESTRING',2)""".format(
            epsg=epsg
        )
    )
    sqlindex = "SELECT CreateSpatialIndex('linkfl','glink')"
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sql3)
        cursl.execute(sqlindex)
    except Exception as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            "QKan_Database (1) SQL-Fehler in SpatiaLite:",
        )
        consl.close()
        return False
    consl.commit()

    # Anbindung Direkteinleitungen --------------------------------------------------------------
    # Die Tabelle linksw verwaltet die Anbindung von Gebäuden an Haltungen. Diese Anbindung
    # wird anschließend in das Feld haltnam eingetragen. Der Export erfolgt allerdings anhand
    # der grafischen Verknüpfungen dieser Tabelle.

    sql = """CREATE TABLE linksw (
    pk INTEGER PRIMARY KEY,
    elnam TEXT,
    haltnam TEXT,
    schnam TEXT,
    teilgebiet TEXT)"""

    try:
        cursl.execute(sql)
    except:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(traceback.format_exc()),
            'Tabelle "linksw" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = """SELECT AddGeometryColumn('linksw','geom',{epsg},'POLYGON',2)""".format(
        epsg=epsg
    )
    sql2 = (
        """SELECT AddGeometryColumn('linksw','gbuf',{epsg},'MULTIPOLYGON',2)""".format(
            epsg=epsg
        )
    )
    sql3 = (
        """SELECT AddGeometryColumn('linksw','glink',{epsg},'LINESTRING',2)""".format(
            epsg=epsg
        )
    )
    sqlindex = "SELECT CreateSpatialIndex('linksw','geom')"
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sql3)
        cursl.execute(sqlindex)
    except:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(traceback.format_exc()),
            "QKan_Database (2) SQL-Fehler in SpatiaLite: \n",
        )
        consl.close()
        return False
    consl.commit()

    # Teileinzugsgebiete ------------------------------------------------------------------

    sql = """-- Haltungsflächen. Verschneidung, Verwaltung der Befestigungsgrade (alte Programme)
    CREATE TABLE tezg (
    pk INTEGER PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,
    schnam TEXT,
    neigkl INTEGER DEFAULT 1,   -- Werte [1-5], als Vorgabe fuer automatisch erzeugte unbef Flaechen
    neigung REAL,               -- absolute Neigung (%)
    befgrad REAL,               -- (-) Befestigungsgrad absolut, nur optional fuer SWMM und HE6
    schwerpunktlaufzeit REAL,   -- Schwerpunktlaufzeit (s)
    regenschreiber TEXT,        -- Regenschreiber beziehen sich auf Zieldaten
    teilgebiet TEXT,
    abflussparameter TEXT,      -- als Vorgabe fuer automatisch erzeugte unbef Flaechen
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "tezg" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('tezg','geom',{},'MULTIPOLYGON',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('tezg','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "tezg" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Direkte Einleitungen ----------------------------------------------------------
    # Erfasst alle Direkteinleitungen mit festem SW-Zufluss (m³/a)
    # Die Zuordnung zum Teilgebiet dient nur der Auswahl

    sql = """CREATE TABLE einleit (
    pk INTEGER PRIMARY KEY,
    elnam TEXT,
    haltnam TEXT,
    schnam TEXT,
    teilgebiet TEXT, 
    zufluss REAL,
    ew REAL,
    einzugsgebiet TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "einleit" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('einleit','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "einleit" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Einleitungen aus Aussengebieten ----------------------------------------------------------------
    # Erfasst alle Außengebiete
    # Die Zuordnung zum Teilgebiet dient nur der Auswahl

    sql = """CREATE TABLE aussengebiete (
        pk INTEGER PRIMARY KEY, 
        gebnam TEXT, 
        schnam TEXT, 
        hoeheob REAL, 
        hoeheun REAL, 
        fliessweg REAL, 
        basisabfluss REAL, 
        cn REAL, 
        regenschreiber TEXT, 
        teilgebiet TEXT, 
        kommentar TEXT, 
        createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            'Tabelle "aussengebiete" konnte nicht erstellt werden: \n{}'.format(
                repr(err)
            )
        )
        consl.close()
        return False

    sql = """SELECT AddGeometryColumn('aussengebiete','geom',{epsg},'MULTIPOLYGON',2)""".format(
        epsg=epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('aussengebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            'In der Tabelle "aussengebiete" konnte das Attribut "geom" nicht hinzugefuegt werden: \n{}'.format(
                repr(err)
            )
        )
        consl.close()
        return False
    consl.commit()

    # Anbindung Aussengebiete -----------------------------------------------------------------------------
    # Die Tabelle linkageb verwaltet die Anbindung von Aussengebieten an Schächte. Diese Anbindung
    # wird anschließend in das Feld schnam eingetragen. Der Export erfolgt allerdings anhand
    # der grafischen Verknüpfungen dieser Tabelle.

    sql = """CREATE TABLE linkageb (
    pk INTEGER PRIMARY KEY,
    gebnam TEXT,
    schnam TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "linkageb" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = (
        """SELECT AddGeometryColumn('linkageb','glink',{epsg},'LINESTRING',2)""".format(
            epsg=epsg
        )
    )
    sqlindex = "SELECT CreateSpatialIndex('linkageb','glink')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(traceback.format_exc()),
            "QKan_Database (2) SQL-Fehler in SpatiaLite: \n",
        )
        consl.close()
        return False
    consl.commit()

    # Simulationsstatus/Planungsstatus -----------------------------------------

    sql = """CREATE TABLE simulationsstatus (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "simulationsstatus" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'keine Angabe', 0, NULL, 5",
            "'vorhanden', 1, 1, 0",
            "'geplant', 2, NULL, 1",
            "'fiktiv', 3, NULL, 2",
            "'außer Betrieb (keine Sim.)', 4, NULL, 3",
            "'verfüllt (keine Sim.)', 5, NULL, NULL",
            "'stillgelegt', NULL, NULL, 4",
            "'rückgebaut', NULL, NULL, 6",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO simulationsstatus (bezeichnung, he_nr, mu_nr, kp_nr) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "simulationsstatus" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Auslasstypen -------------------------------------------------------------

    sql = """CREATE TABLE auslasstypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "auslasstypen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'frei', 0, NULL, NULL",
            "'normal', 1, NULL, NULL",
            "'konstant', 2, NULL, NULL",
            "'Tide', 3, NULL, NULL",
            "'Zeitreihe', 4, NULL, NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO auslasstypen (bezeichnung, he_nr, mu_nr, kp_nr) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "auslasstypen" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Abflussparameter -------------------------------------------------------------

    sql = """CREATE TABLE abflussparameter (
    pk INTEGER PRIMARY KEY, 
    apnam TEXT, 
    anfangsabflussbeiwert REAL, 
    endabflussbeiwert REAL, 
    benetzungsverlust REAL, 
    muldenverlust REAL, 
    benetzung_startwert REAL, 
    mulden_startwert REAL, 
    rauheit_kst REAL,                       -- Rauheit Stricklerbeiwert = 1/n
    pctZero REAL,                           -- SWMM: % Zero-Imperv
    bodenklasse TEXT, 
    flaechentyp TEXT, 
    kommentar TEXT, 
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "abflussparameter" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:
        daten = [
            "'$Default_Bef', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, NULL, NULL",
            "'$Default_Unbef', 'Standart qkhe', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', 'Grünfläche'",
            "'Gebäude', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, NULL, 'Gebäude'",
            "'Straße', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, NULL, 'Straße'",
            "'Grünfläche', 'Standart qkhe', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', 'Grünfläche'",
            "'Gewässer', 'Standart qkhe', 0, 0, 0, 0, 0, 0, NULL, 'Gewässer'",
        ]

        for ds in daten:
            sql = """INSERT INTO abflussparameter
                     ( apnam, kommentar, anfangsabflussbeiwert, endabflussbeiwert, benetzungsverlust, 
                       muldenverlust, benetzung_startwert, mulden_startwert, bodenklasse, flaechentyp) Values ({})""".format(
                ds
            )
            cursl.execute(sql)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "abflussparameter" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Tabelle "flaechentypen" --------------------------------------------------------------------

    sql = """CREATE TABLE IF NOT EXISTS flaechentypen (
        pk INTEGER PRIMARY KEY,
        bezeichnung TEXT,
        he_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "flaechentypen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:
        for bez, num in [
            ["Gebäude", 0],
            ["Straße", 1],
            ["Grünfläche", 2],
            ["Gewässer", 3],
        ]:
            sql = """INSERT INTO flaechentypen
                     (bezeichnung, he_nr) Values ('{bez}', {num})""".format(
                bez=bez, num=num
            )
            cursl.execute(sql)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "abflussparameter" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Bodenklasse -------------------------------------------------------------

    sql = """CREATE TABLE bodenklassen (
    pk INTEGER PRIMARY KEY, 
    bknam TEXT, 
    infiltrationsrateanfang REAL,               -- (mm/min)
    infiltrationsrateende REAL,                 -- (mm/min)
    infiltrationsratestart REAL,                -- (mm/min)
    rueckgangskonstante REAL,                   -- (1/d)
    regenerationskonstante REAL,                -- (1/d)
    saettigungswassergehalt REAL,               -- (mm)
    kommentar TEXT, 
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "bodenklassen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        "'VollDurchlaessig', 10, 9, 10, 144, 1.584, 100, 'Importiert mit qg2he'",
        "'Sand', 2.099, 0.16, 1.256, 227.9, 1.584, 12, 'Importiert mit qg2he'",
        "'SandigerLehm', 1.798, 0.101, 1.06, 143.9, 0.72, 18, 'Importiert mit qg2he'",
        "'LehmLoess', 1.601, 0.081, 0.94, 100.2, 0.432, 23, 'Importiert mit qg2he'",
        "'Ton', 1.9, 0.03, 1.087, 180, 0.144, 16, 'Importiert mit qg2he'",
        "'Undurchlaessig', 0, 0, 0, 100, 1, 0, 'Importiert mit qg2he'",
    ]

    for ds in daten:
        try:
            sql = """INSERT INTO bodenklassen
                     ( 'bknam', 'infiltrationsrateanfang', 'infiltrationsrateende', 'infiltrationsratestart', 
                       'rueckgangskonstante', 'regenerationskonstante', 'saettigungswassergehalt', 
                       'kommentar') Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "bodenklassen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
            )
            consl.close()
            return False
    consl.commit()

    # Abflusstypen -------------------------------------------------------------

    sql = """CREATE TABLE abflusstypen (
    pk INTEGER PRIMARY KEY, 
    abflusstyp TEXT,
    he_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "abflusstypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        "'Speicherkaskade', 0, 0",
        "'Direktabfluss', 0, 0",
        "'Fliesszeiten', 1, 1",
        "'Schwerpunktlaufzeit', 2, 2",
        "'Schwerpunktfließzeit', 2, 2",
    ]

    for ds in daten:
        try:
            sql = """INSERT INTO abflusstypen
                     (abflusstyp, he_nr, kp_nr) Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "abflusstypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
            )
            consl.close()
            return False
    consl.commit()

    # Knotentypen -------------------------------------------------------------

    sql = """CREATE TABLE knotentypen (
    pk INTEGER PRIMARY KEY, 
    knotentyp TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "knotentypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        "'Anfangsschacht'",
        "'Einzelschacht'",
        "'Endschacht'",
        "'Hochpunkt'",
        "'Normalschacht'",
        "'Tiefpunkt'",
        "'Verzweigung'",
        "'Fliesszeiten'",
    ]

    for ds in daten:
        try:
            sql = """INSERT INTO knotentypen
                     ( 'knotentyp') Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "knotentypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
            )
            consl.close()
            return False
    consl.commit()

    # Schachttypen -------------------------------------------------------------

    sql = """CREATE TABLE schachttypen (
    pk INTEGER PRIMARY KEY, 
    schachttyp TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "schachttypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = ["'Auslass'", "'Schacht'", "'Speicher'"]

    for ds in daten:
        try:
            sql = """INSERT INTO schachttypen
                     ( 'schachttyp') Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "schachttypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
            )
            consl.close()
            return False
    consl.commit()

    # Kennlinie Speicherbauwerke -----------------------------------------------

    sql = """CREATE TABLE speicherkennlinien (
    pk INTEGER PRIMARY KEY, 
    schnam TEXT, 
    wspiegel REAL, 
    oberfl REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "Speicherkennlinien".',
        )
        consl.close()
        return False
    consl.commit()

    # Hilfstabelle für den DYNA-Export -----------------------------------------

    sql = """
        CREATE TABLE IF NOT EXISTS dynahal (
            pk INTEGER PRIMARY KEY,
            haltnam TEXT,
            schoben TEXT,
            schunten TEXT,
            teilgebiet TEXT,
            kanalnummer TEXT,
            haltungsnummer TEXT,
            anzobob INTEGER,
            anzobun INTEGER,
            anzunun INTEGER,
            anzunob INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "dynahal".',
        )
        consl.close()
        return False
    consl.commit()

    # Hilfstabelle für den Flächen-Export

    sql = """
        CREATE TABLE IF NOT EXISTS flaechen_he8 (
            pk INTEGER PRIMARY KEY,
            Name TEXT, 
            Haltung TEXT, 
            Groesse REAL, 
            Regenschreiber TEXT, 
            Flaechentyp INTEGER, 
            BerechnungSpeicherkonstante INTEGER, 
            Typ INTEGER, 
            AnzahlSpeicher INTEGER, 
            Speicherkonstante REAL, 
            Schwerpunktlaufzeit REAL, 
            FliesszeitOberflaeche REAL, 
            LaengsteFliesszeitKanal REAL, 
            Parametersatz TEXT, 
            Neigungsklasse INTEGER, 
            ZuordnUnabhEZG INTEGER,
            IstPolygonalflaeche SMALLINT, 
            ZuordnungGesperrt SMALLINT, 
            LastModified TEXT DEFAULT (datetime('now')), 
            Kommentar TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "flaechen_he8".',
        )
        consl.close()
        return False

    sql = """SELECT AddGeometryColumn('flaechen_he8','Geometry', -1,
            'MULTIPOLYGON',2)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen des Attributes "flaechen_he8.Geometry".',
        )
        consl.close()
        return False

    sql = """SELECT CreateSpatialIndex('flaechen_he8', 'Geometry')"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen des Spatial Index für Attribut "Geometry".',
        )
        consl.close()
        return False

    consl.commit()

    # Allgemeine Informationen -----------------------------------------------

    sql = """CREATE TABLE info (
    pk INTEGER PRIMARY KEY, 
    subject TEXT, 
    value TEXT,
    createdat TEXT DEFAULT (datetime('now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Tabelle "Info".',
        )
        consl.close()
        return False

    # Plausibilitätskontrollen --------------------------------------------------

    # Prüfung der Anbindungen in "linkfl" auf eindeutige Zuordnung zu Flächen und Haltungen

    sql = """CREATE VIEW IF NOT EXISTS "v_linkfl_check" AS 
            WITH lfok AS
            (   SELECT 
                    lf.pk AS "pk",
                    lf.flnam AS "linkfl_nam", 
                    lf.haltnam AS "linkfl_haltnam", 
                    fl.flnam AS "flaech_nam",
                    tg.flnam AS "tezg_nam",
                    min(lf.pk) AS pkmin, 
                    max(lf.pk) AS pkmax,
                    count(*) AS anzahl
                FROM linkfl AS lf
                LEFT JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam
                WHERE fl.aufteilen = "ja" and fl.aufteilen IS NOT NULL
                GROUP BY fl.flnam, tg.flnam
                UNION
                SELECT 
                    lf.pk AS "pk",
                    lf.flnam AS "linkfl_nam", 
                    lf.haltnam AS "linkfl_haltnam", 
                    fl.flnam AS "flaech_nam",
                    NULL AS "tezg_nam",
                    min(lf.pk) AS pkmin, 
                    max(lf.pk) AS pkmax,
                    count(*) AS anzahl
                FROM linkfl AS lf
                LEFT JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                WHERE fl.aufteilen <> "ja" OR fl.aufteilen IS NULL
                GROUP BY fl.flnam)
            SELECT pk, anzahl, CASE WHEN anzahl > 1 THEN 'mehrfach vorhanden' WHEN flaech_nam IS NULL THEN 'Keine Fläche' WHEN linkfl_haltnam IS NULL THEN  'Keine Haltung' ELSE 'o.k.' END AS fehler
            FROM lfok"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_linkfl_check".',
        )
        consl.close()
        return False

    # Feststellen der Flächen ohne Anbindung

    sql = """CREATE VIEW IF NOT EXISTS "v_flaechen_ohne_linkfl" AS 
            SELECT 
                fl.pk, 
                fl.flnam AS "flaech_nam",
                fl.aufteilen AS "flaech_aufteilen", 
                'Verbindung fehlt' AS "Fehler"
            FROM flaechen AS fl
            LEFT JOIN linkfl AS lf
            ON lf.flnam = fl.flnam
            LEFT JOIN tezg AS tg
            ON tg.flnam = lf.tezgnam
            WHERE ( (fl.aufteilen <> "ja" or fl.aufteilen IS NULL) AND
                     lf.pk IS NULL) OR
                  (  fl.aufteilen = "ja" AND fl.aufteilen IS NOT NULL AND 
                     lf.pk IS NULL)
            UNION
            VALUES
                (0, '', '', 'o.k.') """

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_flaechen_ohne_linkfl".',
        )
        consl.close()
        return False

    # Vergleich der Flächengröße mit der Summe der verschnittenen Teile

    sql = """CREATE VIEW IF NOT EXISTS "v_flaechen_check" AS 
            WITH flintersect AS (
                SELECT fl.flnam AS finam, 
                       CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                       ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                       END AS flaeche
                FROM linkfl AS lf
                INNER JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam)
            SELECT fa.flnam, 
                   AREA(fa.geom) AS flaeche, 
                   sum(fi.flaeche) AS "summe_flaechen_stuecke", 
                   sum(fi.flaeche) - AREA(fa.geom) AS differenz
            FROM flaechen AS fa
            LEFT JOIN flintersect AS fi
            ON fa.flnam = fi.finam
            GROUP BY fa.flnam
            HAVING ABS(sum(fi.flaeche) - AREA(fa.geom)) > 2"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_flaechen_check".',
        )
        consl.close()
        return False

    # Vergleich der Haltungsflächengrößen mit der Summe der verschnittenen Teile

    sql = """CREATE VIEW IF NOT EXISTS "v_tezg_check" AS 
            WITH flintersect AS (
                SELECT tg.flnam AS finam, 
                       CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                       ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                       END AS flaeche
                FROM linkfl AS lf
                INNER JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam)
            SELECT tg.flnam, 
                   AREA(tg.geom) AS haltungsflaeche, 
                   sum(fi.flaeche) AS summe_flaechen_stuecke, 
                   sum(fi.flaeche) - AREA(tg.geom) AS differenz
            FROM tezg AS tg
            LEFT JOIN flintersect AS fi
            ON tg.flnam = fi.finam
            GROUP BY tg.flnam
            HAVING ABS(sum(fi.flaeche) - AREA(tg.geom)) > 2"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_tezg_check".',
        )
        consl.close()
        return False

    consl.commit()

    # Doppelte Verbindungslinien an Flächen prüfen

    sql = """CREATE VIEW IF NOT EXISTS "v_linkfl_redundant" AS 
            WITH lfm AS (
                SELECT flnam, tezgnam, count(*) AS anz
                FROM linkfl AS lf
                GROUP BY flnam, tezgnam)
            SELECT lf.pk, lf.flnam, lf.tezgnam, lfm.anz
            FROM linkfl AS lf
            LEFT JOIN lfm
            ON lf.flnam = lfm.flnam and lf.tezgnam = lfm.tezgnam
            WHERE anz <> 1 or lf.flnam IS NULL
            ORDER BY lf.flnam"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_linkfl_redundant".',
        )
        consl.close()
        return False

    consl.commit()

    # Doppelte Verbindungslinien an Direkteinleitungen prüfen

    sql = """CREATE VIEW IF NOT EXISTS "v_linksw_redundant" AS 
            WITH lsm AS (
                SELECT elnam, count(*) AS anz
                FROM linksw AS ls
                GROUP BY elnam)
            SELECT ls.pk, ls.elnam, lsm.anz
            FROM linksw AS ls
            LEFT JOIN lsm
            ON ls.elnam = lsm.elnam
            WHERE anz <> 1 or ls.elnam IS NULL
            ORDER BY ls.elnam"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_linksw_redundant".',
        )
        consl.close()
        return False

    consl.commit()

    # Abschluss --------------------------------------------------------------------

    # Aktuelle Version eintragen
    sql = """INSERT INTO info (subject, value) VALUES ('version', '{}'); \n""".format(
        version
    )
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Einfügen der Tabelle "Info".',
        )
        consl.close()
        return False
    consl.commit()

    fortschritt("Tabellen erstellt...", 0.01)

    return True


# ----------------------------------------------------------------------------------------------------------------------
def test() -> None:
    # Verzeichnis der Testdaten
    pfad = "C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/modelldb_itwh"
    database_qkan = os.path.join(pfad, "test1.sqlite")

    if os.path.exists(database_qkan):
        os.remove(database_qkan)

    consl = spatialite_connect(database=database_qkan)
    cursl = consl.cursor()

    progress_message_bar = iface.messageBar().createMessage("Doing something boring...")
    progress = QProgressBar()
    progress.setMaximum(10)
    progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    progress_message_bar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progress_message_bar, iface.messageBar().INFO)
    progress.setValue(2)
    iface.messageBar().clearWidgets()

    iface.mainWindow().statusBar().showMessage(
        "SpatiaLite-Datenbank wird erstellt. Bitte warten... {} %".format(20)
    )
    import time

    time.sleep(1)

    sql = "SELECT InitSpatialMetadata(transaction = TRUE)"
    cursl.execute(sql)

    iface.messageBar().pushMessage(
        "Information", "SpatiaLite-Datenbank ist erstellt!", level=Qgis.Info
    )

    createdbtables(consl, cursl, version="1.0.0")
    consl.close()


if __name__ in ("__main__", "__console__", "__builtin__"):
    test()
