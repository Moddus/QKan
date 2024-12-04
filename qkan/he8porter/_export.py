from typing import List

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import checknames, fehlermeldung, fortschritt, meldung
from qkan.linkflaechen.updatelinks import updatelinkfl
from qkan.utils import get_logger

logger = get_logger("QKan.he8.export")


# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self, db_qkan: DBConnection):

        self.liste_teilgebiete = QKan.config.selections.teilgebiete
        self.db_qkan = db_qkan

        self.append = QKan.config.check_export.append
        self.update = QKan.config.check_export.update

        self.nextid = 0

    def run(self) -> bool:
        """
        Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in
        eine HE_SpatiaLite-Datenbank
        """
        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Export in Arbeit. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

        # --------------------------------------------------------------------------------------------
        # Besonderes Gimmick des ITWH-Programmiers: Die IDs der Tabellen muessen sequentiell
        # vergeben werden!!! Ein Grund ist, dass (u.a.?) die Tabelle "tabelleninhalte" mit verschiedenen
        # Tabellen verknuepft ist und dieser ID eindeutig sein muss.

        self.db_qkan.sqlyml('he8_get_id', 'id der HE-idbm-Datenbank lesen')
        data = self.db_qkan.fetchone()
        if not data:
            logger.error(
                "he8porter._export.run: SELECT NextId, Version FROM he.Itwh$ProgInfo"
                f"\nAbfrageergebnis ist leer: {data}"
            )
        self.nextid = int(data[0]) + 1
        he_db_version = data[1].split(".")
        logger.debug(f"HE IDBF-Version {he_db_version}")

        # Export
        result = all(
            [
                # self._profile(),
                self._bodenklassen(),
                self._abflussparameter(),
                self._schaechte(),              # 30%
                self._auslaesse(),
                self._speicher(),
                self._haltungen(),              # 60%
                self._wehre(),
                self._pumpen(),
                self._drosseln(),
                self._schieber(),
                self._qregler(),
                self._hregler(),
                self._grundseitenauslaesse(),
                self._flaechen(),               # 95%
                # self._einleitdirekt(),
                # self._aussengebiete(),
                # self._einzugsgebiet(),
                self._tezg(),                   # 100%
            ]
        )

        self.progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")

        return result

        # fortschritt("Ende...", 1)
        # self.progress_bar.setValue(100)
        # status_message.setText("Datenexport abgeschlossen.")
        # status_message.setLevel(Qgis.Success)

    def _schaechte(self) -> bool:
        """Export Schächte"""

        if QKan.config.check_export.schaechte:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_schaechte_sel'
                else:
                    sqlnam = 'he8_update_schaechte_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_schaechte (1)"
                ):
                    logger.error_data('Export Update Schächte ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")

            if self.append:
                # Feststellen der Anzahl Schächte in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_schaechte (2)"
                ):
                    logger.error_data('Abfrage Anzahl Schächte in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_schaechte_sel'
                else:
                    sqlnam = 'he8_append_schaechte_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_schaechte (3)",
                    parameters={'id': nr0}
                ):
                    logger.error_data('Einfügen Schächte in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")

                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: Gesamtzahl Schächte nach Einfügen"
                ):
                    logger.error_data('Gesamtzahl Schächte nach Einfügen ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Schächte eingefügt", 0.30)
                self.progress_bar.setValue(30)
        return True

    def _speicher(self) -> bool:
        """Export Speicherbauwerke"""

        if QKan.config.check_export.speicher:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_speicher_sel'
                else:
                    sqlnam = 'he8_update_speicher_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_speicher (1)"
                ):
                    logger.error_data('Export Update Speicher ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")

            if self.append:
                # Feststellen der Anzahl Speicherschächte in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_speicher',
                    "db_qkan: export_to_he8.export_speicherschaechte (1)"
                ):
                    logger.error_data('Abfrage Anzahl Speicher in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_speicher_sel'
                else:
                    sqlnam = 'he8_append_speicher_all'

                if not self.db_qkan.sqlyml(sqlnam, "db_qkan: export_speicher (1)"):
                    return False

                sql = "SELECT count(*) FROM he.Speicherschacht"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_speicherschaechte (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Speicherschächte eingefügt", 0.34)
                self.progress_bar.setValue(34)
        return True

    def _auslaesse(self) -> bool:
        """Export Auslässe"""

        if QKan.config.check_export.auslaesse:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Auslass SET
                    (   Sohlhoehe, Gelaendehoehe, 
                        Scheitelhoehe,
                        Planungsstatus,
                        LastModified, Kommentar, Geometry
                        ) =
                    ( SELECT
                        schaechte.sohlhoehe AS sohlhoehe, 
                        coalesce(schaechte.deckelhoehe, 0.0) AS gelaendehoehe,
                        schaechte.deckelhoehe AS scheitelhoehe,
                        st.he_nr AS planungsstatus, 
                        coalesce(schaechte.createdat, datetime('now')) AS lastmodified, 
                        schaechte.kommentar AS kommentar,
                        SetSrid(schaechte.geop, -1) AS Geometry
                      FROM schaechte
                      LEFT JOIN simulationsstatus AS st
                      ON schaechte.simstatus = st.bezeichnung
                      WHERE schaechte.schnam = he.Auslass.Name and schaechte.schachttyp = 'Auslass'{auswahl})
                    WHERE he.Auslass.Name IN 
                          (SELECT schnam FROM schaechte WHERE schaechte.schachttyp = 'Auslass'{auswahl})
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_auslaesse (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Auslässe in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_auslaesse',
                    "db_qkan: export_to_he8.export_auslaesse (1)"
                ):
                    logger.error_data('Abfrage Anzahl Auslässe in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                    INSERT INTO he.Auslass
                    ( Id, Name, Typ, Sohlhoehe,
                      Gelaendehoehe, Art, AnzahlKanten,
                      Scheitelhoehe, 
                      Planungsstatus,
                      LastModified, Kommentar, Geometry)
                    SELECT
                      {nr0} + row_number() OVER (ORDER BY schaechte.schnam) AS id, 
                      schaechte.schnam AS name, 
                      1 AS typ, 
                      schaechte.sohlhoehe AS sohlhoehe, 
                      coalesce(schaechte.deckelhoehe, 0.0) AS gelaendehoehe,
                      1 AS art, 
                      2 AS anzahlkanten, 
                      schaechte.deckelhoehe AS scheitelhoehe,
                      st.he_nr AS planungsstatus, 
                      coalesce(schaechte.createdat, datetime('now')) AS lastmodified, 
                      schaechte.kommentar AS kommentar,
                      SetSrid(schaechte.geop, -1) AS Geometry
                    FROM schaechte
                    LEFT JOIN simulationsstatus AS st
                    ON schaechte.simstatus = st.bezeichnung
                    WHERE schaechte.schnam NOT IN (SELECT Name FROM he.Auslass) and 
                          schaechte.schachttyp = 'Auslass'{auswahl}
                """

                if not self.db_qkan.sql(sql, "db_qkan: export_auslaesse (2)"):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_auslaesse',
                    "db_qkan: export_to_he8.export_auslaesse (2)"
                ):
                    logger.error_data('Gesamtzahl Auslässe nach Einfügen ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Auslässe eingefügt", 0.32)
                self.progress_bar.setValue(32)
        return True

    def _haltungen(self) -> bool:
        """Export Haltungen"""

        if QKan.config.check_export.haltungen:
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                  UPDATE he.Rohr SET
                  ( SchachtOben, SchachtUnten,
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Profiltyp, Sonderprofilbezeichnung,
                    Geometrie1, Geometrie2, 
                    Kanalart,
                    Rauigkeitsbeiwert, Anzahl,
                    RauhigkeitAnzeige,
                    Kommentar,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry) =
                  ( SELECT
                      ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                      coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                      coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                      coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                      coalesce(pf.he_nr, 68) AS Profiltyp, 
                      CASE WHEN coalesce(pf.he_nr, 68) = 68 THEN ha.profilnam
                      ELSE NULL
                      END                       AS Sonderprofilbezeichnung, 
                      coalesce(IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe), 0) AS Geometrie1, 
                      coalesce(IIF(ha.breite>20, ha.breite/1000, ha.breite),0) AS Geometrie2,
                      ea.he_nr AS Kanalart,
                      coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                      coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                      ha.kommentar AS Kommentar,
                      coalesce(ha.createdat, datetime('now')) AS LastModified, 
                      28 AS Materialart, 
                      0 AS Einzugsgebiet, 
                      0 AS KonstanterZuflussTezg, 
                      0 AS BefestigteFlaeche, 
                      0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                    FROM
                      haltungen AS ha 
                      JOIN schaechte AS sob ON ha.schoben = sob.schnam
                      JOIN schaechte AS sun ON ha.schunten = sun.schnam
                      LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf 
                        ON ha.profilnam = pf.profilnam
                      LEFT JOIN (SELECT bezeichnung, he_nr FROM entwaesserungsarten GROUP BY bezeichnung) AS ea 
                        ON ha.entwart = ea.bezeichnung
                      LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                      WHERE (ha.haltungstyp IS NULL or ha.haltungstyp = 'Haltung') AND ha.haltnam = he.Rohr.Name{auswahl})
                  WHERE he.Rohr.Name IN 
                  ( SELECT haltnam FROM haltungen AS ha
                    WHERE (ha.haltungstyp IS NULL OR ha.haltungstyp = 'Haltung'){auswahl})
                  """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_haltungen (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Haltungen in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Rohr"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_haltungen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                  INSERT INTO he.Rohr
                  ( Id, 
                    Name, SchachtOben, SchachtUnten, 
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Profiltyp, Sonderprofilbezeichnung, 
                    Geometrie1, Geometrie2, 
                    Kanalart, 
                    Rauigkeitsbeiwert, Anzahl, 
                    Rauigkeitsansatz, 
                    RauhigkeitAnzeige,
                    Kommentar,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry)
                  SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name, ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                    coalesce(ha.laenge, glength(ha.geom),0) AS Laenge,
                    coalesce(ha.sohleoben,sob.sohlhoehe,0) AS SohlhoeheOben,
                    coalesce(ha.sohleunten,sun.sohlhoehe,0) AS SohlhoeheUnten,
                    coalesce(pf.he_nr, 68) AS Profiltyp,
                    CASE WHEN coalesce(pf.he_nr, 68) = 68 THEN ha.profilnam
                    ELSE NULL
                    END
                    AS Sonderprofilbezeichnung, 
                    coalesce(IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe), 0) AS Geometrie1, 
                    coalesce(IIF(ha.breite>20, ha.breite/1000, ha.breite),0) AS Geometrie2,
                    ea.he_nr AS Kanalart,
                    coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                    1 AS Rauigkeitsansatz, 
                    coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                    ha.kommentar AS Kommentar,
                    coalesce(ha.createdat, datetime('now')) AS LastModified, 
                    28 AS Materialart,
                    0 AS Einzugsgebiet,
                    0 AS KonstanterZuflussTezg,
                    0 AS BefestigteFlaeche,
                    0 AS UnbefestigteFlaeche,
                  SetSrid(ha.geom, -1) AS Geometry
                  FROM
                    haltungen AS ha
                    JOIN schaechte AS sob ON ha.schoben = sob.schnam
                    JOIN schaechte AS sun ON ha.schunten = sun.schnam
                    LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                      ON ha.profilnam = pf.profilnam
                    LEFT JOIN (SELECT bezeichnung, he_nr FROM entwaesserungsarten GROUP BY bezeichnung) AS ea 
                      ON ha.entwart = ea.bezeichnung
                    LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                    WHERE 
                        ha.haltnam NOT IN (SELECT Name FROM he.Rohr) 
                        AND (ha.haltungstyp IS NULL OR ha.haltungstyp = 'Haltung'){auswahl};
                  """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_haltungen (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Rohr"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_haltungen (4)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Haltungen eingefügt", 0.70)
                self.progress_bar.setValue(70)
        return True

    def _flaechen(self) -> bool:
        """Export Flächenobjekte"""

        if QKan.config.check_export.flaechen:

            mindestflaeche = QKan.config.mindestflaeche
            autokorrektur = QKan.config.autokorrektur
            fangradius = QKan.config.fangradius
            mit_verschneidung = QKan.config.mit_verschneidung

            nr0 = None  # Für Fortschrittsmeldung

            # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
            if not checknames(self.db_qkan, "flaechen", "flnam", "f_", autokorrektur):
                return False

            if not updatelinkfl(self.db_qkan, fangradius):
                fehlermeldung(
                    "Fehler beim Update der Flächen-Verknüpfungen",
                    "Der logische Cache konnte nicht aktualisiert werden.",
                )
                return False

            # Zu verschneidende zusammen mit nicht zu verschneidene Flächen exportieren

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" WHERE fl.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            # Verschneidung nur, wenn (mit_verschneidung)
            if mit_verschneidung:
                case_verschneidung = "(fl.aufteilen <> 'ja' AND not fl.aufteilen) OR fl.aufteilen IS NULL"
                join_verschneidung = """
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam"""
                expr_verschneidung = """CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))"""
            else:
                case_verschneidung = "1"
                join_verschneidung = ""
                expr_verschneidung = "fl.geom"  # dummy

            if self.update:
                # aus Performancegründen wird die Auswahl der zu bearbeitenden Flächen in eine
                # temporäre Tabelle tempfl geschrieben
                sqllis = (
                    """CREATE TEMP TABLE IF NOT EXISTS flupdate (flnam TEXT)""",
                    """DELETE FROM flupdate""",
                    f"""
                    INSERT INTO flupdate (flnam)
                      SELECT substr(printf('%s-%d', fl.flnam, lf.pk),1,30) AS flnam 
                      FROM linkfl AS lf
                      INNER JOIN flaechen AS fl
                      ON lf.flnam = fl.flnam
                      INNER JOIN haltungen AS ha
                      ON lf.haltnam = ha.haltnam
                      LEFT JOIN abflusstypen AS at
                      ON lf.abflusstyp = at.abflusstyp
                      LEFT JOIN abflussparameter AS ap
                      ON fl.abflussparameter = ap.apnam
                      LEFT JOIN flaechentypen AS ft
                      ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl}""",
                    f"""
                    WITH flintersect AS (
                      SELECT substr(printf('%s-%d', fl.flnam, lf.pk),1,30) AS flnam, 
                        ha.haltnam AS haltnam, fl.neigkl AS neigkl,
                        at.he_nr AS abflusstyp, 
                        CASE WHEN ap.bodenklasse IS NULL THEN 0 ELSE 1 END AS typbef, 
                        coalesce(lf.speicherzahl, 2) AS speicherzahl, coalesce(lf.speicherkonst, 0) AS speicherkonst,
                        lf.fliesszeitflaeche AS fliesszeitflaeche, lf.fliesszeitkanal AS fliesszeitkanal,
                        CASE WHEN {case_verschneidung} THEN area(fl.geom)/10000 
                        ELSE area({expr_verschneidung})/10000 
                        END AS flaeche, 
                        fl.regenschreiber AS regenschreiber,
                        coalesce(ft.he_nr, 0) AS flaechentypnr, 
                        fl.abflussparameter AS abflussparameter, fl.createdat AS createdat,
                        fl.kommentar AS kommentar,
                        CASE WHEN {case_verschneidung} THEN fl.geom
                        ELSE {expr_verschneidung} 
                        END AS geom
                      FROM linkfl AS lf
                      INNER JOIN flaechen AS fl
                      ON lf.flnam = fl.flnam
                      INNER JOIN haltungen AS ha
                      ON lf.haltnam = ha.haltnam
                      LEFT JOIN abflusstypen AS at
                      ON lf.abflusstyp = at.abflusstyp
                      LEFT JOIN abflussparameter AS ap
                      ON fl.abflussparameter = ap.apnam
                      LEFT JOIN flaechentypen AS ft
                      ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl})
                    UPDATE he.Flaeche SET (
                      Haltung, Groesse, Regenschreiber, Flaechentyp, 
                      BerechnungSpeicherkonstante, Typ, AnzahlSpeicher,
                      Speicherkonstante, 
                      Schwerpunktlaufzeit,
                      FliesszeitOberflaeche, LaengsteFliesszeitKanal,
                      Parametersatz, Neigungsklasse, 
                      LastModified,
                      Kommentar, 
                      Geometry) = 
                    ( SELECT 
                        haltnam AS Haltung, flaeche AS Groesse, regenschreiber AS Regenschreiber, 
                        flaechentypnr AS Flaechentyp, 
                        COALESCE(abflusstyp, 2) AS BerechnungSpeicherkonstante, 
                        COALESCE(typbef,0) AS Typ, 
                        COALESCE(speicherzahl,3) AS AnzahlSpeicher, 
                        COALESCE(speicherkonst, 0.0) AS Speicherkonstante, 
                        COALESCE(fliesszeitflaeche, 0.0) AS Schwerpunktlaufzeit, 
                        COALESCE(fliesszeitflaeche,0.0) AS FliesszeitOberflaeche, 
                        COALESCE(fliesszeitkanal,0.0) AS LaengsteFliesszeitKanal, 
                        abflussparameter AS Parametersatz, coalesce(neigkl, 1) AS Neigungsklasse, 
                        coalesce(createdat, datetime('now')) AS lastmodified, 
                        kommentar AS Kommentar, 
                        SetSrid(geom, -1) AS Geometry
                      FROM flintersect AS fi
                      WHERE flnam = he.Flaeche.Name and flaeche*10000 > {mindestflaeche} and flaeche IS NOT NULL
                    ) WHERE he.Flaeche.Name IN (SELECT flnam FROM flupdate)
                    """,
                )

                for sql in sqllis:
                    if not self.db_qkan.sql(
                        sql, "db_qkan: export_to_he8.export_flaechen (1)"
                    ):
                        return False

            if self.append:
                # Feststellen der Anzahl Flächen in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Flaeche"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_flaechen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                    WITH flintersect AS (
                      SELECT
                        {nr0} + row_number() OVER (ORDER BY lf.flnam) AS Id, 
                        substr(printf('%s-%d', fl.flnam, lf.pk),1,30) AS flnam, 
                        ha.haltnam AS haltnam, fl.neigkl AS neigkl,
                        at.he_nr AS abflusstyp, 
                        CASE WHEN ap.bodenklasse IS NULL THEN 0 ELSE 1 END AS typbef, 
                        coalesce(lf.speicherzahl, 2) AS speicherzahl, coalesce(lf.speicherkonst, 0) AS speicherkonst,
                        lf.fliesszeitflaeche AS fliesszeitflaeche, lf.fliesszeitkanal AS fliesszeitkanal,
                        CASE WHEN {case_verschneidung} THEN area(fl.geom)/10000 
                        ELSE area({expr_verschneidung})/10000 
                        END AS flaeche, 
                        fl.regenschreiber AS regenschreiber, coalesce(ft.he_nr, 0) AS flaechentypnr, 
                        fl.abflussparameter AS abflussparameter, fl.createdat AS createdat,
                        fl.kommentar AS kommentar,
                        CASE WHEN {case_verschneidung} THEN fl.geom
                        ELSE {expr_verschneidung} 
                        END AS geom
                      FROM linkfl AS lf
                      INNER JOIN flaechen AS fl
                      ON lf.flnam = fl.flnam
                      INNER JOIN haltungen AS ha
                      ON lf.haltnam = ha.haltnam
                      LEFT JOIN abflusstypen AS at
                      ON lf.abflusstyp = at.abflusstyp
                      LEFT JOIN abflussparameter AS ap
                      ON fl.abflussparameter = ap.apnam
                      LEFT JOIN flaechentypen AS ft
                      ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl})
                    INSERT INTO he.Flaeche (
                      id, 
                      Name, Haltung, Groesse, Regenschreiber, Flaechentyp, 
                      BerechnungSpeicherkonstante, Typ, AnzahlSpeicher,
                      Speicherkonstante, 
                      Schwerpunktlaufzeit,
                      FliesszeitOberflaeche, LaengsteFliesszeitKanal,
                      Parametersatz, Neigungsklasse, ZuordnUnabhEZG, 
                      IstPolygonalflaeche, ZuordnungGesperrt, 
                      LastModified,
                      Kommentar, 
                      Geometry)
                    SELECT 
                      id AS id, 
                      flnam AS Name, haltnam AS Haltung, flaeche AS Groesse, regenschreiber AS Regenschreiber, 
                      flaechentypnr AS Flaechentyp, 
                      COALESCE(abflusstyp, 2) AS BerechnungSpeicherkonstante, 
                      COALESCE(typbef,0) AS Typ, 
                      COALESCE(speicherzahl,3) AS AnzahlSpeicher, 
                      COALESCE(speicherkonst, 0.0) AS Speicherkonstante, 
                      COALESCE(fliesszeitflaeche, 0.0) AS Schwerpunktlaufzeit, 
                      COALESCE(fliesszeitflaeche,0.0) AS FliesszeitOberflaeche, 
                      COALESCE(fliesszeitkanal,0.0) AS LaengsteFliesszeitKanal, 
                      abflussparameter AS Parametersatz, coalesce(neigkl, 1) AS Neigungsklasse, 
                      1 AS IstPolygonalflaeche, 1 AS ZuordnungGesperrt, 0 AS ZuordnUnabhEZG, 
                      coalesce(createdat, datetime('now')) AS lastmodified, 
                      kommentar AS Kommentar, 
                      SetSrid(geom, -1) AS Geometry
                    FROM flintersect AS fi
                    WHERE flaeche*10000 > {mindestflaeche} and (flnam NOT IN (SELECT Name FROM he.Flaeche))"""

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_flaechen (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Flaeche"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_flaechen (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Flächen eingefügt", 0.95)
                self.progress_bar.setValue(95)

        return True

    def _tezg(self) -> bool:
        """Export Haltungsflächen als befestigte und unbefestigte Flächen"""

        if QKan.config.check_export.tezg_hf:
            if self.append:
                # Feststellen der Anzahl Haltungsflaechen in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Flaeche"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_tezg (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                mindestflaeche = QKan.config.mindestflaeche

                sql = f"""
                    INSERT INTO he.Flaeche (
                      id, 
                      Name, Haltung, Groesse, Regenschreiber, Flaechentyp, 
                      BerechnungSpeicherkonstante, Typ, AnzahlSpeicher,
                      Speicherkonstante, 
                      Schwerpunktlaufzeit,
                      FliesszeitOberflaeche, LaengsteFliesszeitKanal,
                      Parametersatz, Neigungsklasse, ZuordnUnabhEZG, 
                      IstPolygonalflaeche, ZuordnungGesperrt, 
                      LastModified,
                      Kommentar, 
                      Geometry)
                    SELECT 
                      {nr0} + row_number() OVER (ORDER BY tg.flnam) AS Id, 
                      CASE WHEN tb.bef = 0
                        THEN printf('%s_b', tg.flnam)
                        ELSE printf('%s_u', tg.flnam) 
                      END           AS Name, 
                      tg.haltnam AS Haltung, 
                      area(tg.geom)/10000.*abs(tb.bef - coalesce(tg.befgrad, 0)/100.) AS Groesse, 
                      tg.regenschreiber AS Regenschreiber, 
                      coalesce(ft.he_nr, 0) AS Flaechentyp, 
                      2 AS BerechnungSpeicherkonstante, 
                      tb.bef AS Typ, 
                      2 AS AnzahlSpeicher, 
                      0. AS Speicherkonstante,                                  -- nicht verwendet 
                      coalesce(tg.schwerpunktlaufzeit/60., 0.) AS Schwerpunktlaufzeit,
                      0. AS FliesszeitOberflaeche,                              -- nicht verwendet 
                      0. AS LaengsteFliesszeitKanal,                            -- nicht verwendet
                      CASE WHEN tb.bef = 0
                        THEN '$Default_Bef'
                        ELSE '$Default_Unbef'
                      END       AS Parametersatz, 
                      coalesce(tg.neigkl, 1) AS Neigungsklasse, 
                      1 AS IstPolygonalflaeche, 1 AS ZuordnungGesperrt, 0 AS ZuordnUnabhEZG, 
                      coalesce(tg.createdat, datetime('now')) AS lastmodified, 
                      tg.kommentar AS Kommentar, 
                      SetSrid(tg.geom, -1) AS Geometry
                    FROM tezg AS tg
                    LEFT JOIN he.Flaeche AS fh
                    ON fh.Name = tg.flnam
                    , (SELECT he_nr FROM flaechentypen WHERE bezeichnung = 'Gebäude') AS ft
                    , (SELECT column1 AS bef FROM (VALUES (0) , (1))) AS tb
                    WHERE fh.Name IS NULL AND
                     area(tg.geom)*abs(tb.bef - coalesce(tg.befgrad, 0)/100.) > {mindestflaeche}"""

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_tezg (1)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Flaeche"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_tezg (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Haltungsflaechen eingefügt", 1.00)
                self.progress_bar.setValue(100)
        elif QKan.config.check_export.tezg:
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM tezg"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_tezg (2)"
                ):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                    logger.debug(f"idmin = {idmin}\nidmax = {idmax}\n")
                else:
                    fehlermeldung(
                        "Fehler (7) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung(
                        "Einfügen tezg als GIPS-TEZG", "Keine Haltungsflächen vorhanden"
                    )
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    mindestflaeche = QKan.config.mindestflaeche

                    sql = f"""
                        INSERT INTO he.GipsEinzugsflaeche (
                            id, 
                            Name, Haltung,
                            IsEinzugsflaeche,
                            IsHaltungsflaeche,
                            IsTwEinzugsflaeche, 
                            LastModified,
                            Kommentar, 
                            Geometry)
                        SELECT 
                            tg.rowid + {id0} AS id,
                            tg.flnam AS Name,
                            tg.haltnam AS Haltung,
                            0 AS IsEinzugsflaeche,
                            1 AS IsHaltungflaeche,
                            0 AS IsTwEinzugsflaeche, 
                            coalesce(tg.createdat, datetime('now')) AS lastmodified, 
                            tg.kommentar AS Kommentar, 
                            SetSrid(CastToMultiPolygon(tg.geom), -1) AS Geometry
                        FROM tezg AS tg
                    """

                    if not self.db_qkan.sql(sql, "db_qkan: export_to_he8.export_tezg (3)"):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        'he8_nextid',
                        parameters=(self.nextid,),
                    )

                    fortschritt("{} Haltungsflaechen eingefuegt".format(self.nextid - nr0), 0.90)
                    self.progress_bar.setValue(90)

        self.db_qkan.commit()

        return True

    def _pumpen(self) -> bool:
        """Export Pumpen"""

        if QKan.config.check_export.pumpen:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Pumpe SET
                    (   SchachtOben, SchachtUnten, 
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry 
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        WHERE ha.haltnam = he.Pumpe.Name
                    )
                    WHERE he.Pumpe.Name IN (
                        SELECT haltnam FROM haltungen AS ha WHERE ha.haltungstyp = 'Pumpe'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_pumpen (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Pumpen in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Pumpe"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_pumpen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                INSERT INTO he.Pumpe (
                    Id,
                    Name, 
                    SchachtOben, SchachtUnten,
                    Planungsstatus, 
                    Kommentar, LastModified,
                    Geometry 
                ) 
                SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name,
                    ha.schoben AS SchachtOben,
                    ha.schunten AS SchachtUnten,
                    si.he_nr AS Planungsstatus,
                    ha.kommentar AS Kommentar,
                    ha.createdat AS LastModified,
                    SetSrid(ha.geom, -1) AS Geometry
                FROM haltungen AS ha
                LEFT JOIN simulationsstatus AS si
                ON ha.simstatus = si.bezeichnung
                WHERE ha.haltungstyp = 'Pumpe'
                AND ha.haltnam NOT IN (SELECT Name FROM he.Pumpe){auswahl};
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_pumpen (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Pumpe"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_pumpen (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Pumpen eingefügt", 0.64)
                self.progress_bar.setValue(64)
        return True

    def _wehre(self) -> bool:
        """Export Pumpen"""

        if QKan.config.check_export.wehre:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Wehr SET
                    (   SchachtOben, SchachtUnten, 
                        Ueberfallbeiwert, 
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            wehre.uebeiwert AS Ueberfallbeiwert,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        WHERE ha.haltnam = he.Wehr.Name{auswahl}
                    )
                    WHERE he.Wehr.Name IN (
                        SELECT haltnam FROM haltungen AS ha WHERE ha.haltungstyp = 'Wehr'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_wehre (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Wehre in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Wehr"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_wehre (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                INSERT INTO he.Wehr (
                    Id,
                    Name, 
                    SchachtOben, SchachtUnten, 
                    Ueberfallbeiwert, 
                    Planungsstatus, 
                    Kommentar, LastModified,
                    Geometry
                ) 
                SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name,
                    ha.schoben AS SchachtOben,
                    ha.schunten AS SchachtUnten,
                    ha.ks AS Ueberfallbeiwert,
                    si.he_nr AS Planungsstatus,
                    ha.kommentar AS Kommentar,
                    ha.createdat AS LastModified,
                    SetSrid(ha.geom, -1) AS Geometry
                FROM haltungen AS ha
                LEFT JOIN simulationsstatus AS si
                ON ha.simstatus = si.bezeichnung
                WHERE ha.haltungstyp = 'Wehr'
                AND ha.haltnam NOT IN (SELECT Name FROM he.Wehr){auswahl};
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_wehre (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Wehr"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_wehre (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Wehre eingefügt", 0.62)
                self.progress_bar.setValue(62)
        return True

    def _drosseln(self) -> bool:
        """Export Drosseln"""

        if QKan.config.check_export.drosseln:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Drossel SET
                    (   SchachtOben, SchachtUnten, 
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        WHERE ha.haltnam = he.Drossel.Name{auswahl}
                    )
                    WHERE he.Drossel.Name IN (
                        SELECT haltnam FROM haltungen AS ha WHERE ha.haltungstyp = 'Drossel'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_drosseln (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Drosseln in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Drossel"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_drosseln (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                INSERT INTO he.Drossel (
                    Id,
                    Name, 
                    SchachtOben, SchachtUnten,
                    Planungsstatus,
                    Kommentar, LastModified,
                    Geometry
                ) 
                SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name,
                    ha.schoben AS SchachtOben,
                    ha.schunten AS SchachtUnten,
                    si.he_nr AS Planungsstatus,
                    ha.kommentar AS Kommentar,
                    ha.createdat AS LastModified,
                    SetSrid(ha.geom, -1) AS Geometry
                FROM haltungen AS ha
                LEFT JOIN simulationsstatus AS si
                ON ha.simstatus = si.bezeichnung
                WHERE ha.haltungstyp = 'Drossel'
                AND ha.haltnam NOT IN (SELECT Name FROM he.Drossel){auswahl};
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_drosseln (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Drossel"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_drosseln (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Drosseln eingefügt", 0.66)
                self.progress_bar.setValue(66)
        return True

    def _schieber(self) -> bool:
        """Export Drosseln"""

        if QKan.config.check_export.schieber:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Schieber SET
                    (   SchachtOben, SchachtUnten, 
                        Anfangsstellung, 
                        MaximaleHubhoehe,
                        Geometrie2,
                        Verluste,
                        Profiltyp,
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            ha.sohleoben AS Anfangsstellung,
                            ha.sohleoben + IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe) AS MaximaleHubhoehe,
                            IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                            ha.ks AS Verluste,
                            pf.he_nr AS Profiltyp,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                          ON ha.profilnam = pf.profilnam
                        WHERE ha.haltnam = he.Schieber.Name{auswahl}
                    )
                    WHERE he.Schieber.Name IN (
                        SELECT haltnam FROM haltungen AS ha WHERE ha.haltungstyp = 'Schieber'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_schieber (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Schieber in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Schieber"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_schieber (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                INSERT INTO he.Schieber (
                    Id,
                    Name, 
                    SchachtOben, SchachtUnten,
                    Anfangsstellung, 
                    MaximaleHubhoehe,
                    Geometrie2,
                    Verluste,
                    Profiltyp,
                    Planungsstatus,
                    Kommentar, LastModified,
                    Geometry
                ) 
                SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name,
                    ha.schoben AS SchachtOben,
                    ha.schunten AS SchachtUnten,
                    ha.sohleoben AS Anfangsstellung,
                    ha.sohleoben + IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe) AS MaximaleHubhoehe,
                    IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                    ha.ks AS Verluste,
                    pf.he_nr AS Profiltyp,
                    si.he_nr AS Planungsstatus,
                    ha.kommentar AS Kommentar,
                    ha.createdat AS LastModified,
                    SetSrid(ha.geom, -1) AS Geometry
                FROM haltungen AS ha
                LEFT JOIN simulationsstatus AS si
                ON ha.simstatus = si.bezeichnung
                LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                  ON ha.profilnam = pf.profilnam
                WHERE ha.haltungstyp = 'Schieber'
                AND ha.haltnam NOT IN (SELECT Name FROM he.Schieber){auswahl};
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_schieber (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Schieber"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_schieber (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Schieber eingefügt", 0.68)
                self.progress_bar.setValue(68)
        return True

    def _grundseitenauslaesse(self) -> bool:
        """Export Grund- und Seitenauslässe"""

        if QKan.config.check_export.grundseitenauslaesse:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.GrundSeitenauslass SET
                    (   SchachtOben, SchachtUnten, 
                        HoeheUnterkante,
                        Geometrie2,
                        Auslassbeiwert,
                        Profiltyp,
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            ha.sohleoben AS HoeheUnterkante,
                            IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                            ha.ks AS Auslassbeiwert,
                            pf.he_nr AS Profiltyp,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                          ON ha.profilnam = pf.profilnam
                        WHERE ha.haltnam = he.GrundSeitenauslass.Name{auswahl}
                    )
                    WHERE he.GrundSeitenauslass.Name IN (
                        SELECT haltnam FROM haltungen AS ha WHERE ha.haltungstyp = 'GrundSeitenauslass'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_grundseitenauslaesse (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Grund-/Seitenauslässe in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.GrundSeitenauslass"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_grundseitenauslaesse (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                INSERT INTO he.GrundSeitenauslass (
                    Id,
                    Name, 
                    SchachtOben, SchachtUnten,
                    HoeheUnterkante,
                    Geometrie2,
                    Auslassbeiwert,
                    Profiltyp,
                    Planungsstatus,
                    Kommentar, LastModified,
                    Geometry
                ) 
                SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name,
                    ha.schoben AS SchachtOben,
                    ha.schunten AS SchachtUnten,
                    ha.sohleoben AS HoeheUnterkante,
                    IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                    ha.ks AS Auslassbeiwert,
                    pf.he_nr AS Profiltyp,
                    si.he_nr AS Planungsstatus,
                    ha.kommentar AS Kommentar,
                    ha.createdat AS LastModified,
                    SetSrid(ha.geom, -1) AS Geometry
                FROM haltungen AS ha
                LEFT JOIN simulationsstatus AS si
                ON ha.simstatus = si.bezeichnung
                LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                  ON ha.profilnam = pf.profilnam
                WHERE ha.haltungstyp = 'GrundSeitenauslass'
                AND ha.haltnam NOT IN (SELECT Name FROM he.GrundSeitenauslass){auswahl};
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_grundseitenauslaesse (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.GrundSeitenauslass"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_grundseitenauslaesse (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Grund-/Seitenauslässe eingefügt", 0.74)
                self.progress_bar.setValue(74)
        return True

    def _qregler(self) -> bool:
        """Export Q-Regler"""

        if QKan.config.check_export.qregler:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                  UPDATE he.QRegler SET
                  ( SchachtOben, SchachtUnten,
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Geometrie1, Geometrie2, 
                    Kanalart,
                    Rauigkeitsbeiwert, Anzahl,
                    RauhigkeitAnzeige,
                    Profiltyp,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry) =
                  ( SELECT
                      ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                      coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                      coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                      coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                      IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe) AS Geometrie1, IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                      ea.he_nr AS Kanalart,
                      coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                      coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                      pf.he_nr AS Profiltyp,
                      coalesce(ha.createdat, datetime('now')) AS LastModified, 
                      28 AS Materialart, 
                      0 AS Einzugsgebiet, 
                      0 AS KonstanterZuflussTezg, 
                      0 AS BefestigteFlaeche, 
                      0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                    FROM
                      haltungen AS ha 
                      JOIN schaechte AS sob ON ha.schoben = sob.schnam
                      JOIN schaechte AS sun ON ha.schunten = sun.schnam
                      LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                        ON ha.profilnam = pf.profilnam
                      LEFT JOIN (SELECT bezeichnung, he_nr FROM entwaesserungsarten GROUP BY bezeichnung) AS ea 
                        ON ha.entwart = ea.bezeichnung
                      LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                      WHERE ha.haltungstyp = 'Q-Regler' AND ha.haltnam = he.QRegler.Name{auswahl})
                  WHERE he.QRegler.Name IN 
                  ( SELECT haltnam FROM haltungen AS ha WHERE ha.haltungstyp = 'Q-Regler'){auswahl}
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_qregler (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Q-Regler in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.QRegler"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_qregler (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                  INSERT INTO he.QRegler
                  ( Id, 
                    Name, SchachtOben, SchachtUnten, 
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Geometrie1, Geometrie2, 
                    Kanalart, 
                    Rauigkeitsbeiwert, Anzahl, 
                    Rauigkeitsansatz, 
                    RauhigkeitAnzeige,
                    Profiltyp,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry)
                  SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name, ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                    coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                    coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                    coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                    IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe) AS Geometrie1, IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                    ea.he_nr AS Kanalart,
                    coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                    1 AS Rauigkeitsansatz, 
                    coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                    pf.he_nr AS Profiltyp,
                    coalesce(ha.createdat, datetime('now')) AS LastModified, 
                    28 AS Materialart,
                    0 AS Einzugsgebiet,
                    0 AS KonstanterZuflussTezg,
                    0 AS BefestigteFlaeche,
                    0 AS UnbefestigteFlaeche,
                  SetSrid(ha.geom, -1) AS Geometry
                  FROM
                    haltungen AS ha
                    JOIN schaechte AS sob ON ha.schoben = sob.schnam
                    JOIN schaechte AS sun ON ha.schunten = sun.schnam
                    LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                      ON ha.profilnam = pf.profilnam
                    LEFT JOIN (SELECT bezeichnung, he_nr FROM entwaesserungsarten GROUP BY bezeichnung) AS ea 
                      ON ha.entwart = ea.bezeichnung
                    LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                    WHERE ha.haltnam NOT IN (SELECT Name FROM he.QRegler) 
                    AND ha.haltungstyp = 'Q-Regler'{auswahl};
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_qregler (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.QRegler"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_qregler (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Q-Regler eingefügt", 0.70)
                self.progress_bar.setValue(70)
        return True

    def _hregler(self) -> bool:
        """Export H-Regler"""

        if QKan.config.check_export.hregler:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                  UPDATE he.HRegler SET
                  ( SchachtOben, SchachtUnten,
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Geometrie1, Geometrie2, 
                    Kanalart,
                    Rauigkeitsbeiwert, Anzahl,
                    RauhigkeitAnzeige,
                    Profiltyp,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry) =
                  ( SELECT
                      ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                      coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                      coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                      coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                      IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe) AS Geometrie1, IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                      ea.he_nr AS Kanalart,
                      coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                      coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                      pf.he_nr AS Profiltyp,
                      coalesce(ha.createdat, datetime('now')) AS LastModified, 
                      28 AS Materialart, 
                      0 AS Einzugsgebiet, 
                      0 AS KonstanterZuflussTezg, 
                      0 AS BefestigteFlaeche, 
                      0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                    FROM
                      haltungen AS ha 
                      JOIN schaechte AS sob ON ha.schoben = sob.schnam
                      JOIN schaechte AS sun ON ha.schunten = sun.schnam
                      LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                        ON ha.profilnam = pf.profilnam
                      LEFT JOIN (SELECT bezeichnung, he_nr FROM entwaesserungsarten GROUP BY bezeichnung) AS ea 
                        ON ha.entwart = ea.bezeichnung
                      LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                      WHERE ha.haltungstyp = 'H-Regler' AND ha.haltnam = he.HRegler.Name{auswahl})
                  WHERE he.HRegler.Name IN 
                  ( SELECT haltnam FROM haltungen AS ha WHERE ha.haltungstyp = 'H-Regler'){auswahl}
                    """

                if not self.db_qkan.sql(
                    'he8_update_',
                    "db_qkan: export_to_he8.export_hregler (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl H-Regler in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.HRegler"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_h_regler (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                  INSERT INTO he.HRegler
                  ( Id, 
                    Name, SchachtOben, SchachtUnten, 
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Geometrie1, Geometrie2, 
                    Kanalart, 
                    Rauigkeitsbeiwert, Anzahl, 
                    Rauigkeitsansatz, 
                    RauhigkeitAnzeige,
                    Profiltyp,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry)
                  SELECT
                    {nr0} + row_number() OVER (ORDER BY ha.haltnam) AS Id, 
                    ha.haltnam AS Name, ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                    coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                    coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                    coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                    IIF(ha.hoehe>20, ha.hoehe/1000, ha.hoehe) AS Geometrie1, IIF(ha.breite>20, ha.breite/1000, ha.breite) AS Geometrie2,
                    ea.he_nr AS Kanalart,
                    coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                    1 AS Rauigkeitsansatz, 
                    coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                    pf.he_nr AS Profiltyp,
                    coalesce(ha.createdat, datetime('now')) AS LastModified, 
                    28 AS Materialart,
                    0 AS Einzugsgebiet,
                    0 AS KonstanterZuflussTezg,
                    0 AS BefestigteFlaeche,
                    0 AS UnbefestigteFlaeche,
                  SetSrid(ha.geom, -1) AS Geometry
                  FROM
                    haltungen AS ha
                    JOIN schaechte AS sob ON ha.schoben = sob.schnam
                    JOIN schaechte AS sun ON ha.schunten = sun.schnam
                    LEFT JOIN (SELECT profilnam, he_nr FROM profile GROUP BY profilnam) AS pf
                      ON ha.profilnam = pf.profilnam
                    LEFT JOIN (SELECT bezeichnung, he_nr FROM entwaesserungsarten GROUP BY bezeichnung) AS ea 
                      ON ha.entwart = ea.bezeichnung
                    LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                    WHERE ha.haltnam NOT IN (SELECT Name FROM he.HRegler) 
                    AND ha.haltungstyp = 'H-Regler'{auswahl};
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_hregler (3)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.HRegler"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_h_regler (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} H-Regler eingefügt", 0.72)
                self.progress_bar.setValue(72)
        return True

    def _abflussparameter(self) -> bool:
        """Export Abflussparameter"""

        if QKan.config.check_export.abflussparameter:
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT count(*) FROM he.AbflussParameter"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_Abflussparameter (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                INSERT INTO he.AbflussParameter (
                    Id,
                    Name, 
                    AbflussbeiwertAnfang, AbflussbeiwertEnde, 
                    Muldenverlust, Benetzungsverlust, 
                    BenetzungSpeicherStart, MuldenauffuellgradStart, 
                    Typ, 
                    Bodenklasse, 
                    Kommentar, LastModified
                    )
                SELECT 
                    {nr0} + row_number() OVER (ORDER BY ap.apnam) AS Id, 
                    ap.apnam,
                    ap.anfangsabflussbeiwert, ap.endabflussbeiwert,
                    ap.muldenverlust, ap.benetzungsverlust, 
                    ap.benetzung_startwert, ap.mulden_startwert, 
                    CASE WHEN ap.bodenklasse IS NULL THEN 0 ELSE 1 END AS Typ,
                    ap.bodenklasse, 
                    ap.kommentar, ap.createdat
                FROM abflussparameter AS ap
                LEFT JOIN he.AbflussParameter AS ha
                ON ha.Name = ap.apnam
                WHERE ha.Name IS NULL
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_abflussparameter (2)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.AbflussParameter"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_Abflussparameter (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )

                self.db_qkan.commit()

                fortschritt("{} Abflussparameter eingefuegt".format(anzn - anzv), 0.04)
                self.progress_bar.setValue(4)


        return True

    def _bodenklassen(self) -> bool:
        """Export der Bodenklassen"""

        if QKan.config.check_export.bodenklassen:
            if self.append:
                # Feststellen der Anzahl Bodenklassen in ITWH-Datenbank fuer korrekte Werte von nextid
                sql = "SELECT count(*) FROM he.Bodenklasse"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_Bodenklassen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sql = f"""
                INSERT INTO he.Bodenklasse (
                    Id, Name, 
                    InfiltrationsrateAnfang, InfiltrationsrateEnde, InfiltrationsrateStart, 
                    Rueckgangskonstante, Regenerationskonstante, Saettigungswassergehalt, 
                    Kommentar, LastModified
                )
                SELECT 
                    {nr0} + row_number() OVER (ORDER BY bk.bknam) AS Id, 
                    bk.bknam, 
                    bk.infiltrationsrateanfang, bk.infiltrationsrateende, bk.infiltrationsratestart, 
                    bk.rueckgangskonstante, bk.regenerationskonstante, bk.saettigungswassergehalt, 
                    bk.kommentar, bk.createdat
                FROM bodenklassen AS bk
                LEFT JOIN he.Bodenklasse AS hb
                ON hb.Name = bk.bknam
                WHERE hb.Name IS NULL
                """

                if not self.db_qkan.sql(
                    sql, "db_qkan: export_to_he8.export_abflussparameter (2)"
                ):
                    return False

                sql = "SELECT count(*) FROM he.Bodenklasse"
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_Bodenklassen (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sql(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt("{} Abflussparameter eingefuegt".format(anzn - anzv), 0.02)
                self.progress_bar.setValue(2)

        return True
