"""
DUKATOR - Archivador de Música Underground
Punto de entrada principal
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui.app import main

if __name__ == "__main__":
    main()