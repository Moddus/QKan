# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Callable, List, Optional, cast
from qgis.core import Qgis
import qgis
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QStandardPaths, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QListWidget, QMenu, QMenuBar, QWidget
from qgis.core import QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from .config import Config
from .utils import QgisPanelLogger

# Toggle in DEV to log to console
LOG_TO_CONSOLE = False


# noinspection PyPep8Naming
def classFactory(iface: QgisInterface) -> "QKan":  # pylint: disable=invalid-name
    qkan = QKan(iface)
    return qkan


class _ExternalQKanPlugin:
    """
    Used as an internal type for external extensions to QKan
    """

    name = __name__
    instance: "_ExternalQKanPlugin"
    plugins: List

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        pass

    def unload(self) -> None:
        pass


class QKan:
    instance: "QKan"
    config: Config
    template_dir: str
    forms: str

    def __init__(self, iface: qgis.gui.QgisInterface):
        QKan.instance = self

        # Init logging
        self.logger = logging.getLogger("QKan")
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.log_path = Path(tempfile.gettempdir()) / "QKan_{}.log".format(
            datetime.datetime.today().strftime("%Y-%m-%d")
        )
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        qgis_handler = QgisPanelLogger()
        qgis_handler.setFormatter(
            logging.Formatter(
                fmt="%(name)s - %(message)s",
            )
        )
        qgis_handler.setLevel(logging.INFO)

        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(qgis_handler)

        if LOG_TO_CONSOLE:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(stream_handler)

        # Init config
        try:
            QKan.config = Config.load()
        except (json.JSONDecodeError, OSError):
            self.logger.error("Failed to read config file.", exc_info=True)
            QKan.config = Config()
            QKan.config.save()

        # QGIS
        self.iface = iface
        self.actions: List[QAction] = []

        # Set default template directory
        QKan.template_dir = os.path.join(pluginDirectory("qkan"), "templates")

        # Set list of QKan-Forms
        forms_dir = os.path.join(pluginDirectory("qkan"), "forms")
        QKan.forms = [
            el for el in os.listdir(forms_dir) if os.path.splitext(el)[1] == ".ui"
        ]
        # self.logger.debug(f"forms_dir: {forms_dir}")
        # self.logger.debug(f"Formularliste: \n{QKan.forms}")

        # Plugins
        self.instances: List[_ExternalQKanPlugin] = []

        # Translations
        self.translator = QTranslator()
        locale = (QSettings().value("locale/userLocale") or "en")[0:2]
        for _file in (Path(__file__).parent / "i18n").iterdir():
            if _file.name.endswith("_{}.qm".format(locale)):
                self.translator.load(str(_file))
        # noinspection PyArgumentList
        QCoreApplication.installTranslator(self.translator)

        from .createunbeffl import CreateUnbefFl
        from .he8porter import He8Porter
        from .dynaporter import DynaPorter
        from .muporter import MuPorter
        from .swmmporter import SWMMPorter
        from .strakatporter import StrakatPorter
        from .linkflaechen import LinkFl
        from .surfaceTools import SurfaceTools
        from .isyporter import IsyPorter
        from .m145porter import M145Porter
        # from .ganglinienhe8 import GanglinienHE8
        from .datacheck import Plausi
        from .zustandsklassen import zustandsklassen
        from .sanierungsbedarfszahl import sanierungsbedarfszahl
        from .laengsschnitt import Laengsschnitt
        from .floodTools import FloodTools
        from .tools import QKanTools
        from .info import Infos

        self.plugins: List = [
            CreateUnbefFl(iface),
            He8Porter(iface),
            DynaPorter(iface),
            MuPorter(iface),
            SWMMPorter(iface),
            StrakatPorter(iface),
            LinkFl(iface),
            SurfaceTools(iface),
            IsyPorter(iface),
            M145Porter(iface),
            # GanglinienHE8(iface),
            Plausi(iface),
            zustandsklassen(iface),
            sanierungsbedarfszahl(iface),
            Laengsschnitt(iface),
            FloodTools(iface),
            QKanTools(iface),
            Infos(iface),
        ]

        actions = cast(QMenuBar, self.iface.mainWindow().menuBar()).actions()

        self.menu: Optional[QMenu] = None
        for menu in actions:
            if menu.text() == "QKan":
                self.menu = menu.menu()
                self.menu_action = menu
                break

        #mnuSub1 = self.menu.addMenu('Sub-menu')

        self.toolbar = self.iface.addToolBar("QKan")
        self.toolbar.setObjectName("QKan")

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        # Create and insert QKan menu after the 3rd menu
        if self.menu is None:
            self.menu = QMenu("QKan", self.iface.mainWindow().menuBar())

            actions = self.iface.mainWindow().menuBar().actions()
            prepend = actions[3] if len(actions) > 3 else None

            self.menu_action = (
                self.iface.mainWindow().menuBar().insertMenu(prepend, self.menu)
            )

        # Calls initGui on all known QKan plugins
        for plugin in self.plugins:
            plugin.initGui()

        self.sort_actions()

    def sort_actions(self) -> None:
        # Finally sort all actions
        self.actions.sort(key=lambda x: cast(str, cast(QAction, x).text().lower()))
        alis={}
        e=0
        for x in self.actions:
            alis[x.text()] = e
            e+=1

        if self.menu:
            self.menu.clear()
            allgemein = self.menu.addMenu("Allgemein")
            verwaltung = self.menu.addMenu("Verwaltung")
            daten = self.menu.addMenu("Daten")
            hyex = self.menu.addMenu("Hystem-Extran")
            xml = self.menu.addMenu("XML")
            dyna = self.menu.addMenu("DYNA")
            mike = self.menu.addMenu("Mike+")
            swmm = self.menu.addMenu("SWMM")
            strakat = self.menu.addMenu("STRAKAT")
            flaechen = self.menu.addMenu("Flächenverabeitung")
            zustand = self.menu.addMenu("Zustandsbewertung")
            flood2D = self.menu.addMenu("Überflutung")
            info = self.menu.addMenu("Info")

            allgemein.addAction(self.actions[alis['Allgemeine Optionen']])
            allgemein.addAction(self.actions[alis['QKan-Projekt aktualisieren']])
            allgemein.addAction(self.actions[alis['Projektdatei auf bestehende QKan-Datenbank übertragen']])
            verwaltung.addAction(self.actions[alis['QKan-Datenbank aktualisieren']])
            verwaltung.addAction(self.actions[alis['Neue QKan-Datenbank erstellen']])
            daten.addAction(self.actions[alis['Plausibilitätsprüfungen']])
            daten.addAction(self.actions[alis['Tabellendaten aus Clipboard einfügen']])
            daten.addAction(self.actions[alis['Tabellendaten aus Clipboard: Zuordnung anzeigen']])
            daten.addAction(self.actions[alis['Laengsschnitt']])
            flaechen.addAction(self.actions[alis['Erzeuge unbefestigte Flächen...']])
            flaechen.addAction(self.actions[alis['Erzeuge Voronoiflächen zu Haltungen']])
            flaechen.addAction(self.actions[alis['Entferne Überlappungen']])
            flaechen.addAction(self.actions[alis['Alle Elemente des Entwässerungsnetzes zu Teilgebiet zuordnen']])
            flaechen.addAction(self.actions[alis['Teilgebietszuordnungen als Gruppen verwalten']])
            flaechen.addAction(self.actions[alis['Erzeuge Verknüpfungslinien von Direkteinleitungen zu Haltungen']])
            flaechen.addAction(self.actions[alis['Erzeuge Verknüpfungslinien von Flächen zu Haltungen']])
            flaechen.addAction(self.actions[alis['Verknüpfungen bereinigen']])
            flaechen.addAction(self.actions[alis['Oberflächenabflussparameter eintragen']])
            hyex.addAction(self.actions[alis['Import aus Hystem-Extran 8']])
            hyex.addAction(self.actions[alis['Export nach Hystem-Extran 8']])
            hyex.addAction(self.actions[alis['Ergebnisse aus Hystem-Extran 8']])
            mike.addAction(self.actions[alis['Import aus Mike+']])
            dyna.addAction(self.actions[alis['Import aus DYNA-Datei (*.EIN)']])
            dyna.addAction(self.actions[alis['Export in DYNA-Datei...']])
            xml.addAction(self.actions[alis['Import aus DWA-XML']])
            xml.addAction(self.actions[alis['Import aus ISYBAU-XML']])
            xml.addAction(self.actions[alis['Export nach ISYBAU-XML']])
            swmm.addAction(self.actions[alis['Import von SWMM-Datei (*.INP)']])
            swmm.addAction(self.actions[alis['Export nach SWMM-Datei (*.INP)']])
            strakat.addAction(self.actions[alis['Import aus STRAKAT']])
            # laengs.addAction(self.actions[alis['Längsschnitt-Tool für HE8']])
            # laengs.addAction(self.actions[alis['Ganglinien-Tool für HE8']])
            zustand.addAction(self.actions[alis['Zustandsklassen ermitteln']])
            zustand.addAction(self.actions[alis['Sanierungsbedarfszahl ermitteln']])
            flood2D.addAction(self.actions[alis['Überflutungsanimation']])
            info.addAction(self.actions[alis['Über QKan']])
            info.addAction(self.actions[alis['Infos zum QKan Projekt']])

    def unload(self) -> None:
        from qgis.utils import unloadPlugin

        # Shutdown logger
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        # Unload all other instances
        for instance in self.instances:
            print("Unloading ", instance.name)
            if not unloadPlugin(instance.name):
                print("Failed to unload plugin!")

        if self.menu:
            # Remove entries from own menu
            for action in self.menu.actions():
                self.menu.removeAction(action)

        # Remove entries from Plugin menu and toolbar
        for action in self.actions:
            self.iface.removeToolBarIcon(action)

        # Remove the toolbar
        if self.toolbar:
            del self.toolbar

        # Remove menu
        self.iface.mainWindow().menuBar().removeAction(self.menu_action)

        # Unload translator
        # noinspection PyArgumentList
        QCoreApplication.removeTranslator(self.translator)

        # Call unload on all loaded plugins
        for plugin in self.plugins:
            plugin.unload()

    def register(self, instance: "_ExternalQKanPlugin") -> None:
        self.instances.append(instance)

        self.plugins += instance.plugins

    def unregister(self, instance: "_ExternalQKanPlugin") -> None:
        self.instances.remove(instance)

        for plugin in instance.plugins:
            self.plugins.remove(plugin)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Callable,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str = None,
        whats_this: str = None,
        parent: QWidget = None,
    ) -> QAction:
        """Add a toolbar icon to the toolbar/menu.

        :param icon_path:       Path to the icon for this action. Can be a resource
                                path (e.g. ':/plugins/foo/bar.png') or a normal
                                file system path.
        :param text:            Text that should be shown in menu items for this action.
        :param callback:        Function to be called when the action is triggered.
        :param enabled_flag:    A flag indicating if the action should be enabled
                                by default. Defaults to True.
        :param add_to_menu:     Flag indicating whether the action should also
                                be added to the menu. Defaults to True.
        :param add_to_toolbar:  Flag indicating whether the action should also
                                be added to the toolbar. Defaults to True.
        :param status_tip:      Optional text to show in a popup when mouse pointer
                                hovers over the action.
        :param whats_this:      Optional text to show in the status bar when the
                                mouse pointer hovers over the action.
        :param parent:          Parent widget for the new action. Defaults None.
        :returns:               The action that was created. Note that the action is also
                                added to self.actions.
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu and self.menu:
            self.menu.addAction(action)

        self.actions.append(action)

        return action


def get_default_dir() -> str:
    """
    A helper method that returns the path of the currently opened project
    *or* the user's default directory
    """

    # noinspection PyArgumentList
    project_path = QgsProject.instance().fileName()
    if project_path:
        return str(Path(project_path).parent.absolute())
    else:
        # noinspection PyArgumentList
        return str(
            Path(
                QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[-1]
            ).absolute()
        )


def list_selected_items(list_widget: QListWidget) -> List[str]:
    """
    Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

    :param list_widget: Liste aller Widgets
    """

    return [_.text() for _ in list_widget.selectedItems()]
