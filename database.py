import dna_nanotube_tools
from PyQt6.QtWidgets import QMainWindow
import ui.datatypes

"""
This file allows cross module data syncing
"""


main_window: QMainWindow


def domains():
    return [dna_nanotube_tools.domain(9, 0)] * 14


def settings():
    return ui.datatypes.profile(
        count=200,
        diameter=2.2,
        H=3.549,
        T=2,
        B=21,
        Z_c=0.17,
        Z_s=1.26,
        theta_b=34.29,
        theta_c=360 / 21,
        theta_s=2.3,
    )