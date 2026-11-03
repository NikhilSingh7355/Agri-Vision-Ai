# AgriVision AI

Streamlit app: upload or capture a leaf photo, get a crop/disease prediction with confidence,
Hindi/English guidance, and a downloadable report.

## Two modes
- **CNN mode** (real diagnosis): active when `model.keras` and `labels.json` are next to `app.py`.
- **Demo mode**: no model file. Only estimates the yellow/brown lesion share of the leaf. It is NOT a classifier
  and the app says so on screen.

## 1. Train the model (once, ~20-40 min on a free Colab GPU)
1. Open Google Colab, set Runtime > GPU, upload `train.py`.
2. Run:
   ```
   !pip install tensorflow-datasets scikit-learn
   !python train.py
   ```
3. Download `model.keras`, `labels.json`, `metrics.json` and put them in this folder.
   `metrics.json` is shown in the app sidebar, so use these REAL numbers in your slides.
   Note: PlantVillage images are lab-style (plain background) and random splits can leak near-duplicate
   images, so field accuracy will be lower than test accuracy. Say this honestly in the pitch.

## 2. Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## 3. Deploy (free)
**Streamlit Community Cloud**: push this folder to a GitHub repo (include model.keras; if >100 MB use Git LFS),
go to share.streamlit.io, New app, pick the repo, main file `app.py`, Deploy. You get a public link.

**Hugging Face Spaces** (alternative): New Space > SDK Streamlit > upload these files.

Put the final link on the PPT.

## 4. Voice assistant (Hindi / English / Bhojpuri-experimental)
Files: `voice.py` (+ small hook in `app.py`). Flow: mic -> Groq Whisper -> Groq Llama (knows the scan result) -> edge-tts voice (gTTS fallback).
1. Free key: console.groq.com > API Keys.
2. Local: create `.streamlit/secrets.toml` with `GROQ_API_KEY = "gsk_..."`
   Cloud: App settings > Secrets > paste the same line.
3. Without the key the app still works; the voice section just shows "off".
Limits (say these honestly): Bhojpuri is heard as Hindi and spoken with a Hindi voice; noisy fields hurt accuracy;
the assistant never gives pesticide names or doses, it sends the farmer to KVK / Kisan Call Centre.
Do not commit secrets.toml to GitHub (add `.streamlit/secrets.toml` to .gitignore).
