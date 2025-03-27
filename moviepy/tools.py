# moviepy/tools.py

import warnings

def deprecated_version_of(new_func, oldname=None):
    """
    Gibt eine Wrapper-Funktion zurück, die auf die neue Funktion verweist,
    aber eine Deprecation-Warnung für die alte ausgibt.
    """
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"'{oldname or new_func.__name__}' ist veraltet. Verwende stattdessen '{new_func.__name__}'.",
            category=DeprecationWarning,
            stacklevel=2
        )
        return new_func(*args, **kwargs)
    return wrapper

# Dummy fallback dictionary
extensions_dict = {}

# Dummy fallback function
def find_extension(filename):
    return None
def convert_to_seconds(varnames):
    """
    Decorator für Funktionen, die Zeit-Argumente erhalten (z.B. t="00:01:23").
    Wandelt diese Zeit-Strings automatisch in Sekunden um.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            for var in varnames:
                if var in kwargs:
                    val = kwargs[var]
                    if isinstance(val, str):
                        parts = [float(p) for p in val.strip().split(":")]
                        if len(parts) == 1:
                            kwargs[var] = parts[0]
                        elif len(parts) == 2:
                            kwargs[var] = parts[0] * 60 + parts[1]
                        elif len(parts) == 3:
                            kwargs[var] = parts[0] * 3600 + parts[1] * 60 + parts[2]
            return f(*args, **kwargs)
        return wrapper
    return decorator

    raise ValueError(f"Ungültiges Zeitformat: {time_input}")
def is_string(s):
    return isinstance(s, str)
import subprocess

def subprocess_call(cmd, **kwargs):
    """
    Führt einen Shell-Befehl aus (wie ffmpeg) und leitet stdout/stderr um.
    """
    return subprocess.call(cmd, shell=True, **kwargs)
