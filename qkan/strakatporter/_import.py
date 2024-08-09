import os
import re
from struct import unpack
from typing import Iterator

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis, QgsGeometry, QgsPoint
from qkan import QKan
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

logger = get_logger("QKan.strakat.import")


class Bericht_STRAKAT(ClassObject):
    datum: str = ""
    untersucher: str = ""
    ag_kontrolle: str = ""
    fahrzeug: str = ""
    inspekteur: str = ""
    wetter: str = ""
    atv149: float = 0.0
    fortsetzung: int = 0
    station_gegen: float = 0.0
    station_untersucher: float = 0.0
    atv_kuerzel: str = ""
    atv_langtext: str = ""
    charakt1: str = ""
    charakt2: str = ""
    quantnr1: int = 0
    quantnr2: int = 0
    streckenschaden: str = ""
    pos_von: int = 0
    pos_bis: int = 0
    sandatum: str = ""
    geloescht: int = 0
    schadensklasse: int = 0
    untersuchungsrichtung: int = 0
    bandnr: str = ""
    videozaehler: int = 0
    sanierung: str = ""
    atv143: float = 0.0
    skdichtheit: int = 0
    skbetriebssicherheit: int = 0
    skstandsicherheit: int = 0
    kommentar: str = ""
    strakatid: str = ""
    hausanschlid: str = ""
    berichtid: str = ""


class Kanal_STRAKAT(ClassObject):
    nummer: int = 0
    rw_gerinne_o: float = 0.0
    hw_gerinne_o: float = 0.0
    rw_gerinne_u: float = 0.0
    hw_gerinne_u: float = 0.0
    rw_rohranfang: float = 0.0
    hw_rohranfang: float = 0.0
    rw_rohrende: float = 0.0
    hw_rohrende: float = 0.0
    zuflussnummer1: int = 0
    zuflussnummer2: int = 0
    zuflussnummer3: int = 0
    zuflussnummer4: int = 0
    zuflussnummer5: int = 0
    zuflussnummer6: int = 0
    zuflussnummer7: int = 0
    zuflussnummer8: int = 0
    abflussnummer1: int = 0
    abflussnummer2: int = 0
    abflussnummer3: int = 0
    abflussnummer4: int = 0
    abflussnummer5: int = 0
    schacht_oben: str = ""
    schacht_unten: str = ""
    haltungsname: str = ""
    rohrbreite_v: float = 0.0
    rohrhoehe___v: float = 0.0
    flaechenfactor_v: float = 0.0
    deckel_oben_v: float = 0.0
    deckel_unten_v: float = 0.0
    sohle_oben___v: float = 0.0
    sohle_unten__v: float = 0.0
    s_sohle_oben_v: float = 0.0
    sohle_zufluss1: float = 0.0
    sohle_zufluss2: float = 0.0
    sohle_zufluss3: float = 0.0
    sohle_zufluss4: float = 0.0
    sohle_zufluss5: float = 0.0
    sohle_zufluss6: float = 0.0
    sohle_zufluss7: float = 0.0
    sohle_zufluss8: float = 0.0
    kanalart: int = 0
    profilart_v: int = 0
    material_v: int = 0
    e_gebiet: int = 0
    strassennummer: int = 0
    schachtnummer: int = 0
    schachtart: int = 0
    berichtsnummer: int = 0
    laenge: float = 0.0
    schachtmaterial: int = 0
    oberflaeche: int = 0
    baujahr: int = 0
    wasserschutz: int = 0
    eigentum: int = 0
    naechste_halt: int = 0
    rueckadresse: int = 0
    strakatid: str = ""


class ImportTask:
    def __init__(
        self,
        db_qkan: DBConnection,
    ):
        # all parameters (except db_qkan) are passed via QKan.config
        self.db_qkan = db_qkan
        self.allrefs = QKan.config.check_import.allrefs
        self.epsg = QKan.config.epsg
        self.dbtyp = QKan.config.database_typ
        self.strakatdir = QKan.config.strakat.import_dir
        self.projectfile = QKan.config.project.file
        self.db_name = QKan.config.database.qkan
        self.richtung = QKan.config.xml.richt_choice
        self.kriterienschaeden = QKan.config.zustand.kriterienschaeden
        self.maxdiff = QKan.config.strakat.maxdiff


    def run(self) -> bool:

        self.iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(self.iface.messageBar())
        self.progress_bar.setRange(0, 100)

        self.status_message = self.iface.messageBar().createMessage(
            "", "Import aus STRAKAT läuft. Bitte warten..."
        )
        self.status_message.layout().addWidget(self.progress_bar)
        self.iface.messageBar().pushWidget(self.status_message, Qgis.Info, 60)
        self.progress_bar.setValue(0)
        logger.debug("progress_bar initialisiert")

        result = all(
            [
                self._strakat_kanaltabelle(), self.progress_bar.setValue(30),   logger.debug("_strakat_kanaltabelle"),
                self._strakat_reftables(), self.progress_bar.setValue(10),      logger.debug("_strakat_reftables"),
                self._reftables(), self.progress_bar.setValue(15),              logger.debug("_reftables"),
                self._schaechte(), self.progress_bar.setValue(40),              logger.debug("_schaechte"),
                self._haltungen(), self.progress_bar.setValue(50),              logger.debug("_haltungen"),
                self._strakat_hausanschl(), self.progress_bar.setValue(80),     logger.debug("_strakat_hausanschl"),
                self._anschlussleitungen(), self.progress_bar.setValue(90),     logger.debug("_anschlussleitungen"),

                self.db_qkan._adapt_reftable('entwaesserungsarten'),

                self._strakat_berichte(), self.progress_bar.setValue(95),       logger.debug("_strakat_berichte"),
                self._haltungen_untersucht(),                                   logger.debug("_haltungen_untersucht"),
                self._untersuchdat_haltung(),                                   logger.debug("_untersuchdat_haltung"),
                self._schaechte_untersucht(),                                   logger.debug("_schaechte_untersucht"),
                self._untersuchdat_schacht(),                                   logger.debug("_untersuchdat_schacht"),
            ]
        )

        self.progress_bar.setValue(100)
        self.status_message.setText("Fertig! STRAKAT-Import abgeschlossen.")

        self.iface.messageBar().clearWidgets()

        return result

    def _strakat_kanaltabelle(self) -> bool:
        """Import der Kanaldaten aus der STRAKAT-Datei 'kanal.rwtopen', entspricht ACCESS-Tabelle 'KANALTABELLE'
        """

        # Erstellung Tabelle t_strakatkanal
        sql = "PRAGMA table_list('t_strakatkanal')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_strakatkanal', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_strakatkanal (
                pk INTEGER PRIMARY KEY,
                nummer INTEGER,
                rw_gerinne_o REAL,
                hw_gerinne_o REAL,
                rw_gerinne_u REAL,
                hw_gerinne_u REAL,
                rw_rohranfang REAL,
                hw_rohranfang REAL,
                rw_rohrende REAL,
                hw_rohrende REAL,
                zuflussnummer1 INTEGER,
                zuflussnummer2 INTEGER,
                zuflussnummer3 INTEGER,
                zuflussnummer4 INTEGER,
                zuflussnummer5 INTEGER,
                zuflussnummer6 INTEGER,
                zuflussnummer7 INTEGER,
                zuflussnummer8 INTEGER,
                abflussnummer1 INTEGER,
                abflussnummer2 INTEGER,
                abflussnummer3 INTEGER,
                abflussnummer4 INTEGER,
                abflussnummer5 INTEGER,
                schacht_oben TEXT,
                schacht_unten TEXT,
                haltungsname TEXT,
                rohrbreite_v REAL,
                rohrhoehe___v REAL,
                flaechenfactor_v REAL,
                deckel_oben_v REAL,
                deckel_unten_v REAL,
                sohle_oben___v REAL,
                sohle_unten__v REAL,
                s_sohle_oben_v REAL,           -- Position in Datei kanal.rwtopen unbekannt
                sohle_zufluss1 REAL,
                sohle_zufluss2 REAL,
                sohle_zufluss3 REAL,
                sohle_zufluss4 REAL,
                sohle_zufluss5 REAL,
                sohle_zufluss6 REAL,
                sohle_zufluss7 REAL,
                sohle_zufluss8 REAL,
                kanalart INTEGER,
                profilart_v INTEGER,
                material_v INTEGER,
                e_gebiet INTEGER,
                strassennummer INTEGER,
                schachtnummer INTEGER,
                schachtart INTEGER,
                berichtsnummer INTEGER,
                laenge REAL,
                schachtmaterial INTEGER,
                oberflaeche INTEGER,
                baujahr INTEGER,
                wasserschutz INTEGER,
                eigentum INTEGER,
                naechste_halt INTEGER,
                rueckadresse INTEGER,
                mark INTEGER DEFAULT 0,
                strakatid TEXT
            )"""
            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakatkanal"'):
                return False

            sqls = [
                f"SELECT AddGeometryColumn('t_strakatkanal', 'geom', {self.epsg}, 'LINESTRING')",
                "SELECT CreateSpatialIndex('t_strakatkanal', 'geom')",
                f"SELECT AddGeometryColumn('t_strakatkanal', 'geop', {self.epsg}, 'POINT')",
                "SELECT CreateSpatialIndex('t_strakatkanal', 'geop')",
            ]
            for sql in sqls:
                if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import ergänze geom und geop in t_strakatkanal"):
                    logger.error('Fehler beim Ergänzen von geom und geop in t_strakatkanal')
                    return False

            self.db_qkan.commit()

        def _iter() -> Iterator[Kanal_STRAKAT]:
        # Datei kanal.rwtopen einlesen und in Tabelle schreiben
            blength = 1024                      # Blocklänge in der STRAKAT-Datei
            with open(os.path.join(self.strakatdir, 'kanal.rwtopen'), 'rb') as fo:

                _ = fo.read(blength)               # Kopfzeile ohne Bedeutung?

                maxloop = 1000000           # Begrenzung zur Sicherheit. Falls erreicht: Meldung
                for n in range(1, maxloop):
                    b = fo.read(blength)
                    if not b:
                        break
                    (
                        rw_gerinne_o, hw_gerinne_o,
                        rw_gerinne_u, hw_gerinne_u,
                        rw_rohranfang, hw_rohranfang,
                        rw_rohrende, hw_rohrende
                    ) = (round(el, 3) for el in unpack('dddddddd', b[0:64]))

                    (
                        zuflussnummer1, zuflussnummer2,
                        zuflussnummer3, zuflussnummer4,
                        zuflussnummer5, zuflussnummer6,
                        zuflussnummer7, zuflussnummer8,
                        abflussnummer1, abflussnummer2,
                        abflussnummer3, abflussnummer4,
                        abflussnummer5
                    ) = unpack('iiiiiiiiiiiii', b[64:116])

                    schacht_oben = b[172:b[172:187].find(b'\x00')+172].decode('ansi').strip()
                    haltungsname = b[187:b[187:202].find(b'\x00')+187].decode('ansi').strip()

                    (
                        rohrbreite_v, rohrbreite_g, rohrhoehe___v, rohrhoehe___g,
                        wandstaerke_v, wandstaerke_g, ersatzdu___v, ersatzdu___g,
                        flaechenfactor_v, flaechenfactor_g, umfangsfactor_v, umfangsfactor_g,
                        hydr__radius_v, hydr__radius_g
                    ) = unpack('ffffffffffffff', b[116:172])

                    (
                        deckel_oben_v, deckel_oben_g, deckel_unten_v, deckel_unten_g,
                        sohle_oben___v, sohle_oben___g, sohle_unten__v, sohle_unten__g
                    ) = (round(el, 3) for el in unpack('ffffffff', b[202:234]))

                    s_sohle_oben_v = 0.0                        # Position in Datei kanal.rwtopen unbekannt

                    (
                        sohle_zufluss1, sohle_zufluss2, sohle_zufluss3, sohle_zufluss4,
                        sohle_zufluss5, sohle_zufluss6, sohle_zufluss7, sohle_zufluss8
                    ) = (round(el, 3) for el in unpack('ffffffff', b[434:466]))

                    (
                        kanalart, profilart_v, profilart_g, material_v,
                        material_g, e_gebiet, strassennummer
                    ) = unpack('hhhhhhh', b[490:504])

                    (
                        schachtnummer, schachtart
                    ) = unpack('ih', b[504:510])

                    (  # kann nicht mit dem vorherigen
                        berichtsnummer, laenge, schachtmaterial  # zusammengefasst werden, weil Startadresse
                    ) = unpack('ifh', b[510:520])  # glattes Vielfaches der Länge sein muss

                    laenge = round(laenge, 3)

                    oberflaeche = unpack('h', b[528:530])[0]
                    oberflaeche_b = b[528:530]
                    baujahr = unpack('h', b[550:552])[0]
                    wasserschutz = unpack('h', b[554:556])[0]
                    eigentum = unpack('h', b[556:558])[0]
                    naechste_halt = unpack('i', b[558:562])[0]
                    rueckadresse = unpack('i', b[562:566])[0]

                    nummer = unpack('i', b[829:833])[0]

                    (
                        h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                    ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[917:933])]
                    strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                    schacht_unten = b[965:b[965:980].find(b'\x00')+965].decode('ansi').strip()

                    yield Kanal_STRAKAT(
                        nummer=nummer,
                        rw_gerinne_o=rw_gerinne_o,
                        hw_gerinne_o=hw_gerinne_o,
                        rw_gerinne_u=rw_gerinne_u,
                        hw_gerinne_u=hw_gerinne_u,
                        rw_rohranfang=rw_rohranfang,
                        hw_rohranfang=hw_rohranfang,
                        rw_rohrende=rw_rohrende,
                        hw_rohrende=hw_rohrende,
                        zuflussnummer1=zuflussnummer1,
                        zuflussnummer2=zuflussnummer2,
                        zuflussnummer3=zuflussnummer3,
                        zuflussnummer4=zuflussnummer4,
                        zuflussnummer5=zuflussnummer5,
                        zuflussnummer6=zuflussnummer6,
                        zuflussnummer7=zuflussnummer7,
                        zuflussnummer8=zuflussnummer8,
                        abflussnummer1=abflussnummer1,
                        abflussnummer2=abflussnummer2,
                        abflussnummer3=abflussnummer3,
                        abflussnummer4=abflussnummer4,
                        abflussnummer5=abflussnummer5,
                        schacht_oben=schacht_oben,
                        schacht_unten=schacht_unten,
                        haltungsname=haltungsname,
                        rohrbreite_v=rohrbreite_v,
                        rohrhoehe___v=rohrhoehe___v,
                        flaechenfactor_v=flaechenfactor_v,
                        deckel_oben_v=deckel_oben_v,
                        deckel_unten_v=deckel_unten_v,
                        sohle_oben___v=sohle_oben___v,
                        sohle_unten__v=sohle_unten__v,
                        s_sohle_oben_v=s_sohle_oben_v,
                        sohle_zufluss1=sohle_zufluss1,
                        sohle_zufluss2=sohle_zufluss2,
                        sohle_zufluss3=sohle_zufluss3,
                        sohle_zufluss4=sohle_zufluss4,
                        sohle_zufluss5=sohle_zufluss5,
                        sohle_zufluss6=sohle_zufluss6,
                        sohle_zufluss7=sohle_zufluss7,
                        sohle_zufluss8=sohle_zufluss8,
                        kanalart=kanalart,
                        profilart_v=profilart_v,
                        material_v=material_v,
                        e_gebiet=e_gebiet,
                        strassennummer=strassennummer,
                        schachtnummer=schachtnummer,
                        schachtart=schachtart,
                        berichtsnummer=berichtsnummer,
                        laenge=laenge,
                        schachtmaterial=schachtmaterial,
                        oberflaeche=oberflaeche,
                        baujahr=baujahr,
                        wasserschutz=wasserschutz,
                        eigentum=eigentum,
                        naechste_halt=naechste_halt,
                        rueckadresse=rueckadresse,
                        strakatid=strakatid,
                    )
                else:
                    logger.error('Programmfehler: Einlesen der Datei "kanal.rwtopen wurde nach '
                                 '1000000 Datensätze abgebrochen!"')
                    return False

        params = ()                           # STRAKAT data stored in tuple of dicts for better performance
                                            # with sql-statement executemany
        logger.debug("{__name__}: Berichte werden gelesen und in data gespeichert ...")

        for _schacht in _iter():
            data = {
                'nummer': _schacht.nummer,
                'rw_gerinne_o': _schacht.rw_gerinne_o, 'hw_gerinne_o': _schacht.hw_gerinne_o,
                'rw_gerinne_u': _schacht.rw_gerinne_u, 'hw_gerinne_u': _schacht.hw_gerinne_u,
                'rw_rohranfang': _schacht.rw_rohranfang, 'hw_rohranfang': _schacht.hw_rohranfang,
                'rw_rohrende': _schacht.rw_rohrende, 'hw_rohrende': _schacht.hw_rohrende,
                'zuflussnummer1': _schacht.zuflussnummer1, 'zuflussnummer2': _schacht.zuflussnummer2,
                'zuflussnummer3': _schacht.zuflussnummer3, 'zuflussnummer4': _schacht.zuflussnummer4,
                'zuflussnummer5': _schacht.zuflussnummer5, 'zuflussnummer6': _schacht.zuflussnummer6,
                'zuflussnummer7': _schacht.zuflussnummer7, 'zuflussnummer8': _schacht.zuflussnummer8,
                'abflussnummer1': _schacht.abflussnummer1, 'abflussnummer2': _schacht.abflussnummer2,
                'abflussnummer3': _schacht.abflussnummer3, 'abflussnummer4': _schacht.abflussnummer4,
                'abflussnummer5': _schacht.abflussnummer5,
                'schacht_oben': _schacht.schacht_oben, 'schacht_unten': _schacht.schacht_unten,
                'haltungsname': _schacht.haltungsname,
                'rohrbreite_v': _schacht.rohrbreite_v, 'rohrhoehe___v': _schacht.rohrhoehe___v,
                'flaechenfactor_v': _schacht.flaechenfactor_v,
                'deckel_oben_v': _schacht.deckel_oben_v, 'deckel_unten_v': _schacht.deckel_unten_v,
                'sohle_oben___v': _schacht.sohle_oben___v, 'sohle_unten__v': _schacht.sohle_unten__v,
                's_sohle_oben_v': 0.0,
                'sohle_zufluss1': _schacht.sohle_zufluss1, 'sohle_zufluss2': _schacht.sohle_zufluss2,
                'sohle_zufluss3': _schacht.sohle_zufluss3, 'sohle_zufluss4': _schacht.sohle_zufluss4,
                'sohle_zufluss5': _schacht.sohle_zufluss5, 'sohle_zufluss6': _schacht.sohle_zufluss6,
                'sohle_zufluss7': _schacht.sohle_zufluss7, 'sohle_zufluss8': _schacht.sohle_zufluss8,
                'kanalart': _schacht.kanalart, 'profilart_v': _schacht.profilart_v,
                'material_v': _schacht.material_v,
                'e_gebiet': _schacht.e_gebiet, 'strassennummer': _schacht.strassennummer,
                'schachtnummer': _schacht.schachtnummer, 'schachtart': _schacht.schachtart,
                'berichtsnummer': _schacht.berichtsnummer,
                'laenge': _schacht.laenge, 'schachtmaterial': _schacht.schachtmaterial,
                'oberflaeche': _schacht.oberflaeche,
                'baujahr': _schacht.baujahr, 'wasserschutz': _schacht.wasserschutz, 'eigentum': _schacht.eigentum,
                'naechste_halt': _schacht.naechste_halt, 'rueckadresse': _schacht.rueckadresse,
                'strakatid': _schacht.strakatid
            }
            params += (data,)

        logger.debug("{__name__}: Berichte werden in temporäre STRAKAT-Tabellen geschrieben ...")

        sql = """INSERT INTO t_strakatkanal (
            nummer, 
            rw_gerinne_o, hw_gerinne_o, rw_gerinne_u, hw_gerinne_u,
            rw_rohranfang, hw_rohranfang, rw_rohrende, hw_rohrende,
            zuflussnummer1, zuflussnummer2, zuflussnummer3, zuflussnummer4,
            zuflussnummer5, zuflussnummer6, zuflussnummer7, zuflussnummer8,
            abflussnummer1, abflussnummer2, abflussnummer3, abflussnummer4, abflussnummer5,
            schacht_oben, schacht_unten, haltungsname,
            rohrbreite_v, rohrhoehe___v, flaechenfactor_v,
            deckel_oben_v, deckel_unten_v, sohle_oben___v, sohle_unten__v, s_sohle_oben_v,
            sohle_zufluss1, sohle_zufluss2, sohle_zufluss3, sohle_zufluss4,
            sohle_zufluss5, sohle_zufluss6, sohle_zufluss7, sohle_zufluss8,
            kanalart, profilart_v, material_v,
            e_gebiet, strassennummer,
            schachtnummer, schachtart, berichtsnummer,
            laenge, schachtmaterial, oberflaeche,
            baujahr, wasserschutz, eigentum,
            naechste_halt, rueckadresse, strakatid
        )
        VALUES (
            :nummer, 
            :rw_gerinne_o, :hw_gerinne_o, :rw_gerinne_u, :hw_gerinne_u,
            :rw_rohranfang, :hw_rohranfang, :rw_rohrende, :hw_rohrende,
            :zuflussnummer1, :zuflussnummer2, :zuflussnummer3, :zuflussnummer4,
            :zuflussnummer5, :zuflussnummer6, :zuflussnummer7, :zuflussnummer8,
            :abflussnummer1, :abflussnummer2, :abflussnummer3, :abflussnummer4, :abflussnummer5,
            :schacht_oben, :schacht_unten, :haltungsname,
            :rohrbreite_v, :rohrhoehe___v, :flaechenfactor_v,
            :deckel_oben_v, :deckel_unten_v, :sohle_oben___v, :sohle_unten__v, :s_sohle_oben_v,
            :sohle_zufluss1, :sohle_zufluss2, :sohle_zufluss3, :sohle_zufluss4,
            :sohle_zufluss5, :sohle_zufluss6, :sohle_zufluss7, :sohle_zufluss8,
            :kanalart, :profilart_v, :material_v,
            :e_gebiet, :strassennummer,
            :schachtnummer, :schachtart, :berichtsnummer,
            :laenge, :schachtmaterial, :oberflaeche,
            :baujahr, :wasserschutz, :eigentum,
            :naechste_halt, :rueckadresse, :strakatid                
        )"""

        if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Schächte", parameters=params, many=True):
            logger.error('Fehler beim Lesen der Datei "kanal.rwtopen"')
            return False

        sqls = [
            f"""UPDATE t_strakatkanal
                SET geom = MakeLine(
                    Makepoint(rw_gerinne_o, hw_gerinne_o, {self.epsg}),
                    Makepoint(rw_gerinne_u, hw_gerinne_u, {self.epsg})
                )
                WHERE rw_gerinne_o > 1
                  AND rw_gerinne_u > 1
                  AND hw_gerinne_o > 1
                  AND hw_gerinne_u > 1
            """,
            f"""UPDATE t_strakatkanal
                SET geop = Makepoint(rw_gerinne_o, hw_gerinne_o, {self.epsg})
                WHERE rw_gerinne_o > 1   AND hw_gerinne_o > 1
            """,
            "DELETE FROM t_strakatkanal WHERE schachtnummer = 0"
        ]
        for sql in sqls:
            if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Geoobjekte t_strakatkanal"):
                logger.error('Fehler beim Erzeugen der Geoobjekte t_strakatkanal')
                return False

        # Bereinigung inkonsistenter Schachtbezeichnungen

        # 1. Übertragen des schacht_oben auf Kanäle ohne schachtoben oder mit einem schachtoben,
        #    der nicht mit anderen Schachtoben übereinstimmt.
        sqls = [
            # 1.0 Fehlende Schachtbezeichnungen ergänzen
            "UPDATE t_strakatkanal SET schacht_oben = 'S_' || substr(printf('0000%d', pk), -5) WHERE schacht_oben = ''",
            # 1.1 Abzweigende Haltungen (k1k), deren schacht_oben nicht mit dem eines durchlaufenden
            #     Stranges (schacht_unten = schacht_oben: k2k) übereinstimmt.
            f"""WITH k2k AS (
                    SELECT ku.ROWID, ku.nummer, ku.geop, ku.schacht_oben, ku.schachtart, ku.kanalart
                    FROM t_strakatkanal ko
                    JOIN t_strakatkanal ku ON ko.abflussnummer1 = ku.nummer AND ko.schacht_unten = ku.schacht_oben
                ),
                k1k AS (
                    SELECT
                        k1.nummer AS n1, k2.nummer AS n2, k1.schacht_oben AS schoben_diff, 
                        k2.schacht_oben AS schoben, k1.schachtart, k1.kanalart
                    FROM k2k AS k2
                    JOIN t_strakatkanal AS k1 ON st_distance(k2.geop, k1.geop) < {self.maxdiff}
                    WHERE
                        k2.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name='t_strakatkanal'
                            AND search_frame=makecircle(x(k1.geop),y(k1.geop), {self.maxdiff}, {self.epsg}))
                        AND k2.schacht_oben <> k1.schacht_oben
                )
                UPDATE t_strakatkanal SET schacht_oben = ksk.schoben
                FROM (SELECT n1, schoben FROM k1k) AS ksk
                WHERE ksk.n1 = t_strakatkanal.nummer AND ksk.schoben <> ''""",

            # 1.2 Unterschiedliche Schachtnamen an der gleichen Position
            f"""WITH k2k AS (
                    SELECT k2.nummer AS nummer, k1.schacht_oben AS schoben
                    FROM t_strakatkanal AS k2
                    JOIN t_strakatkanal AS k1 ON st_distance(k2.geop, k1.geop) < {self.maxdiff}
                    WHERE
                        k2.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name='t_strakatkanal'
                            AND search_frame=makecircle(x(k1.geop),y(k1.geop), {self.maxdiff}, {self.epsg}))
                        AND k1.schacht_oben <> k2.schacht_oben AND k1.nummer < k2.nummer
                )
                UPDATE t_strakatkanal SET schacht_oben = ksk.schoben
                FROM (SELECT nummer, schoben FROM k2k) AS ksk
                WHERE ksk.nummer = t_strakatkanal.nummer AND ksk.schoben <> ''""",

            # 1.3 Test der Haltungen, die über "abflussnummmerx" und "zuflussnummerx" verbunden sind.
            """ WITH ka AS (
                    SELECT n1 AS id, n4, kurz, text
                    FROM t_reflists
                    WHERE tabtyp = 'schachtart' 
                ),
                sx AS (
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer1 = ku.nummer
                    WHERE ko.abflussnummer1 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer2 = ku.nummer
                    WHERE ko.abflussnummer2 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer3 = ku.nummer
                    WHERE ko.abflussnummer3 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer4 = ku.nummer
                    WHERE ko.abflussnummer4 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer5 = ku.nummer
                    WHERE ko.abflussnummer5 > 0 AND ko.schacht_unten <> ku.schacht_oben
                )
                UPDATE t_strakatkanal SET schacht_unten = sx.schacht_oben
                FROM sx
                WHERE sx.nummer_oben = t_strakatkanal.nummer AND t_strakatkanal.schacht_unten <> sx.schacht_oben AND sx.schacht_oben <> ''""",
        ]
        for sql in sqls:
            if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Korrektur Schachtnamen t_strakatkanal"):
                logger.error('Fehler bei der Korrektur der Schachtnamen t_strakatkanal')
                return False

        self.db_qkan.commit()

        return True

    def _strakat_reftables(self) -> bool:
        """Import der STRAKAT-Referenztabellen aus der STRAKAT-Datei 'referenztabelle.strakat'
        """

        # Erstellung Tabelle t_reflists. Diese Tabelle enthält die STRAKAT-Rohdaten aller Referenztabellen.
        # Diese werden in den einzelnen Importen mittels Filter auf die Spalte "tabtyp" spezifiziert und eingebunden.
        sql = "PRAGMA table_list('t_reflists')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_reflists', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_reflists (
                pk INTEGER PRIMARY KEY,
                id INTEGER,                 -- Schlüssel je Tabellenart
                tabtyp TEXT,                -- Tabellenart
                n1 INTEGER,                 -- Inhalt abhängig von von tabtyp 
                n2 INTEGER,                 -- Inhalt abhängig von von tabtyp
                n3 INTEGER,                 -- Inhalt abhängig von von tabtyp
                n4 INTEGER,                 -- Inhalt abhängig von von tabtyp
                n5 INTEGER,                 -- Inhalt abhängig von von tabtyp
                kurz TEXT, 
                text TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_reflists"'):
                return False

        t_typen = {
            1: 'kanalart',
            2: 'rohrmaterial',
            3: 'profilart',
            4: 'entwaesserungsgebiet',
            5: 'schachtart',
            6: 'auflagerart',
            7: 'wasserhaltung',
            8: 'verbau',
            9: 'absturzart',
            10: 'deckelart',
            11: 'erschwernis',
            12: 'oberflaeche',
            13: 'eigentum',
            14: 'wasserschutzzone',
            15: 'massnahme',
            16: 'genauigkeit',
            17: 'sanierungsmassnahme',
            19: 'herkunkft',
            20: 'hausanschlussart',
            21: 'schachtmaterial',
            27: 'strasse',
        }

        # Datei referenztabelle.strakat einlesen und in Tabelle schreiben
        blength = 128                       # Blocklänge in der STRAKAT-Datei
        with open(os.path.join(self.strakatdir, 'system', 'referenztabelle.strakat'), 'rb') as fo:
            idvor = -1                          # Erkennung eines neuen Tabellentyps
            for n in range(1, 1000000):
                """Einlesen der Blöcke. Begrenzung nur zur Sicherheit"""
                b = fo.read(blength)

                if b:
                    (
                        n0, n1, n2, n3, n4, n5
                    ) = unpack('HHHHBB', b[0:10])
                else:
                    break

                # Prüfen, ob: 1. Wechsel zu anderer List, 2. Listenende
                nextlist = False
                if n0 != idvor:
                    endelist = False
                    nextlist = True
                    idvor = n0
                elif endelist:
                    continue
                if b[10:128] == b'\x00' * 118:
                    endelist = True
                    continue

                tabtyp = t_typen.get(n0, None)
                if not tabtyp:
                    # Tabellentyp unbekannt
                    continue

                id = n1

                kurz = b[10:b[10:26].find(b'\x00')+10].decode('ansi')
                text = b[26:b[26:128].find(b'\x00')+26].decode('ansi')

                params = {'tabtyp': tabtyp, 'id': id,
                          'n1': n1, 'n2': n2, 'n3': n3, 'n4': n4, 'n5': n5,
                          'kurz': kurz, 'text': text}

                sql = """INSERT INTO t_reflists (
                    tabtyp, id,
                    n1, n2, n3, n4, n5, 
                    kurz, text                    
                )
                VALUES (
                    :tabtyp, :id, :n1, :n2, :n3, :n4, :n5, :kurz, :text
                )"""

                if not self.db_qkan.sql(sql, "strakat_import Referenztabellen", params):
                    logger.error('Fehler beim Lesen der Datei "system/referenztabelle.strakat"')
                    return False
            else:
                logger.error('Programmfehler: Einlesen der Datei "system/referenztabelle.strakat"'
                             ' wurde nicht ordnungsgemäß abgeschlossen!"')
                return False

        self.db_qkan.commit()

        return True

    def _strakat_hausanschl(self) -> bool:
        """Import der Hausanschlussdaten aus der STRAKAT-Datei 'haus.rwtopen', entspricht ACCESS-Tabelle 'HAUSANSCHLUSSTABELLE'
        """

        # Erstellung Tabelle t_strakathausanschluesse
        sql = "PRAGMA table_list('t_strakathausanschluesse')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_strakathausanschluesse', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_strakathausanschluesse (
                pk INTEGER PRIMARY KEY,
                nummer INTEGER,
                nextnum INTEGER,
                x1 REAL,
                x2 REAL,
                x3 REAL,
                x4 REAL,
                x5 REAL,
                x6 REAL,
                x7 REAL,
                x8 REAL,
                x9 REAL,
                y1 REAL,
                y2 REAL,
                y3 REAL,
                y4 REAL,
                y5 REAL,
                y6 REAL,
                y7 REAL,
                y8 REAL,
                y9 REAL,
                rohrbreite REAL,
                berichtnr INTEGER,
                anschlusshalnr INTEGER,
                anschlusshalname TEXT,
                haschob TEXT,
                haschun TEXT,
                urstation REAL,
                strakatid TEXT,
                hausanschlid TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakathausanschluesse"'):
                return False

        # Datei haus.rwtopen einlesen und in Tabelle schreiben
        blength = 640                      # Blocklänge in der STRAKAT-Datei
        with open(os.path.join(self.strakatdir, 'haus.rwtopen'), 'rb') as fo:
            _ = fo.read(blength)               # Kopfzeile ohne Bedeutung?
            for nummer in range(1, 1000000):
                """Einlesen der Blöcke. Begrenzung nur zur Sicherheit"""
                b = fo.read(blength)
                if not b or len(b) < blength:
                    break
                xlis = list(unpack('ddddddddd', b[20:92]))
                ylis = list(unpack('ddddddddd', b[100:172]))
                # d1, d2, d3, d4, d5, d6, d7, d8, d9 = unpack('fffffffff', b[220:256])

                # Erste x-Koordinate = 0 auf alle folgenden übertragen, weil in STRAKAT manchmal
                # in den hinteren Spalten noch Reste von alten Koordinaten stehen
                # In QKan (s. u.) werden alle Koordinaten mit xi < 0 unterdrückt
                for i in range(2, 8):
                    if xlis[i] < 1:
                        xlis[i+1] = -xlis[i+1]      # für nachträgliche Kontrolle

                (x1, x2, x3, x4, x5, x6, x7, x8, x9) = xlis
                (y1, y2, y3, y4, y5, y6, y7, y8, y9) = ylis

                rohrbreite = unpack('f', b[220:224])[0]  # nur erste von 9 Rohrbreiten lesen

                berichtnr = unpack('i', b[299:303])[0]
                anschlusshalnr = unpack('i', b[303:307])[0]
                nextnum = unpack('i', b[311:315])[0]

                haschob = b[326:b[326:346].find(b'\x00')+326].decode('ansi').strip()
                haschun = b[362:b[362:382].find(b'\x00')+362].decode('ansi').strip()

                urstation = unpack('f', b[515:519])[0]

                anschlusshalname = b[611:b[611:631].find(b'\x00')+611].decode('ansi').strip()

                (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                 ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[524:540])]
                strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'
                (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                 ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[540:556])]
                hausanschlid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                params = {
                    'nummer': nummer, 'nextnum': nextnum,
                    'x1': x1, 'x2': x2, 'x3': x3,
                    'x4': x4, 'x5': x5, 'x6': x6,
                    'x7': x7, 'x8': x8, 'x9': x9,
                    'y1': y1, 'y2': y2, 'y3': y3,
                    'y4': y4, 'y5': y5, 'y6': y6,
                    'y7': y7, 'y8': y8, 'y9': y9,
                    'rohrbreite': rohrbreite,
                    'berichtnr': berichtnr,
                    'anschlusshalnr': anschlusshalnr, 'anschlusshalname': anschlusshalname,
                    'haschob': haschob, 'haschun': haschun, 'urstation': urstation,
                    'strakatid': strakatid, 'hausanschlid': hausanschlid,
                }

                sql = """INSERT INTO t_strakathausanschluesse (
                    nummer, nextnum,
                    x1, x2, x3,
                    x4, x5, x6,
                    x7, x8, x9,
                    y1, y2, y3,
                    y4, y5, y6,
                    y7, y8, y9,
                    rohrbreite,
                    berichtnr,
                    anschlusshalnr, anschlusshalname,
                    haschob, haschun, urstation,
                    strakatid, hausanschlid
                )
                VALUES (
                    :nummer, :nextnum,
                    :x1, :x2, :x3,
                    :x4, :x5, :x6,
                    :x7, :x8, :x9,
                    :y1, :y2, :y3,
                    :y4, :y5, :y6,
                    :y7, :y8, :y9,
                    :rohrbreite,
                    :berichtnr,
                    :anschlusshalnr, :anschlusshalname,
                    :haschob, :haschun, :urstation,
                    :strakatid, :hausanschlid
                )"""

                if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
                    logger.error('Fehler beim Lesen der Datei "haus.rwtopen"')
                    return False
            else:
                logger.error('Programmfehler: Einlesen der Datei "kanal.rwtopen wurde nicht '
                             'ordnungsgemäß abgeschlossen!"')
                return False

        self.db_qkan.commit()

        return True

    def _strakat_berichte(self) -> bool:
        """Import der Schadensdaten aus der STRAKAT-Datei 'ENBericht.rwtopen', entspricht ACCESS-Tabelle 'SCHADENSTABELLE'
        """
        # Erstellung Tabelle t_strakatberichte
        sql = "PRAGMA table_list('t_strakatberichte')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_strakatberichte', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_strakatberichte (
                pk INTEGER PRIMARY KEY,
                datum TEXT,
                untersucher TEXT,
                ag_kontrolle TEXT,
                fahrzeug TEXT,
                inspekteur TEXT,
                wetter TEXT,
                atv149 REAL,
                fortsetzung INTEGER,
                station_gegen REAL,
                station_untersucher REAL,
                atv_kuerzel TEXT,
                atv_langtext TEXT,
                charakt1 TEXT,
                charakt2 TEXT,
                quantnr1 TEXT,
                quantnr2 TEXT,
                streckenschaden TEXT,
                pos_von INTEGER,
                pos_bis INTEGER,
                sandatum TEXT,
                geloescht INTEGER,
                schadensklasse INTEGER,
                untersuchungsrichtung INTEGER,
                bandnr TEXT,
                videozaehler INTEGER,
                sanierung TEXT,
                atv143 REAL,
                skdichtheit INTEGER,
                skbetriebssicherheit INTEGER,
                skstandsicherheit INTEGER,
                kommentar TEXT,
                strakatid TEXT,
                hausanschlid TEXT,
                berichtid TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakatberichte"'):
                return False

        def _iter() -> Iterator[Bericht_STRAKAT]:
            # Datei kanal.rwtopen einlesen und in Tabelle schreiben
            blength = 1024                      # Blocklänge in der STRAKAT-Datei
            leer = b'\x00'*128
            with open(os.path.join(self.strakatdir, 'ENBericht.rwtopen'), 'rb') as fo:

                _ = fo.read(blength)               # Kopfzeile ohne Bedeutung?

                if QKan.config.check_import.testmodus:
                    maxloop = 20000  # Testmodus für Anwender
                else:
                    maxloop = 5000000  # Begrenzung zur Sicherheit. Falls erreicht: Meldung

                for n in range(1, maxloop):
                    b = fo.read(blength)
                    if not b:
                        break

                    anf = b[0:128]
                    rest = b[896:1024]          # if rest != leer
                    if anf == leer:
                        continue
                    datum = b[0:10].decode('ansi')
                    if datum[2] != '.' or datum[5] != '.':
                        if re.fullmatch('\\d\\d[\\.\\,\\:\\;\\/\\*\\>\\+\\-_]'
                                        '\\d\\d[\\.\\,\\:\\;\\/\\*\\>\\+\\-_]\\d\\d\\d\\d',
                                        datum
                                        ):
                            logger.debug(f"Warnung STRAKAT-Berichte Nr. {n}: Datumsformat wird korrigiert: {datum}")
                            datum = datum[:2] + '.' + datum[3:5] + '.' + datum[6:10]
                        else:
                            logger.debug(f"Lesefehler STRAKAT-Berichte Nr. {n}: Datumsformat fehlerhaft"
                                         f". Datensatz wird ignoriert: {datum}")

                            continue
                    datum = datum[6:10] + '-' + datum[3:5] + '-' + datum[:2]
                    untersucher = b[11:b[11:31].find(b'\x00') + 11].decode('ansi').strip()
                    ag_kontrolle = b[31:b[31:46].find(b'\x00') + 31].decode('ansi').strip()
                    fahrzeug = b[46:b[46:57].find(b'\x00') + 46].decode('ansi').strip()
                    inspekteur = b[58:b[58:74].find(b'\x00') + 58].decode('ansi').strip()
                    wetter = b[73:b[73:88].find(b'\x00') + 73].decode('ansi').strip()

                    atv149 = unpack('f', b[90:94])[0]

                    fortsetzung = unpack('I', b[103:107])[0]
                    station_gegen = round(unpack('d', b[107:115])[0], 3)
                    station_untersucher = round(unpack('d', b[115:123])[0], 3)

                    atv_kuerzel = b[123:b[123:134].find(b'\x00') + 123].decode('ansi').strip()
                    if not atv_kuerzel:
                        continue
                    atv_langtext = b[134:b[134:295].find(b'\x00') + 134].decode('ansi').strip()
                    sandatum = b[284:294].decode('ansi')
                    geloescht = unpack('b', b[296:297])[0]
                    schadensklasse = unpack('B', b[295:296])[0]
                    untersuchungsrichtung = unpack('B', b[297:298])[0]
                    bandnr = b[301:b[301:320].find(b'\x00') + 301].decode('ansi').strip()
                    videozaehler = unpack('I', b[320:324])[0]

                    pos_von, pos_bis = unpack('BB', b[366:368])                                 # STRAKT: von/bis Uhr
                    sanierung = b[400:b[400:411].find(b'\x00') + 400].decode('ansi').strip()
                    atv143 = unpack('f', b[430:434])[0]

                    quantnr1, quantnr2 = unpack('bb', b[434:436])
                    streckenschaden = b[436:b[436:437].find(b'\x00') + 436].decode('ansi').strip()
                    charakt1 = b[438:b[438:449].find(b'\x00') + 438].decode('ansi').strip()
                    charakt2 = b[449:b[449:].find(b'\x00') + 449].decode('ansi').strip()

                    anmerkung = b[463:b[463:715].find(b'\x00') + 463].decode('ansi').strip()
                    if sanierung != '' and anmerkung != '':
                        kommentar = sanierung + ', ' + anmerkung
                    else:
                        kommentar = sanierung + anmerkung               # eins von beiden ist leer

                    skdichtheit, skstandsicherheit, skbetriebssicherheit = unpack('BBB', b[634:637])

                    (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                     ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[643:659])]
                    strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'
                    (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                     ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[659:675])]
                    hausanschlid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'
                    (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                     ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[675:691])]
                    berichtid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                    yield Bericht_STRAKAT(
                        datum=datum,
                        untersucher=untersucher,
                        ag_kontrolle=ag_kontrolle,
                        fahrzeug=fahrzeug,
                        inspekteur=inspekteur,
                        wetter=wetter,
                        atv149=atv149,
                        fortsetzung=fortsetzung,
                        station_gegen=station_gegen,
                        station_untersucher=station_untersucher,
                        atv_kuerzel=atv_kuerzel,
                        atv_langtext=atv_langtext,
                        charakt1=charakt1,
                        charakt2=charakt2,
                        quantnr1=quantnr1,
                        quantnr2=quantnr2,
                        streckenschaden=streckenschaden,
                        pos_von=pos_von,
                        pos_bis=pos_bis,
                        sandatum=sandatum,
                        geloescht=geloescht,
                        schadensklasse=schadensklasse,
                        untersuchungsrichtung=untersuchungsrichtung,
                        bandnr=bandnr,
                        videozaehler=videozaehler,
                        sanierung=sanierung,
                        atv143=atv143,
                        skdichtheit=skdichtheit,
                        skbetriebssicherheit=skbetriebssicherheit,
                        skstandsicherheit=skstandsicherheit,
                        kommentar=kommentar,
                        strakatid=strakatid,
                        hausanschlid=hausanschlid,
                        berichtid=berichtid,
                    )
                else:
                    if QKan.config.check_import.testmodus:
                        logger.debug(f"Testmodus: Import Berichte nach {maxloop}. Datensatz abgebrochen")
                    else:
                        logger.error('Programmfehler: Einlesen der Datei "kanal.rwtopen wurde nicht '
                                 'ordnungsgemäß abgeschlossen!"')
                    return False

        params = ()                           # STRAKAT data stored in tuple of dicts for better performance
                                            # with sql-statement executemany
        logger.debug("{__name__}: Berichte werden gelesen und in data gespeichert ...")

        for _bericht in _iter():
            data = {
                'datum': _bericht.datum,
                'untersucher': _bericht.untersucher,
                'ag_kontrolle': _bericht.ag_kontrolle,
                'fahrzeug': _bericht.fahrzeug,
                'inspekteur': _bericht.inspekteur,
                'wetter': _bericht.wetter,
                'atv149': _bericht.atv149,
                'fortsetzung': _bericht.fortsetzung,
                'station_gegen': _bericht.station_gegen,
                'station_untersucher': _bericht.station_untersucher,
                'atv_kuerzel': _bericht.atv_kuerzel,
                'atv_langtext': _bericht.atv_langtext,
                'charakt1': _bericht.charakt1,
                'charakt2': _bericht.charakt2,
                'quantnr1': _bericht.quantnr1,
                'quantnr2': _bericht.quantnr2,
                'streckenschaden': _bericht.streckenschaden,
                'pos_von': _bericht.pos_von,
                'pos_bis': _bericht.pos_bis,
                'sandatum': _bericht.sandatum,
                'geloescht': _bericht.geloescht,
                'schadensklasse': _bericht.schadensklasse,
                'untersuchungsrichtung': _bericht.untersuchungsrichtung,
                'bandnr': _bericht.bandnr,
                'videozaehler': _bericht.videozaehler,
                'sanierung': _bericht.sanierung,
                'atv143': _bericht.atv143,
                'skdichtheit': _bericht.skdichtheit,
                'skbetriebssicherheit': _bericht.skbetriebssicherheit,
                'skstandsicherheit': _bericht.skstandsicherheit,
                'kommentar': _bericht.kommentar,
                'strakatid': _bericht.strakatid,
                'hausanschlid': _bericht.hausanschlid,
                'berichtid': _bericht.berichtid,
            }
            params += (data,)

        logger.debug("{__name__}: Berichte werden in temporäre STRAKAT-Tabellen geschrieben ...")

        sql = """
            INSERT INTO t_strakatberichte (
                datum, 
                untersucher, 
                ag_kontrolle, 
                fahrzeug, 
                inspekteur, 
                wetter, 
                atv149, 
                fortsetzung, 
                station_gegen, 
                station_untersucher, 
                atv_kuerzel, 
                atv_langtext, 
                charakt1,
                charakt2,
                quantnr1,
                quantnr2,
                streckenschaden,
                pos_von,
                pos_bis,
                sandatum, 
                geloescht, 
                schadensklasse, 
                untersuchungsrichtung, 
                bandnr, 
                videozaehler, 
                sanierung, 
                atv143, 
                skdichtheit, 
                skbetriebssicherheit,
                skstandsicherheit, 
                kommentar, 
                strakatid, 
                hausanschlid, 
                berichtid
            ) VALUES (
                :datum, 
                :untersucher, 
                :ag_kontrolle, 
                :fahrzeug, 
                :inspekteur, 
                :wetter, 
                :atv149, 
                :fortsetzung, 
                :station_gegen, 
                :station_untersucher, 
                :atv_kuerzel, 
                :atv_langtext, 
                :charakt1,
                :charakt2,
                :quantnr1,
                :quantnr2,
                :streckenschaden,
                :pos_von,
                :pos_bis,
                :sandatum, 
                :geloescht, 
                :schadensklasse, 
                :untersuchungsrichtung, 
                :bandnr, 
                :videozaehler, 
                :sanierung, 
                :atv143, 
                :skdichtheit, 
                :skbetriebssicherheit,
                :skstandsicherheit, 
                :kommentar, 
                :strakatid, 
                :hausanschlid, 
                :berichtid
            )
        """

        if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Bericht", parameters=params, many=True):
            logger.error('Fehler beim Lesen der Datei "ENBericht.rwtopen"')
            return False

        self.db_qkan.commit()

        logger.debug("{__name__}: Berichte werden in QKan-Tabellen geschrieben ...")

        return True

    def _reftables(self) -> bool:
        """Referenztabellen füllen"""

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert

        # Referenztabelle Entwässerungsarten

        sql = """INSERT INTO entwaesserungsarten (bezeichnung, kuerzel, bemerkung)
                 SELECT text, kurz, 'Importiert aus STRAKAT'
                 FROM t_reflists
                 WHERE tabtyp = 'kanalart'"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste entwaesserungsarten"):
            return False

        # Ergänzen weiterer Kennnummern in speziellen Datensätzen
        daten = [
            ('Regenwasser', 'KR', 'Regenwasser', 1, 2, 'R', 'KR', 0, 0),
            ('Schmutzwasser', 'KS', 'Schmutzwasser', 2, 1, 'S', 'KS', 0, 0),
            ('Mischwasser', 'KM', 'Mischwasser', 0, 0, 'M', 'KM', 0, 0),
        ]

        params = [(ds[3], ds[4], ds[5], ds[6], ds[7], ds[8], ds[0],) for ds in daten]           # umsortieren
        sql = """UPDATE entwaesserungsarten
                 SET he_nr = ?, kp_nr = ?, m150 = ?, isybau = ?, transport = ?, druckdicht = ?
                 WHERE bezeichnung = ?"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste entwaesserungsarten", params, many=True):
            return False

        # Referenztabelle Haltungstypen

        daten = [
            ('Haltung', None),
            ('Drossel', 'HYSTEM-EXTRAN 8'),
            ('H-Regler', 'HYSTEM-EXTRAN 8'),
            ('Q-Regler', 'HYSTEM-EXTRAN 8'),
            ('Schieber', 'HYSTEM-EXTRAN 8'),
            ('GrundSeitenauslass', 'HYSTEM-EXTRAN 8'),
            ('Pumpe', None),
            ('Wehr', None),
        ]

        params = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE
        sql = """INSERT INTO haltungstypen (bezeichnung, bemerkung)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM haltungstypen)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste haltungstypen", params, many=True):
            return False

        # Referenztabelle Rohrprofile

        sql = """INSERT INTO profile (profilnam, kuerzel, kommentar)
                 SELECT text, kurz, 'Importiert aus STRAKAT'
                 FROM t_reflists
                 WHERE tabtyp = 'profilart'"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste profile"):
            return False

        # Referenztabelle Entwässerungsgebiete

        sql = """INSERT INTO teilgebiete (tgnam, kommentar)
                 SELECT rl.text, 'Importiert aus STRAKAT'
                 FROM t_reflists AS rl
                 JOIN t_strakatkanal AS skt ON skt.e_gebiet = rl.id         -- nur verwendete
                 WHERE tabtyp = 'entwaesserungsgebiet'
                 GROUP BY rl.id"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste profile"):
            return False


        # Referenztabelle Pumpentypen

        daten = [
            ('Offline', 1),
            ('Online Schaltstufen', 2),
            ('Online Kennlinie', 3),
            ('Online Wasserstandsdifferenz', 4),
            ('Ideal', 5),
        ]

        params = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO pumpentypen (bezeichnung, he_nr)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM pumpentypen)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste pumpentypen", params, many=True):
            return False

        # Referenztabelle Untersuchungsrichtung

        daten = [
            ('in Fließrichtung', '0', 'automatisch hinzugefügt'),
            ('gegen Fließrichtung', 'U', 'automatisch hinzugefügt'),
        ]

        params = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO untersuchrichtung (bezeichnung, kuerzel, bemerkung)
                    SELECT ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM untersuchrichtung)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste untersuchrichtung", params, many=True):
            return False

        # Erstellung Tabelle t_mapper_untersuchrichtung
        sql = "PRAGMA table_list('t_mapper_untersuchrichtung')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_mapper_untersuchrichtung', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_mapper_untersuchrichtung (
                id INTEGER PRIMARY KEY,
                untersuchungsrichtung TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_mapper_untersuchrichtung"'):
                return False

        # Liste enthält nur Schachtarten, die nicht 'Schacht' und dabei 'vorhanden' sind (einschließlich 1: 'NS Normalschacht')
        daten = [
            (0,  'in Fließrichtung'),
            (1,  'gegen Fließrichtung'),
        ]
        sql = """INSERT INTO t_mapper_untersuchrichtung (id, untersuchungsrichtung)
                    SELECT ? AS id, ? as untersuchungsrichtung
                WHERE id NOT IN (SELECT id FROM t_mapper_untersuchrichtung)"""

        if not self.db_qkan.sql(sql,
                                "strakat_import Referenzliste t_mapper_untersuchrichtung",
                                daten,
                                many=True):
            return False

        self.db_qkan.commit()

        return True

        # Liste der Kanalarten entspricht im Wesentlichen der QKan-Tabelle 'Entwässerungsarten'

    def _schaechte(self) -> bool:
        """Import der Schächte aus der STRAKAT-Tabelle KANALTABELLE"""

        sql = """WITH
            stk_oberhalb AS (
                SELECT nummer, abflussnummer1
                FROM t_strakatkanal
                WHERE schachtnummer <> 0
            ),
            strassen AS (
                SELECT n1 AS id, kurz, text AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            schachtmaterial AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'schachtmaterial'
            ),
            entwart AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'kanalart' 
            ),
            knotenart AS (
                SELECT n1 AS id, n4, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'schachtart' 
            ),
            gebiet AS (
                SELECT n1 AS id, text, kurz
                FROM t_reflists
                WHERE tabtyp = 'entwaesserungsgebiet'
            )
            INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, strasse, material, 
                                durchm, entwart, schachttyp, knotentyp, teilgebiet,
                                kommentar, geop, geom)
            SELECT
                CASE WHEN stk.schacht_oben = ''
                THEN printf('strakatnr_%1', stk.nummer)
                ELSE stk.schacht_oben
                END                                         AS schnam,
                stk.rw_gerinne_o                 AS xsch,
                stk.hw_gerinne_o                 AS ysch,
                MIN(CASE WHEN stk.s_sohle_oben_v<1 Or stk.s_sohle_oben_v > 5000
                    THEN stk.sohle_oben___v
                    ELSE stk.s_sohle_oben_v
                    END
                )                                           AS sohlhoehe,
                MAX(CASE WHEN stk.deckel_oben_v <1 Or stk.deckel_oben_v > 5000
                    THEN Null 
                    ELSE stk.deckel_oben_v
                    END
                )                                           AS deckelhoehe,
                CASE WHEN INSTR(strassen.name,' ') > 0
                    THEN substr(strassen.name, INSTR(strassen.name,' ')+1)
                    ELSE strassen.name
                END                                         AS strasse,
                schachtmaterial.text                        AS material,
                1.0                                         AS durchm,
                k2e.text                                    AS entwart,
                'Schacht'                                   AS schachttyp,
                k2t.text                                    AS knotentyp,
                k2g.text                                    AS teilgebiet,
                CASE WHEN count(*) > 1
                THEN printf('Schacht in STRAKAT %s mal vorhanden', count(*))
                ELSE 'QKan-STRAKAT-Import' END              AS kommentar,
                Makepoint(stk.rw_gerinne_o, stk.hw_gerinne_o, :epsg)  AS geop,
                CastToMultiPolygon(MakePolygon(MakeCircle(
                    stk.rw_gerinne_o, stk.hw_gerinne_o, 1.0, :epsg))) AS geom
            FROM
                t_strakatkanal AS stk
                LEFT JOIN stk_oberhalb               
                ON stk.nummer = stk_oberhalb.abflussnummer1
                LEFT JOIN strassen                              
                ON stk.strassennummer = strassen.id
                LEFT JOIN schachtmaterial                       
                ON stk.schachtmaterial = schachtmaterial.id
                JOIN entwart AS k2e           
                ON stk.kanalart = k2e.id
                JOIN knotenart AS k2t
                ON stk.schachtart = k2t.id
                JOIN gebiet AS k2g
                ON stk.e_gebiet = k2g.id
            WHERE
                    stk.schachtnummer <> 0
                AND stk.schachtart <> 0
                AND (
                    stk_oberhalb.abflussnummer1 Is Not Null AND 
                    stk.zuflussnummer1 = stk_oberhalb.nummer
                    OR
                    stk_oberhalb.abflussnummer1 Is Null AND
                    stk.zuflussnummer1 = 0
                )
            GROUP BY
                schnam, xsch, ysch,
                strasse, material, schachttyp
            HAVING
                schnam Is Not Null
                AND xsch Is Not Null
                AND ysch Is Not Null
            """

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
            logger.error('Fehler in strakat_import Schächte')
            return False

        self.db_qkan.commit()

        return True

    def _haltungen(self) -> bool:
        """Import der Haltungen aus der STRAKAT-Tabelle KANALTABELLE"""

        sql = """
            WITH
            sto AS (
                SELECT nummer, schacht_unten
                FROM t_strakatkanal
                WHERE schachtnummer <> 0
                GROUP BY schacht_unten
            ),
            profilarten AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'profilart'
            ),
            rohrmaterialien AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'rohrmaterial'
            ),
            strassen AS (
                SELECT n1 AS id, kurz, text AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            entwart AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'kanalart' 
            ),
            knotenart AS (
                SELECT n1 AS id, n4, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'schachtart' 
            ),
            gebiet AS (
                SELECT n1 AS id, text, kurz
                FROM t_reflists
                WHERE tabtyp = 'entwaesserungsgebiet'
            )
            INSERT INTO haltungen (haltnam, schoben, schunten, laenge, 
                xschob, yschob, xschun, yschun, 
                breite, hoehe, 
                sohleoben, sohleunten, 
                profilnam, entwart, druckdicht, material, strasse, teilgebiet,  
                haltungstyp, simstatus, kommentar, geom)
            SELECT
                stk.haltungsname                        AS haltnam,
                Coalesce(
                    sto.schacht_unten,stk.schacht_oben
                    )                                   AS schoben,
                stk.schacht_unten                       AS schunten,
                stk.laenge                              AS laenge,
                stk.rw_gerinne_o                        AS xschob,
                stk.hw_gerinne_o                        AS yschob,
                stk.rw_gerinne_u                        AS xschun,
                stk.hw_gerinne_u                        AS yschun,
                stk.rohrbreite_v/1000.                  AS breite,
                stk.rohrhoehe___v/1000.                 AS hoehe,
                stk.sohle_oben___v                      AS sohleoben,
                stk.sohle_unten__v                      AS sohleunten,
                profilarten.text                        AS profilnam,
                k2e.text                                AS entwart,
                CASE WHEN instr(lower(k2e.text),'druck') > 0
                    THEN 1 ELSE 0 END                   AS druckdicht,
                rohrmaterialien.text                    AS material,
                CASE WHEN INSTR(strassen.name,' ') > 0
                    THEN substr(strassen.name, INSTR(strassen.name,' ')+1)
                    ELSE strassen.name
                END                                     AS strasse,
                k2g.text                                AS teilgebiet,
                'Haltung'                               AS haltungstyp,
                'vorhanden'                             AS simstatus,
                'QKan-STRAKAT-Import'                   AS kommentar,
                MakeLine(MakePoint(stk.rw_gerinne_o,
                                   stk.hw_gerinne_o, :epsg),
                         MakePoint(stk.rw_gerinne_u,
                                   stk.hw_gerinne_u, :epsg)) AS geom
            FROM
                t_strakatkanal AS stk
                LEFT JOIN profilarten
                ON stk.profilart_v = profilarten.id
                LEFT JOIN rohrmaterialien
                ON stk.Material_v = rohrmaterialien.ID
                LEFT JOIN strassen
                ON stk.strassennummer = strassen.ID
                JOIN entwart AS k2e
                ON stk.kanalart = k2e.id
                LEFT JOIN sto
                ON stk.Zuflussnummer1 = sto.Nummer
                JOIN knotenart AS k2t
                ON stk.schachtart = k2t.id
                JOIN gebiet AS k2g
                ON stk.e_gebiet = k2g.id
            WHERE stk.laenge > 0.04
              AND stk.schachtnummer <> 0
              AND stk.schachtart <> 0"""

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import Haltungen (1)", params):
            logger.error('Fehler in strakat_import Haltungen (1)')
            return False

        self.db_qkan.commit()

        # Zusammengesetzte Haltungen werden neu erzeugt und überschreiben das geom-Objekt der jeweiligen Anfanghaltung
        # Erkennungsmerkmal: 1. Kanal hat Schachtart <>0, alle weiteren haben die Schachtart 0.
        # Einschränkung: Als 1. Kanal zählen nur Kanäle, die nicht gemeinsam mit einem anderen Kanal mit schachtart = 0
        # in einen Schacht einleiten. Zusätzlich müssen aufeinander folgende Teile in folgenden Attribute
        # identisch sein: eigentum, kanalart

        def _getstraenge():
            """Liest alle zusammengesetzten Kanäle (Kriterium: schachtart = 0 zuzüglich oberhalb liegendem Kanal)"""
            sql = f"""WITH ko AS (
                        SELECT *
                        FROM t_strakatkanal AS ko
                        LEFT JOIN (SELECT * FROM t_strakatkanal WHERE schachtart = 0) AS k2
                        ON k2.schacht_unten = ko.schacht_unten          -- muendet gemeinsam in einen Schacht
                        WHERE ko.schachtart = 0 OR k2.nummer IS NULL    -- entweder schachtart 0 oder wenn nicht, dann kein paralleler mit schachtart 0
                    )
                    SELECT
                        ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, 
                        ko.haltungsname, ko.schacht_oben, ko.schacht_unten,
                        ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un, 
                        ko.rw_gerinne_o, ko.hw_gerinne_o, ko.rw_gerinne_u, ko.hw_gerinne_u
                        FROM ko
                        JOIN t_strakatkanal AS ku ON ku.schacht_oben = ko.schacht_unten
                        WHERE ko.schachtart = 0
                           OR (ku.schachtart = 0 AND ko.kanalart = ku.kanalart AND ko.eigentum = ku.eigentum)"""

            if not self.db_qkan.sql(sql):
                logger.error('Fehler in strakat_import Haltungen (2)')
                return False

            stnet = self.db_qkan.fetchall()

            idxschob = {ds[3]: ds for ds in stnet}
            idxschun = {ds[4]: ds for ds in stnet}

            # Schleife bis alle Haltungsteilstücke verarbeitet sind
            while len(idxschob) > 0:
                gplis = []  # Knotenpunkte einer zusammengesetzten Haltung
                # Anfang finden
                for anf in idxschob:
                    # Wenn kein Teilstück oberhalb
                    if not idxschun.get(anf):
                        break
                else:
                    raise Exception(f'Fehler: Konnte (mindestens) ein Haltungsteilstück'
                                    f'nicht verarbeiten: Schacht oben = {anf}')
                # Kanal verfolgen und jedes Teilstück entnehmen
                haltnam = idxschob[anf][2]
                node = anf  # Anfang übernehmen
                while True:
                    ds = idxschob[node]
                    gplis.append([ds[7], ds[8]])  # Anfangskoordinate
                    next = idxschob.get(node)[4]  # Schacht unten als nächsten Schacht übernehmen
                    if not idxschob.get(next):
                        # Ende gefunden
                        gplis.append([ds[9], ds[10]])  # Endkoordinate
                        del idxschob[node]
                        break
                    del idxschob[node]
                    node = next

                ptlis = [QgsPoint(x, y) for x, y in gplis]
                geom = QgsGeometry.fromPolyline(ptlis)

                yield haltnam, geom.asWkb()

        for strang_haltnam, strang_wkb in _getstraenge():
            params = {"geom": strang_wkb, "haltnam": strang_haltnam, "epsg": self.epsg}
            sql = f"""UPDATE haltungen SET geom = GeomFromWKB(:geom, :epsg)
                        WHERE haltnam = :haltnam"""
            if not self.db_qkan.sql(sql, "strakat_import Zusammensetzen der Kanalstränge", params):
                return False

        self.db_qkan.commit()

        return True

    def _anschlussleitungen(self) -> bool:
        """Import der STRAKAT-Tabelle anschlussleitungen"""

        sql = """
            WITH lo AS (
                SELECT
                    h.pk, 
                    1 AS n, 
                    Makepoint(x1, y1, :epsg) AS geop
                FROM t_strakathausanschluesse AS h
                UNION 
                SELECT pk, 2 AS n, Makepoint(x2, y2, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x2 > 1
                UNION 
                SELECT pk, 3 AS n, Makepoint(x3, y3, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x3 > 1
                UNION 
                SELECT pk, 4 AS n, Makepoint(x4, y4, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x4 > 1
                UNION 
                SELECT pk, 5 AS n, Makepoint(x5, y5, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x5 > 1
                UNION 
                SELECT pk, 6 AS n, Makepoint(x6, y6, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x6 > 1
                UNION 
                SELECT pk, 7 AS n, Makepoint(x7, y7, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x7 > 1
                UNION 
                SELECT pk, 8 AS n, Makepoint(x8, y8, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x8 > 1
                UNION 
                SELECT pk, 9 AS n, Makepoint(x9, y9, :epsg) AS geop
                FROM t_strakathausanschluesse
                WHERE x9 > 1
            ),
            lp AS (
                SELECT pk, Makeline(geop) AS geom
                FROM lo
                GROUP BY pk
                ORDER BY n
            )
            INSERT INTO anschlussleitungen (leitnam, schoben, schunten, 
                hoehe, breite, laenge,
                simstatus, kommentar, geom)
            SELECT
                CASE WHEN Trim(ha.anschlusshalname) = ''
                THEN
                    CASE WHEN abs(ha.urstation + 1.0) < 0.0001
                    THEN replace(printf('sc_%d', 1000000 + ha.nummer), 'sc_1', 'sc')    -- Schachtanschluss
                    ELSE replace(printf('ha_%d', 1000000 + ha.nummer), 'ha_1', 'ha')    -- Haltungsanschluss
                    END
                ELSE Trim(ha.anschlusshalname)
                END                                 AS leitnam,
                Trim(ha.haschob)                    AS schoben,
                Trim(ha.haschun)                    AS schunten,
                ha.rohrbreite/1000.                 AS hoehe,
                ha.rohrbreite/1000.                 AS breite,
                GLength(lp.geom)                    AS laenge,
                'vorhanden'                         AS simstatus,
                'QKan-STRAKAT-Import'               AS kommentar,
                lp.geom                             AS geom
            FROM
                lp
                JOIN t_strakathausanschluesse AS ha USING (pk)
                JOIN t_strakatkanal AS k ON k.nummer = ha.anschlusshalnr and k.strakatid = ha.strakatid
            WHERE k.schachtnummer <> 0
			GROUP BY ha.pk"""

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import anschlussleitungen", params):
            return False

        self.db_qkan.commit()

        return True

    def _schaechte_untersucht(self) -> bool:
        """Import der Schächte mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        sql = """
        """

        params = {"epsg": self.epsg}
        if not self.db_qkan.sql(sql, "strakat_import Schachtschäden", params):
            return False

        self.db_qkan.commit()

        return True

    def _untersuchdat_schacht(self) -> bool:
        """Import der Schachtschäden aus der STRAKAT-Tabelle t_strakatberichte"""
        pass

    def _haltungen_untersucht(self) -> bool:
        """Import der Haltungen mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        sql = """
            WITH
            sto AS (
                SELECT nummer, schacht_unten
                FROM t_strakatkanal
                WHERE schachtnummer <> 0
            ),
            strassen AS (
                SELECT n1 AS id, kurz, text AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            )
            INSERT INTO haltungen_untersucht (haltnam, schoben, schunten, laenge, 
                xschob, yschob, xschun, yschun, 
                breite, hoehe, 
                strasse, 
                baujahr, untersuchtag, untersucher, 
                wetter,
                bewertungsart, bewertungstag, datenart, 
                max_ZD, max_ZB, max_ZS, 
                kommentar, geom)
            SELECT
                stk.haltungsname                AS haltnam,
                Coalesce(
                    sto.schacht_unten,stk.schacht_oben
                    )                           AS schoben,
                stk.schacht_unten               AS schunten,
                stk.laenge                      AS laenge,
                stk.rw_gerinne_o                AS xschob,
                stk.hw_gerinne_o                AS yschob,
                stk.rw_gerinne_u                AS xschun,
                stk.hw_gerinne_u                AS yschun,
                stk.rohrbreite_v/1000.          AS breite,
                stk.rohrhoehe___v/1000.         AS hoehe,
                CASE WHEN INSTR(strassen.name,' ') > 0
                    THEN substr(strassen.name, INSTR(strassen.name,' ')+1)
                    ELSE strassen.name
                END                             AS strasse,
                stk.baujahr                     AS baujahr,
                stb.datum                       AS untersuchtag,
                stb.untersucher                 AS untersucher,
                CASE WHEN instr(lower(stb.wetter), 'trock') + 
                           instr(lower(stb.wetter), 'kein Nied') > 0 THEN 1
                      WHEN instr(lower(stb.wetter), 'reg')       > 0 THEN 2
                      WHEN instr(lower(stb.wetter), 'fros') +
                           instr(lower(stb.wetter), 'chnee')     > 0 THEN 3
                      ELSE NULL END 		    AS wetter,
                'DWA'                           AS bewertungsart,
                NULL                           AS bewertungstag,
                'DWA'                           AS datenart,
                stb.skdichtheit                 AS max_ZD,
                stb.skbetriebssicherheit        AS max_ZB,
                stb.skstandsicherheit           AS max_ZS,
                'QKan-STRAKAT-Import'                   AS kommentar,
                MakeLine(MakePoint(stk.rw_gerinne_o,
                                   stk.hw_gerinne_o, :epsg),
                         MakePoint(stk.rw_gerinne_u,
                                   stk.hw_gerinne_u, :epsg)) AS geom
            FROM
                t_strakatkanal AS stk
                LEFT JOIN Strassen ON stk.strassennummer = Strassen.ID
                LEFT JOIN sto ON stk.Zuflussnummer1 = sto.Nummer
                JOIN t_strakatberichte AS stb ON stb.strakatid = stk.strakatid
            WHERE stk.laenge > 0.04 AND
                   stk.schachtnummer <> 0
            GROUP BY stk.strakatid, stb.datum
        """

        params = {"epsg": self.epsg}
        if not self.db_qkan.sql(sql, "strakat_import untersuchte Haltungen", params):
            return False

        self.db_qkan.commit()

        return True

    def _untersuchdat_haltung(self) -> bool:
        """Import der Haltungsschäden aus der STRAKAT-Tabelle t_strakatberichte"""

        sql =  """
            WITH
            sto AS (
                SELECT nummer, schacht_unten
                FROM t_strakatkanal
                WHERE schachtnummer <> 0
            )
            INSERT INTO untersuchdat_haltung (
                untersuchhal, schoben, schunten,
                id, untersuchtag, untersuchrichtung,
                inspektionslaenge, bandnr, videozaehler, station, timecode,
                kuerzel, charakt1, charakt2, quantnr1, quantnr2,
                streckenschaden, streckenschaden_lfdnr,
                pos_von, pos_bis,
                foto_dateiname, film_dateiname, ordner_bild, ordner_video,
                kommentar, ZD, ZB, ZS
            )
            SELECT
                stk.haltungsname                AS untersuchhal,
                Coalesce(
                    sto.schacht_unten,stk.schacht_oben
                    )                           AS schoben,
                stk.schacht_unten               AS schunten,
                NULL                            AS id, 
                stb.datum                       AS untersuchtag,
                CASE stb.untersuchungsrichtung
                WHEN 0 THEN 'gegen Fließrichtung'
                WHEN 1 THEN 'in Fließrichtung'
                ELSE NULL END                   AS untersuchrichtung, 
                stk.laenge                      AS inspektionslaenge,
                stb.bandnr                      AS bandnr,
                printf('%02u:%02u:%02u', 
                    (videozaehler % 1000000 - (videozaehler % 10000)) / 10000 % 60, 
                    (videozaehler % 10000 - (videozaehler % 100)) / 100 % 60, 
                    videozaehler % 100 % 60)    AS videozaehler,
                stb.station_untersucher         AS station,
                NULL                            AS timecode,
                stb.atv_kuerzel                 AS kuerzel,
                stb.charakt1                    AS charakt1,
                stb.charakt2                    AS charakt2,                
                stb.quantnr1                    AS quantnr1,
                stb.quantnr2                    AS quantnr2,                
                stb.streckenschaden             AS streckenschaden,
                stb.fortsetzung                 AS streckenschadenlfdnr,
                stb.pos_von                     AS pos_von, 
                stb.pos_bis                     AS pos_bis,
                NULL                            AS foto_dateiname,
                NULL                            AS film_dateiname,
                NULL                            AS ordner_bild,
                NULL                            AS ordner_video,
                kommentar                       AS kommentar,        -- Kombi aus STRAKAT-Feldern Sanierung + Anmerkung
                stb.skdichtheit                 AS ZD,
                stb.skbetriebssicherheit        AS ZB,
                stb.skstandsicherheit           AS ZS
            FROM
                t_strakatkanal AS stk
                LEFT JOIN sto
                ON stk.Zuflussnummer1 = sto.Nummer
                JOIN t_strakatberichte AS stb
                ON stb.strakatid = stk.strakatid
            WHERE stk.laenge > 0.04 AND stk.schachtnummer <> 0 AND stb.hausanschlid = '00000000-0000-0000-0000-000000000000'
        """

        if not self.db_qkan.sql(sql, "strakat_import Haltungsschäden"):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Haltungsschäden")

        self.db_qkan.commit()

        self.db_qkan.setschadenstexte()

