import os
import typing

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QCheckBox, QDialog, QFileDialog, QLineEdit, QPushButton
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget

from qkan import QKan

EXPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "he8_export_dialog_base.ui")
)


class _Dialog(QDialog):
    def __init__(self, default_dir: os.PathLike, tr: typing.Callable, parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)
        self.default_dir = str(default_dir)
        self.tr = tr


class ExportDialog(_Dialog, EXPORT_CLASS):
    tf_database: QLineEdit
    tf_export: QLineEdit
    tf_template: QLineEdit

    pb_database: QPushButton
    pb_export: QPushButton

    cb_export_schaechte: QCheckBox
    cb_export_auslaesse: QCheckBox
    cb_export_speicher: QCheckBox
    cb_export_haltungen: QCheckBox
    cb_export_pumpen: QCheckBox
    cb_export_wehre: QCheckBox

    def __init__(self, default_dir: os.PathLike, tr: typing.Callable, parent=None):
        # noinspection PyArgumentList
        super().__init__(default_dir, tr, parent)
        self.setupUi(self)

        # Attach events
        self.pb_database.clicked.connect(self.select_database)
        self.pb_export.clicked.connect(self.select_export)
        self.pb_template.clicked.connect(self.select_template)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_export.setText(QKan.config.he8.export_file)
        self.tf_template.setText(QKan.config.he8.export_file)
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
        self.cb_export_pumpen.setChecked(
            getattr(QKan.config.check_export, "export_pumpen", True)
        )
        self.cb_export_wehre.setChecked(
            getattr(QKan.config.check_export, "export_wehre", True)
        )

    def select_database(self):
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende SQLite-Datei"),
            self.default_dir,
            "*.sqlite",
        )

        if filename:
            self.tf_database.setText(filename)

    def select_template(self):
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self, self.tr("Vorlage für die zu erstellende HE8-Datei"), self.default_dir, "*.idbm",
        )
        if filename:
            self.tf_template.setText(filename)

    def select_export(self):
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self, self.tr("Zu erstellende HE8-Datei"), self.default_dir, "*.idbm",
        )
        if filename:
            self.tf_export.setText(filename)


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "he8_import_dialog_base.ui")
)


class ImportDialog(_Dialog, IMPORT_CLASS):
    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_database: QPushButton
    pb_import: QPushButton
    pb_project: QPushButton

    # cb_import_tabinit: QCheckBox

    epsg: QgsProjectionSelectionWidget

    def __init__(self, default_dir: os.PathLike, tr=typing.Callable, parent=None):
        # noinspection PyArgumentList
        super().__init__(default_dir, tr, parent)
        self.setupUi(self)

        # Attach events
        self.pb_import.clicked.connect(self.select_import)
        self.pb_project.clicked.connect(self.select_project)
        self.pb_database.clicked.connect(self.select_database)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.he8.import_file)
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        # self.cb_import_tabinit.setChecked(QKan.config.he8.init_database)
        self.tf_project.setText(QKan.config.project.file)

    def select_import(self):
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getOpenFileName(
            self, self.tr("Zu importierende HE8-Datei"), self.default_dir, "*.idbm",
        )
        if filename:
            self.tf_import.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def select_project(self):
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self, self.tr("Zu erstellende Projektdatei"), self.default_dir, "*.qgs",
        )
        if filename:
            self.tf_project.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def select_database(self):
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self, self.tr("Zu erstellende SQLite-Datei"), self.default_dir, "*.sqlite",
        )
        if filename:
            self.tf_database.setText(filename)
            self.default_dir = os.path.dirname(filename)
