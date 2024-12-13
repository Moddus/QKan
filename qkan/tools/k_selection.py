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

logger = get_logger("QKan.tools.k_selection")


def selection(
    db,
    ausw_haltung,
    ausw_schacht,
) -> None:

    pass
