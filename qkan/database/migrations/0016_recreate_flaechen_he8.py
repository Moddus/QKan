from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.0.8"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    sqllis = [
        "SELECT DiscardGeometryColumn('flaechen_he8', 'geom')",
        "DROP TABLE flaechen_he8;",
        """
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
            Kommentar TEXT
        )
        """,
        "SELECT AddGeometryColumn('flaechen_he8','Geometry', -1,'MULTIPOLYGON',2)",
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.8-1)"):
            return False

    dbcon.commit()
    return True
