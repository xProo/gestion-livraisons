"""Point d'entrée : ``python -m src`` depuis le dossier ``projet``."""

import sys

from src.interface import boucle


def main() -> None:
    for flux in (sys.stdout, sys.stderr):
        reconfigurer = getattr(flux, "reconfigure", None)
        if reconfigurer is None:
            continue
        try:
            reconfigurer(encoding="utf-8")
        except (OSError, ValueError):
            pass
    boucle()


if __name__ == "__main__":
    main()
