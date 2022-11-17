import logging

from PyQt6 import uic
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QSizePolicy,
)

import helpers
import refs
import settings
from structures.domains import Domains
from ui.panels.domains.table import Table
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    updated = pyqtSignal(Domains)

    def __init__(self, parent, domains: Domains) -> None:
        super().__init__(parent)
        self.domains: Domains = domains
        uic.loadUi("ui/panels/domains/panel.ui", self)

        # create domains editor table and append it to the bottom of the domains panel
        self.table = Table(self)
        self.layout().addWidget(self.table)

        # set initial values of domain table config widgets
        self.subunit_count.setValue(self.domains.subunit.count)
        self.symmetry.setValue(self.domains.symmetry)
        self.total_count.setValue(self.domains.count)

        logger.info("Loaded domains tab of config panel.")

        self._signals()
        self._prettify()

    def _signals(self):
        """Set up panel signals."""

        def update_total_domain_box():
            self.total_count.setValue(
                self.symmetry.value() * self.subunit_count.value()
            )

        self.symmetry.valueChanged.connect(update_total_domain_box)
        self.subunit_count.valueChanged.connect(update_total_domain_box)

        # when helix joint buttons are clicked refresh the table
        # so that the switch values (-1, 0, 1) get udpated
        self.table.helix_joint_updated.connect(
            lambda: self.table.dump_domains(self.table.fetch_domains())
        )

        # dump the initial domains
        self.table.dump_domains(refs.domains.current)

        # hook update domains button
        self.update_table.clicked.connect(self.refresh)

        # updated event linking
        self.table.cell_widget_updated.connect(
            lambda: self.updated.emit(self.table.fetch_domains())
        )
        self.update_table.clicked.connect(
            lambda: self.updated.emit(self.table.fetch_domains())
        )

    def _prettify(self):
        """Set up styles of panel."""
        # set reload table widget
        self.update_table.setIcon(fetch_icon("checkmark-outline"))

        # set scaling settings for config and table
        config_size_policy = QSizePolicy()
        config_size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        config_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        self.config.setSizePolicy(config_size_policy)

    def refresh(self):
        """Refresh panel settings/domain table."""
        # obtain current domain inputs
        new_domains = self.table.fetch_domains()
        new_domains = Domains(new_domains, self.symmetry.value())

        confirmation: bool = True
        # double-check with user if they want to truncate the domains/subunit count
        # (if that is what they are attempting to do)
        if self.subunit_count.value() < self.domains.subunit.count:
            # helpers.confirm will return a bool
            confirmation: bool = helpers.confirm(
                self.parent(),
                "Subunit Count Reduction",
                f"The prospective subunit count ({self.subunit_count.value()}) is lower than the number of domains in "
                f"the domains table ({self.table.rowCount()}). \n\nAre you sure you want to truncate the "
                f"domains/subunit count to {self.subunit_count.value()}?",
            )
            if confirmation:
                self.updated.emit(new_domains)
                self.total_count.setValue(self.domains.count)
                self.update_table.setStyleSheet(
                    f"background-color: rgb{str(settings.colors['success'])}"
                )
                timer = QTimer(self.parent())
                timer.setInterval(400)
                timer.setSingleShot(True)
                timer.timeout.connect(
                    lambda: self.update_table.setStyleSheet(
                        "background-color: light grey"
                    )
                )
                timer.start()
        else:
            self.updated.emit(new_domains)

        # refresh table
        self.table.dump_domains(new_domains)
