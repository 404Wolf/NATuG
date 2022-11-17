import logging
import os
from contextlib import suppress
from time import time

# whether to delete restoration files
RESET = True

# refs script logger object
logger = logging.getLogger(__name__)

# mute pyqt logs
logging.getLogger("PyQt6").setLevel(logging.WARNING)


def main():
    """Main runner for program."""

    if RESET:
        with suppress(FileNotFoundError):
            os.remove("saves/nucleic_acid/profiles.nano")
            os.remove("saves/nucleic_acid/restored.nano")
            os.remove("saves/domains/restored.nano")
            os.remove("saves/strands/restored.nano")

    with suppress(FileExistsError):
        os.mkdir(f"{os.getcwd()}\\saves\\nucleic_acid")
        os.mkdir(f"{os.getcwd()}\\saves\\domains")
        os.mkdir(f"{os.getcwd()}\\saves\\strands")

    import pyqtgraph as pg

    pg.setConfigOptions(
        useOpenGL=True, antialias=False, background=pg.mkColor(255, 255, 255)
    )

    import refs

    # set log level
    logging.basicConfig(
        level=logging.DEBUG,
    )

    logger.debug(f"Booting @ {time()}")

    logger.info("Loaded profiles and domain settings.")

    import sys

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    logger.info("Loaded the config.")

    # show the ui window
    refs.constructor.show()
    refs.constructor.resizeEvent(None)  # trigger initial resize event
    logger.debug("Set up refs window")

    # begin app event loop
    logger.debug("Beginning event loop...")
    sys.exit(refs.application.exec())


if __name__ == "__main__":
    main()