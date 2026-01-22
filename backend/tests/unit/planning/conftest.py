"""Configuration pytest pour les tests du module Planning.

Ce conftest est auto-suffisant et n'herite pas du conftest global
pour eviter les problemes de dependances circulaires.
"""

import sys
from pathlib import Path

# Ajouter le repertoire backend au path pour les imports
backend_path = Path(__file__).parent.parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
