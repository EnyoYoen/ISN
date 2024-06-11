import os
import sys
import platform

SYSTEM = platform.system()

from vue.Core import Core


def exodus():
    """
        Launches the Exodus game.
    """
    game = Core()
    game.setup_parameter()
    game.run()
    sys.exit(0)


if __name__ == "__main__":
    exodus()
