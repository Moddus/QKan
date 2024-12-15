import os
from typing import TYPE_CHECKING, Optional
import webbrowser
from qgis.gui import QgisInterface
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QWidget,
    QTextBrowser,
)


from qkan import QKan

from . import QKanDBDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_filepath, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_selection.ui")
)


class QgsFileDialog(QKanDBDialog, FORM_CLASS_filepath):  # type: ignore
    button_box: QDialogButtonBox
    pushButton: QPushButton
    pushButton_2: QPushButton
    pushButton_3: QPushButton
    pushButton_4: QPushButton
    pushButton_5: QPushButton
    checkBox: QCheckBox
    checkBox_2: QCheckBox


    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent, readonly=True)

        self.pushButton.clicked.connect(self.select_tg)
        self.pushButton_2.clicked.connect(self.select_oberhalb)
        self.pushButton_3.clicked.connect(self.select_unterhalb)
        self.pushButton_4.clicked.connect(self.select_zwischen_haltung)
        self.pushButton_5.clicked.connect(self.select_zwischen_kreuzung)
        self.button_box.helpRequested.connect(self.click_help)

    def click_help(self) -> None:
        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_Formulare.html#datenbank-aktualisieren"
        os.startfile(help_file)

    def select_tg(self) -> None:

        pass

    def select_oberhalb(self) -> None:

        pass

    def select_unterhalb(self) -> None:

        pass

    def select_zwischen_haltung(self) -> None:

        pass

    def select_zwischen_kreuzung(self) -> None:

        pass