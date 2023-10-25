import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from qkan import QKan, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from ._export import ExportTask
from ._import import ImportTask
from .application_dialog import ExportDialog, ImportDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip

logger = logging.getLogger("QKan.he8.application")


class MuPorter(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"MuPorter: default_dir: {default_dir}")
        self.export_dlg = ExportDialog(default_dir, tr=self.tr)
        self.import_dlg = ImportDialog(default_dir, tr=self.tr)

        self.db_name: Optional[str] = None

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/mu_porter/res/icon_import.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus Mike+"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.export_dlg.close()
        self.import_dlg.close()

    @property
    def database_name(self) -> str:
        """Contains the database name"""
        if self.db_name:
            return self.db_name

        self.db_name, _ = get_database_QKan()
        return self.db_name

    def run_export(self) -> None:
        """Anzeigen des Exportformulars und anschließender Start des Exports in eine Mike+-Datenbank"""

        # noinspection PyArgumentList

        # Datenbankpfad in Dialog übernehmen
        self.export_dlg.tf_database.setText(self.database_name)

        if self.database_name is None:
            fehlermeldung("Fehler: Für diese Funktion muss ein Projekt geladen sein!")
            return

        if not self.export_dlg.prepareDialog():
            return

        # Formular anzeigen
        self.export_dlg.show()

        # Im Formular wurde [OK] geklickt
        if self.export_dlg.exec_():

            # Read from form and save to config
            QKan.config.mu.database = self.export_dlg.tf_database.text()
            QKan.config.mu.export_file = self.export_dlg.tf_exportdb.text()
            QKan.config.mu.template = self.export_dlg.tf_template.text()

            QKan.config.check_export.haltungen = (
                self.export_dlg.cb_haltungen.isChecked()
            )
            QKan.config.check_export.schaechte = (
                self.export_dlg.cb_schaechte.isChecked()
            )
            QKan.config.check_export.auslaesse = (
                self.export_dlg.cb_auslaesse.isChecked()
            )
            QKan.config.check_export.speicher = self.export_dlg.cb_speicher.isChecked()
            QKan.config.check_export.pumpen = self.export_dlg.cb_pumpen.isChecked()
            QKan.config.check_export.wehre = self.export_dlg.cb_wehre.isChecked()
            QKan.config.check_export.flaechen = self.export_dlg.cb_flaechen.isChecked()
            QKan.config.check_export.rohrprofile = (
                self.export_dlg.cb_rohrprofile.isChecked()
            )
            QKan.config.check_export.abflussparameter = (
                self.export_dlg.cb_abflussparameter.isChecked()
            )
            QKan.config.check_export.bodenklassen = (
                self.export_dlg.cb_bodenklassen.isChecked()
            )
            QKan.config.check_export.einleitdirekt = (
                self.export_dlg.cb_einleitdirekt.isChecked()
            )
            QKan.config.check_export.aussengebiete = (
                self.export_dlg.cb_aussengebiete.isChecked()
            )
            QKan.config.check_export.einzugsgebiete = (
                self.export_dlg.cb_einzugsgebiete.isChecked()
            )
            QKan.config.check_export.tezg = self.export_dlg.cb_tezg.isChecked()

            QKan.config.check_export.append = self.export_dlg.rb_append.isChecked()
            QKan.config.check_export.update = self.export_dlg.rb_update.isChecked()

            teilgebiete = [
                _.text() for _ in self.export_dlg.lw_teilgebiete.selectedItems()
            ]
            QKan.config.selections.teilgebiete = teilgebiete

            QKan.config.save()

            self._doexport()

    def _doexport(self) -> bool:
        """Start des Export in eine HE8-Datenbank

        Einspringpunkt für Test
        """

        # Zieldatenbank aus Vorlage kopieren
        if os.path.exists(QKan.config.mu.template):
            try:
                shutil.copyfile(QKan.config.mu.template, QKan.config.mu.export_file)
            except BaseException:
                fehlermeldung(
                    "Fehler in Export nach Mike+",
                    "Fehler beim Kopieren der Vorlage: \n   {QKan.config.mu.template}\n"
                    + "nach Ziel: {QKan.config.mu.export_file}\n",
                )

        self.export_dlg.connectMUDB(QKan.config.mu.export_file)

        # Run export
        ExportTask(self.export_dlg.db_qkan, QKan.config.selections.teilgebiete).run()

        # Close connection
        del self.export_dlg.db_qkan
        self.log.debug("Closed DB")

        return True

    def run_import(self) -> None:
        """Anzeigen des Importformulars Mike+ und anschließender Start des Import aus einer Mike+-Datenbank"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.mu.database = self.import_dlg.tf_database.text()
            QKan.config.project.file = self.import_dlg.tf_project.text()
            QKan.config.mu.import_file = self.import_dlg.tf_import.text()

            QKan.config.check_import.haltungen = (
                self.import_dlg.cb_haltungen.isChecked()
            )
            QKan.config.check_import.schaechte = (
                self.import_dlg.cb_schaechte.isChecked()
            )
            QKan.config.check_import.auslaesse = (
                self.import_dlg.cb_auslaesse.isChecked()
            )
            QKan.config.check_import.speicher = self.import_dlg.cb_speicher.isChecked()
            QKan.config.check_import.pumpen = self.import_dlg.cb_pumpen.isChecked()
            QKan.config.check_import.wehre = self.import_dlg.cb_wehre.isChecked()
            QKan.config.check_import.flaechen = self.import_dlg.cb_flaechen.isChecked()
            QKan.config.check_import.rohrprofile = (
                self.import_dlg.cb_rohrprofile.isChecked()
            )
            QKan.config.check_import.abflussparameter = (
                self.import_dlg.cb_abflussparameter.isChecked()
            )
            QKan.config.check_import.bodenklassen = (
                self.import_dlg.cb_bodenklassen.isChecked()
            )
            QKan.config.check_import.einleitdirekt = (
                self.import_dlg.cb_einleitdirekt.isChecked()
            )
            QKan.config.check_import.aussengebiete = (
                self.import_dlg.cb_aussengebiete.isChecked()
            )
            QKan.config.check_import.einzugsgebiete = (
                self.import_dlg.cb_einzugsgebiete.isChecked()
            )

            # QKan.config.check_import.tezg_ef = self.import_dlg.cb_tezg_ef.isChecked()
            QKan.config.check_import.tezg_hf = self.import_dlg.cb_tezg_hf.isChecked()
            # QKan.config.check_import.tezg_tf = self.import_dlg.cb_tezg_tf.isChecked()

            QKan.config.check_import.append = self.import_dlg.rb_append.isChecked()
            QKan.config.check_import.update = self.import_dlg.rb_update.isChecked()

            crs: QgsCoordinateReferenceSystem = self.import_dlg.pw_epsg.crs()

            try:
                epsg = int(crs.postgisSrid())
            except ValueError:
                # TODO: Reporting this to the user might be preferable
                self.log.exception(
                    "Failed to parse selected CRS %s\nauthid:%s\n"
                    "description:%s\nproj:%s\npostgisSrid:%s\nsrsid:%s\nacronym:%s",
                    crs,
                    crs.authid(),
                    crs.description(),
                    crs.findMatchingProj(),
                    crs.postgisSrid(),
                    crs.srsid(),
                    crs.ellipsoidAcronym(),
                )
            else:
                # TODO: This should all be run in a QgsTask to prevent the main
                #  thread/GUI from hanging. However this seems to either not work
                #  or crash QGIS currently. (QGIS 3.10.3/0e1f846438)
                QKan.config.epsg = epsg

            QKan.config.save()

            if not QKan.config.mu.import_file:
                fehlermeldung("Fehler beim Import", "Es wurde keine Datei ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde keine Datei ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                self._doimport()

    def _doimport(self) -> bool:
        """Start des Import aus einer HE8-Datenbank

        Einspringpunkt für Test
        """

        self.log.info("Creating DB")
        with DBConnection(dbname=QKan.config.mu.database, epsg=QKan.config.epsg) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung(
                    "Fehler im Mike+-Import",
                    f"QKan-Datenbank {QKan.config.mu.database} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im Mike+-Import",
                    f"QKan-Datenbank {QKan.config.mu.database} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )
                return False

            # Attach SQLite-Database with Mike+ Data
            sql = f'ATTACH DATABASE "{QKan.config.mu.import_file}" AS mu'
            if not db_qkan.sql(sql, "MuPorter.run_import_to_mu Attach Mike+"):
                logger.error(
                    f"Fehler in MUPorter._doimport(): Attach fehlgeschlagen: {QKan.config.mu.import_file}"
                )
                return False

            self.log.info("DB creation finished, starting importer")
            imp = ImportTask(db_qkan)
            imp.run()
            del imp

            # Write and load new project file, only if new project
            if QgsProject.instance().fileName() == '':
                QKan.config.project.template = str(
                    Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
                )
                qgsadapt(
                    QKan.config.mu.database,
                    db_qkan,
                    QKan.config.project.file,
                    QKan.config.project.template,
                    QKan.config.epsg,
                )

                # Load generated project
                # noinspection PyArgumentList
                project = QgsProject.instance()
                project.read(QKan.config.project.file)
                project.reloadAllLayers()

                # TODO: Some layers don't have a valid EPSG attached or wrong coordinates

        self.log.debug("Closed DB")

        return True
