import logging
from types import SimpleNamespace

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QDockWidget,
    QMenuBar,
    QVBoxLayout,
    QGroupBox,
    QWidget,
)
from PyQt6.QtGui import QScreen

import config.main
import config.nucleic_acid
import config.domains.storage
import plotting.side_view.runner
import plotting.top_view.runner
import references
from copy import deepcopy

logger = logging.getLogger(__name__)


class Window(QMainWindow):
    """
    The application's main window.

    Attributes:
        docked_widgets (SimpleNamespace): All docked widgets.
        status_bar (QStatusBar): The status bar.
        menu_bar (QMenuBar): The menu bar.
        top_view (QWidget): Top view widget.
        side_view (QWidget): Side view widget.
    """

    def __init__(self):
        # this is an inherited class of QMainWindow,
        # so we must initialize the parent qt widget
        super().__init__()

        # store a reference to self in references for cross module use
        references.Windows.constructor = self

        # utilize inherited methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # initialize status bar
        self._status_bar()

        # initialize menu bar
        self._menu_bar()

        # container to store references to all docked widgets
        self.docked_widgets = SimpleNamespace()

        # add all widgets
        self.load_graphs()
        self._config()

    def _config(self):
        # create a dockable config widget
        self.docked_widgets.config = QDockWidget()
        self.docked_widgets.config.setObjectName("Config Panel")
        self.docked_widgets.config.setWindowTitle("Config")
        self.docked_widgets.config.setStatusTip("Config panel")

        # store the actual link to the widget in self.config
        self.config = config.main.Panel()
        self.docked_widgets.config.setWidget(self.config)

        # floating will be determined by current tab (see self.resizeEvent)
        self.docked_widgets.config.setFeatures(
            QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
        )

        # remove config scaling limitations when config becomes floating
        self.docked_widgets.config.topLevelChanged.connect(self.resizeEvent)

        # dock the new dockable config widget
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.docked_widgets.config
        )

    def load_graphs(self):
        """Load all nanotube graphs simultaneously."""
        self._top_view()
        self._side_view()

    def _top_view(self):
        """Attach top view to main window/replace current top view widget"""
        try:
            assert isinstance(self.top_view, QWidget)
            self.top_view.load()
            logger.info("Reloaded top view graph.")
        except AttributeError or AssertionError:
            # create dockable widget for top view
            self.docked_widgets.top_view = QDockWidget()
            self.docked_widgets.top_view.setObjectName("Top View")
            self.docked_widgets.top_view.setWindowTitle("Top View of Helices")
            self.docked_widgets.top_view.setStatusTip(
                "A plot of the top view of all domains"
            )

            # store widget in class for easier direct access
            self.top_view = plotting.top_view.runner.Plot()

            # attach actual top view widget to docked top view widget
            self.docked_widgets.top_view.setWidget(self.top_view)

            self.docked_widgets.top_view.setAllowedAreas(
                Qt.DockWidgetArea.LeftDockWidgetArea
            )
            self.docked_widgets.top_view.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )

            self.docked_widgets.top_view.topLevelChanged.connect(self.resizeEvent)

            # dock the new dockable top view widget
            self.addDockWidget(
                Qt.DockWidgetArea.LeftDockWidgetArea, self.docked_widgets.top_view
            )

            logger.info("Loaded top view graph for the first time.")

    def _side_view(self):
        """Attach side view to main window/replace current side view widget"""
        try:
            assert isinstance(self.side_view, QWidget)
            self.side_view.load()
            logger.info("Reloaded side view graph.")
        except AttributeError or AssertionError:
            # create group box to place side view widget in
            prettified_side_view = QGroupBox()
            prettified_side_view.setObjectName("Side View")
            prettified_side_view.setLayout(QVBoxLayout())
            prettified_side_view.setTitle("Side View of Helices")
            prettified_side_view.setStatusTip("A plot of the side view of all domains")

            # store widget in class for easier future direct widget access
            self.side_view = plotting.side_view.runner.Plot()
            prettified_side_view.layout().addWidget(self.side_view)

            # set side view as the main widget
            self.setCentralWidget(prettified_side_view)

            logger.info("Loaded side view graph for the first time.")

    def _status_bar(self):
        """Create and add status bar."""
        status_bar = self.status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self.statusBar().setStyleSheet("background-color: rgb(210, 210, 210)")
        logger.info("Created status bar.")

    def _menu_bar(self):
        """Create a menu bar for the main window"""
        # create menu bar
        self.menu_bar = QMenuBar()

        # import all menu bars
        import windows.constructor.menus as menus

        # add all the menus to the filemenu
        self.menu_bar.addMenu(menus.File())
        self.menu_bar.addMenu(menus.view())
        self.menu_bar.addMenu(menus.help())

        # place the menu bar object into the actual menu bar
        self.setMenuBar(self.menu_bar)
        logger.info("Created menu bar.")

    def resizeEvent(self, event):
        """
        Changes size of various widgets dynamically based on the main window's size.

        Notes:
            - If domain tab of config panel is showing, makes config panel pop out and larger
            - If domain tab of config panel is not showing, makes config panel unpop out and smaller
        """
        # side view resizing
        #
        # self.side_view.setMinimumWidth(int(3 * window_width / 8))

        # top view resizing
        #
        # set extra large width of the config panel if it is floating
        if self.docked_widgets.top_view.isFloating():
            self.docked_widgets.top_view.setMinimumWidth(350)
            self.docked_widgets.top_view.setMaximumWidth(99999)
        # set reasonably sized width of not floating panel
        else:
            self.docked_widgets.top_view.setMinimumWidth(180)
            self.docked_widgets.top_view.setMaximumWidth(
                round(2 * self.size().width() / 8)
            )

        # config resizing
        #
        # if the config panel's domain tab is visible make the config panel float
        # and make it a third of the width of the main panel
        if self.config.tabs.domains.isVisible():
            # right when the config tab becomes visible do fancy resizing
            # and make it float...
            if not self.docked_widgets.config.isFloating():
                self.docked_widgets.config.setFloating(True)
                self.docked_widgets.config.setMinimumWidth(
                    round(self.size().width() / 2.5)
                )
                self.docked_widgets.config.setMaximumWidth(
                    round(self.size().width() / 2.5) + 100
                )

                # set the height of the domains table to (the height of a singular domain entry * number of domains)
                desired_config_height = 45 * len(config.domains.storage.current)
                screen_size = references.app.primaryScreen().size().height()
                # but if this would require making the domains table taller than the actual screen size,
                # just set the domains table height to the screen size
                if desired_config_height > screen_size:
                    self.docked_widgets.config.setMinimumHeight(screen_size)
                else:

                    self.docked_widgets.config.setMinimumHeight(desired_config_height)
                    # now that the height has grown allow the height to shrink again
                    self.docked_widgets.config.setMinimumHeight(0)

        # if the config panel's domain tab is not visible then unfloat the config panel
        else:
            self.docked_widgets.config.setFloating(False)
            self.docked_widgets.config.setMinimumWidth(190)
            self.docked_widgets.config.setMaximumWidth(
                round(2 * self.size().width() / 8)
            )