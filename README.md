# AgriVision AI
 TEAM : SHADOW WAR(PRESENTED BY)
 NIKHIL SINGH
 VISHAL KUMAR YADAV
 PRABHAT KUMAR SHARMA
FAZILA ANSARI
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

ppt link:https://docs.google.com/presentation/d/18r-cnmM_ZypqvJtwlYuz_tUit6fFWPMk/edit?usp=sharing&ouid=106116844708181444006&rtpof=true&sd=true
