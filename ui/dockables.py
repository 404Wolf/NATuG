from types import SimpleNamespace
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QTabWidget,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QDockWidget,
)
from PyQt6 import uic
import dna_nanotube_tools
import ui.slots
from PyQt6.QtCore import Qt

# START OF PLACEHOLDER CODE
domains = [dna_nanotube_tools.domain(9, 0)] * 14
_top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)
# END OF PLACEHOLDER CODE

dock_areas = SimpleNamespace(
    left=0x1,
    right=0x2,
    top=0x4,
    bottom=0x8,
    all=0
)

class top_view(QDockWidget):
    """Top view dock"""

    def __init__(self):
        super().__init__("Top View of Helicies")

        self.setWindowTitle("Top View of Helicies")
        self.setStatusTip("A plot of the top view of all domains")
        self.setWidget(_top_view.ui())
        self.widget().setStyleSheet("margin: 5px")

        self.setMaximumWidth(250)
        self.topLevelChanged.connect(lambda: ui.slots.float_resizer(self, 250))
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # area for widget to be docked (this is accessed in main_window.py)
        self.area = Qt.DockWidgetArea(dock_areas.left)


class config(QDockWidget):
    """
    A tab box for config and domain configuration.

    This is a docked widget which initiates on the right side of the main window.
    The layout() subclass arranges all the other subclasses in this order (top to bottom):
    """

    def __init__(self) -> None:
        super().__init__()

        class tab_area(QTabWidget):
            """Settings/Domain tab area"""

            def __init__(self):
                super().__init__()

                # container to store all tabs in
                self.tabs = SimpleNamespace()

                class settings(QWidget):
                    """Settings area"""

                    def __init__(subself):
                        super().__init__()
                        uic.loadUi("ui/settings.ui", subself)

                self.tabs.settings = settings()
                self.tabs.domains = QLabel("Placeholder for domain tab")

                self.addTab(self.tabs.settings, "Settings")
                self.addTab(self.tabs.domains, "Domains")

        class update_graphs(QPushButton):
            def __init__(subself):
                super().__init__("Update Graphs")

        self.laid_out = QWidget()
        self.laid_out.setLayout(QVBoxLayout())
        self.laid_out.layout().addWidget(tab_area())
        self.laid_out.layout().addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        self.laid_out.layout().addWidget(update_graphs())

        self.setWindowTitle("Config")
        self.setStatusTip("Settings panel")
        self.setWidget(self.laid_out)
        self.setMaximumWidth(450)
        # ensure that when the config panel is undocked it can resize to be larger
        self.topLevelChanged.connect(
            lambda: ui.slots.float_resizer(self, 250, maximum_width=400)
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # area for widget to be docked (this is accessed in main_window.py)
        self.area = Qt.DockWidgetArea(dock_areas.right)
