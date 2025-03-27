# moviepy/compat.py

import sys
import os

# DEVNULL für subprocess
try:
    from subprocess import DEVNULL
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

# string_types für Py2/Py3-Kompatibilität
string_types = (str,)
PY3 = True

