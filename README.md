# 🎬 VICO – Video-Effects & Composition Operator

**VICO** ist eine Sammlung von spezialisierten Python-Tools für kreative Videobearbeitung mit Audiosteuerung – inklusive Zoom, Shake, Ripple, Merging, Auto-Analyse und mehr. Ideal für Visual Artists, Musikvideos, VJing oder einfach Nerds mit Stil. 🤘

---

## 📁 Projektstruktur

```
vico/
├── moviepy/          # Lokale, modifizierte Version von MoviePy
├── vico_merge.py     # Kombiniert Video und Audio
├── vico_zoom.py      # Zoom-Effekt auf Audio-Basis
├── vico_shake.py     # Shake-Effekt gesteuert durch RMS
├── vico_ripple.py    # Ripple-Effekt durch Audiointensität
├── vico_color.py     # (vermutlich Farbspiel basierend auf Audio?)
├── vico_clean.py     # Ersetzt verlustbehaftete Audiospur mit WAV
├── Vico_auto.py      # Automatische Audioanalyse
├── gui/              # Optional: Web-GUI via Streamlit
│   └── app.py
├── requirements.txt  # Abhängigkeiten (ohne moviepy!)
└── README.md
```

---

## ⚙️ Installation

### 🔧 Vorbereitung (einmalig)

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# oder
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

---

## 🚀 Verwendung

Alle Tools lassen sich per CLI ausführen, z. B.:

```bash
python vico_merge.py -a bass.wav -v clip1.mp4 clip2.mp4 --crossfade 2 --fps 30
```

Oder starte die (optionale) GUI:

```bash
streamlit run gui/app.py
```

---

## 🧠 Wichtig: Lokaler `moviepy`-Fork

Dieses Projekt verwendet eine **modifizierte Version von `moviepy`**, da neuere Versionen kein vollständiges `editor`-Modul enthalten.  
Die lokal angepasste Version liegt im Ordner:

```
/moviepy
```

Bitte **nicht `moviepy` über pip installieren**, sonst werden deine Änderungen überschrieben.

---

## ⚡ CUDA / GPU-Unterstützung

Wenn du `cupy` verwenden willst (für CUDA-Beschleunigung), stelle sicher, dass:

- ein NVIDIA-Grafiktreiber vorhanden ist
- `CUDA Toolkit` installiert ist
- die passende `cupy`-Version gewählt wird

Falls du **keine GPU** nutzt, kannst du `cupy` in `requirements.txt` einfach entfernen.

---

## 💬 Lizenz & Mitmachen

Kein Lizenztext vorhanden. Also: Frag Reini 😄  
Contributions, Forks & Nerdtalk willkommen!

---

