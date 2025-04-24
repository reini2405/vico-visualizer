# core/vico_executor.py
import subprocess
import sys
import os

def run_vico_merge(audio, videos, crossfade=None, reverse=False, rc=False, fps=None):
    script_path = os.path.join(os.path.dirname(__file__), "..", "vico_modules", "vico_merge.py")
    cmd = [sys.executable, script_path, "-a", audio, "-v"] + videos

    if reverse:
        cmd.append("-r")
    if rc:
        cmd.append("--rc")
    if crossfade:
        cmd += ["-c", str(crossfade)]
    if fps:
        cmd += ["--fps", str(fps)]

    print("Führe aus:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result
