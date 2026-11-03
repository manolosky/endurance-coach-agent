"""Make `coach` importable when a script is run as `python3 scripts/<name>.py`."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
