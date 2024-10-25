import os

from qgis.utils import spatialite_connect

from qkan.utils import get_logger

from qgis.core import (
    Qgis,
    QgsProject,
    QgsVectorLayer,
    QgsDataSourceUri,
)
from qgis.utils import iface, spatialite_connect

logger = get_logger("QKan.tools.k_filepath")


def setfilepath(
    db,
    videopath,
    fotopath,
    fotopath_2,
    ausw_haltung,
    ausw_schacht,
) -> None:
    """Schreibt die Dateipfade in die Datenbank.
    """

    db = spatialite_connect(db)
    curs = db.cursor()

    if ausw_haltung == True:
        bild=''
        video = ''
        if fotopath != "":
            #Bild suchen
            # ordner und dateiname aus datenbank abfragen

            sql = """select pk, foto_dateiname, ordner_bild 
                        from untersuchdat_haltung"""
            try:
                curs.execute(sql)
            except BaseException as err:
                return False


            for attr in curs.fetchall():

                #pfad+name = attr[1]
                #nur name =

                #fotopath, bild_nam = attr[1]


                bild_nam = os.path.basename(attr[1])

                for root, dirs, files in os.walk(fotopath):
                    for file in files:
                        if file.lower() == bild_nam.lower():
                            bild = str(fotopath) + '/' + str(bild_nam)

                            # pfad in db erstzen
                            sql = """Update untersuchdat_haltung set foto_dateiname = ?
                                                WHERE untersuchdat_haltung.pk = ?;"""
                            data = (str(bild), attr[0])

                            try:
                                curs.execute(sql, data)
                            except BaseException as err:
                                return False

            db.commit()

        if videopath != "":

            #Video suchen
            sql = """select pk, film_dateiname, ordner_video
                                from untersuchdat_haltung"""
            try:
                #curs.sql(sql)
                curs.execute(sql)
            except BaseException as err:
                return False

            for attr in curs.fetchall():
                #video_nam = attr[1]

                video_nam = os.path.basename(attr[1])

                for root, dirs, files in os.walk(videopath):
                    for file in files:
                        if file.lower() == video_nam.lower():
                            video = str(videopath)+'/'+str(video_nam)

                            # ordner_video in db ersetzen
                            sql = """Update untersuchdat_haltung set film_dateiname = ?
                                                    WHERE untersuchdat_haltung.pk = ?;"""
                            data = (video, attr[0])

                            try:
                                curs.execute(sql, data)
                            except BaseException as err:
                                return False
            db.commit()


    if ausw_schacht == True and fotopath_2 != "":
        bild = ''

        #ordner und dateiname aus datenbank abfragen
        sql = """select pk, foto_dateiname, ordner 
                    from untersuchdat_schacht"""
        try:
            #curs.sql(sql)
            curs.execute(sql)
        except BaseException as err:
            return False


        for attr in curs.fetchall():
            #bild_nam = attr[1]

            bild_nam = os.path.basename(attr[1])

            iface.messageBar().pushMessage("Error",
                                           "Name: " + str(bild_nam),
                                           level=Qgis.Critical)

            for root, dirs, files in os.walk(fotopath_2):
                for file in files:
                    if file.lower() == bild_nam.lower():
                        bild = fotopath_2+file

                        # pfad in db erstzen
                        sql = """Update untersuchdat_schacht set foto_dateiname = ?
                                            WHERE untersuchdat_schacht.pk = ?;"""
                        data = (bild, attr[0])

                        try:
                            curs.execute(sql, data)
                        except BaseException as err:
                            return False


        db.commit()
