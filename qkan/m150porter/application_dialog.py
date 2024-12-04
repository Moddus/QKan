import os
from typing import Callable, Optional, List

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QDialogButtonBox,
)

from qkan import QKan, enums, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

logger = get_logger("QKan.he8.application_dialog")

EXPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "xml_export_dialog_base.ui")
)


class _Dialog(QDialog):
    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)
        self.default_dir = str(default_dir)
        self.tr = tr


class ExportDialog(_Dialog, EXPORT_CLASS):  # type: ignore
    button_box: QDialogButtonBox
    tf_database: QLineEdit
    tf_export: QLineEdit

    pb_database: QPushButton
    pb_export: QPushButton

    cb_export_schaechte: QCheckBox
    cb_export_auslaesse: QCheckBox
    cb_export_speicher: QCheckBox
    cb_export_haltungen: QCheckBox
    cb_export_pumpen: QCheckBox
    cb_export_wehre: QCheckBox
    cb_export_anschlussleitungen: QCheckBox

    cb_selectedTgbs: QCheckBox
    lw_teilgebiete: QListWidget

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_export.clicked.connect(self.select_export)

        self.button_box.helpRequested.connect(self.click_help)

        # Aktionen zu lw_teilgebiete: QListWidget
        self.cb_selectedTgbs.stateChanged.connect(self.click_selection)
        # self.lw_teilgebiete.itemClicked.connect(self.count_selection)      # ist schon in click_lw_teilgebiete enthalten
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_export.setText(QKan.config.xml.export_file)
        self.cb_export_schaechte.setChecked(
            getattr(QKan.config.check_export, "export_schaechte", True)
        )
        self.cb_export_auslaesse.setChecked(
            getattr(QKan.config.check_export, "export_auslaesse", True)
        )
        self.cb_export_speicher.setChecked(
            getattr(QKan.config.check_export, "export_speicher", True)
        )
        self.cb_export_haltungen.setChecked(
            getattr(QKan.config.check_export, "export_haltungen", True)
        )
        self.cb_export_anschlussleitungen.setChecked(
            getattr(QKan.config.check_export, "export_anschlussleitungen", True)
        )
        self.cb_export_pumpen.setChecked(
            getattr(QKan.config.check_export, "export_pumpen", True)
        )
        self.cb_export_wehre.setChecked(
            getattr(QKan.config.check_export, "export_wehre", True)
        )


    def select_export(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende XML-Datei"),
            self.default_dir,
            "*.xml",
        )
        if filename:
            self.tf_export.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def click_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selectedTgbs.isChecked():
            # Nix tun ...
            logger.debug("\nChecked = True")
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_teilgebiete.count()
            for i in range(anz):
                item = self.lw_teilgebiete.item(i)
                item.setSelected(False)
                # self.lw_teilgebiete.setItemSelected(item, False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def click_lw_teilgebiete(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selectedTgbs.setChecked(True)
        self.count_selection()

    def count_selection(self) -> bool:
        """ Zählung mit Herstellung der Datenbankverbindung
        """
        with DBConnection() as db_qkan:
            self.count(db_qkan)

    def count(self, db_qkan: DBConnection) -> bool:
        """ Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
            der betroffenen Flächen und Haltungen
        """
        teilgebiete: List[str] = list_selected_items(self.lw_teilgebiete)
        # teilgebiete: List[str] = []        # Todo: wieder aktivieren

        # Zu berücksichtigende Flächen zählen
        auswahl = ""
        if len(teilgebiete) != 0:
            auswahl = " WHERE flaechen.teilgebiet in ('{}')".format(
                "', '".join(teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM flaechen {auswahl}"

        if not db_qkan.sql(sql, "QKan_ExportHE.application.countselection (1)"):
            return False
        daten = db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.lf_anzahl_flaechen.setText("0")

        # Zu berücksichtigende Schächte zählen
        auswahl = ""
        if len(teilgebiete) != 0:
            auswahl = " WHERE schaechte.teilgebiet in ('{}')".format(
                "', '".join(teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM schaechte {auswahl}"
        if not db_qkan.sql(sql, "QKan_ExportHE.application.countselection (2) "):
            return False
        daten = db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_schaechte.setText(str(daten[0]))
        else:
            self.lf_anzahl_schaechte.setText("0")

        # Zu berücksichtigende Haltungen zählen
        auswahl = ""
        if len(teilgebiete) != 0:
            auswahl = " WHERE haltungen.teilgebiet in ('{}')".format(
                "', '".join(teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM haltungen {auswahl}"
        if not db_qkan.sql(sql, "QKan_ExportHE.application.countselection (3) "):
            return False
        daten = db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.lf_anzahl_haltungen.setText("0")
        return True

    def prepareDialog(self, db_qkan: DBConnection) -> bool:
        """Füllt Auswahllisten im Export-Dialog"""

        # Alle Teilgebiete in Flächen, Schächten und Haltungen, die noch nicht in Tabelle "teilgebiete" enthalten
        # sind, ergänzen

        sql = """WITH tgb AS (
                SELECT teilgebiet FROM flaechen
                WHERE teilgebiet IS NOT NULL
                UNION
                SELECT teilgebiet FROM haltungen
                WHERE teilgebiet IS NOT NULL
                UNION
                SELECT teilgebiet FROM schaechte
                WHERE teilgebiet IS NOT NULL
                )
                INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM tgb
                WHERE teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not db_qkan.sql(sql, "he8porter.application_dialog.connectQKanDB (1) "):
            return False

        db_qkan.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        teilgebiete = QKan.config.selections.teilgebiete

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not db_qkan.sql(sql, "he8porter.application_dialog.connectQKanDB (4) "):
            return False
        daten = db_qkan.fetchall()
        self.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in teilgebiete:
                    self.lw_teilgebiete.setCurrentRow(ielem)
            except BaseException as err:
                fehlermeldung = "he8porter.application_dialog.connectQKanDB, " + \
                        f"Fehler {repr(err)} in elem = {elem}\n"
                logger.error(fehlermeldung)
                raise Exception(f"{self.__class__.__name__}: {fehlermeldung}")

        # Initialisierung der Anzeige der Anzahl zu exportierender Objekte
        self.count(db_qkan)

        return True

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_XML.html#import-aus-dwa-xml"
        os.startfile(help_file)


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "xml_import_dialog_base.ui")
)


class ImportDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_database: QPushButton
    pb_import: QPushButton
    pb_project: QPushButton

    pb_ordnerbild: QPushButton
    tf_ordnerbild: QLineEdit

    pb_ordnervideo: QPushButton
    tf_ordnervideo: QLineEdit

    cb_import_tabinit: QCheckBox

    epsg: QgsProjectionSelectionWidget

    checkBox: QCheckBox
    checkBox_2: QCheckBox
    checkBox_3: QCheckBox

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_import.clicked.connect(self.select_import)
        self.pb_ordnerbild.clicked.connect(self.select_ordnerbild)
        self.pb_ordnervideo.clicked.connect(self.select_ordnervideo)
        self.pb_project.clicked.connect(self.select_project)
        self.pb_database.clicked.connect(self.select_database)

        self.button_box.helpRequested.connect(self.click_help)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.xml.import_file)
        self.tf_ordnerbild.setText(QKan.config.xml.ordner_bild)
        self.tf_ordnervideo.setText(QKan.config.xml.ordner_video)
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_project.setText(QKan.config.project.file)

        self.checkBox.setChecked(
            getattr(QKan.config.xml, "import_stamm", True)
        )

        self.checkBox_2.setChecked(
            getattr(QKan.config.xml, "import_haus", True)
        )

        self.checkBox_3.setChecked(
            getattr(QKan.config.xml, "import_zustand", True)
        )

    def select_import(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende XML-Datei"),
            self.default_dir,
            "*.xml",
        )
        if filename:
            self.tf_import.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def select_ordnerbild(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        ordner_bild = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner Pfad"),
            self.default_dir,
        )
        if ordner_bild:
            self.tf_ordnerbild.setText(ordner_bild)
            self.default_dir = os.path.dirname(ordner_bild)

    def select_ordnervideo(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        ordner_video = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner Pfad"),
            self.default_dir,
        )
        if ordner_video:
            self.tf_ordnervideo.setText(ordner_video)
            self.default_dir = os.path.dirname(ordner_video)

    def select_project(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende Projektdatei"),
            self.default_dir,
            "*.qgs",
        )
        if filename:
            self.tf_project.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def select_database(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende SQLite-Datei"),
            self.default_dir,
            "*.sqlite",
        )
        if filename:
            self.tf_database.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_XML.html#import-aus-dwa-xml"
        os.startfile(help_file)
