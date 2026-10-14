import json, os, io
from datetime import datetime
import numpy as np
import streamlit as st
from PIL import Image

from advice import get_advice, parse_label, category
from lesion import lesion_share, severity

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "model.keras")
LABELS_PATH = os.path.join(HERE, "labels.json")
METRICS_PATH = os.path.join(HERE, "metrics.json")
CONF_THRESHOLD = 0.60

T = {
    "en": dict(title="AgriVision AI", tag="Detect Early. Protect Crops. Empower Farmers.",
               lang="Language", photo="Take or upload a clear photo of ONE affected leaf",
               upload="Upload leaf photo", camera="Use camera", analyse="Analysing leaf...",
               result="Result", conf="Confidence", crop="Crop", disease="Condition",
               low="Low confidence: the result may be wrong. Retake the photo in daylight with the leaf filling the frame, or ask an expert.",
               top3="Other possibilities", actions="What to do now", prevent="Prevention",
               expert="Expert support", expert_txt="Kisan Call Centre (toll-free): 1800-180-1551. Show this report to your local agriculture officer or KVK.",
               download="Download report", demo_title="Demo mode (no trained model loaded)",
               demo_txt="This is NOT a disease classifier. It only estimates how much of the leaf shows yellow/brown lesion colours. Add model.keras (see README) to enable CNN diagnosis.",
               share="Estimated affected area", sev="Severity", none="none", mild="mild", moderate="moderate", severe="severe",
               noleaf="Could not find a leaf in this photo. Please retake it.",
               disclaimer="AgriVision AI gives guidance, not a final diagnosis. Confirm with an agriculture expert before spraying anything.",
               model_perf="Model performance (test set)", healthy="Healthy"),
    "hi": dict(title="एग्रीविज़न AI", tag="जल्दी पहचानें। फसल बचाएँ। किसान को सशक्त बनाएँ।",
               lang="भाषा", photo="प्रभावित पत्ती की एक साफ़ फोटो लें या अपलोड करें",
               upload="पत्ती की फोटो अपलोड करें", camera="कैमरा उपयोग करें", analyse="पत्ती की जाँच हो रही है...",
               result="परिणाम", conf="विश्वसनीयता", crop="फसल", disease="स्थिति",
               low="विश्वसनीयता कम है: परिणाम गलत हो सकता है। दिन की रोशनी में पत्ती को पूरे फ्रेम में रखकर दोबारा फोटो लें या विशेषज्ञ से पूछें।",
               top3="अन्य संभावनाएँ", actions="अभी क्या करें", prevent="बचाव",
               expert="विशेषज्ञ सहायता", expert_txt="किसान कॉल सेंटर (टोल-फ्री): 1800-180-1551। यह रिपोर्ट अपने कृषि अधिकारी या कृषि विज्ञान केंद्र को दिखाएँ।",
               download="रिपोर्ट डाउनलोड करें", demo_title="डेमो मोड (प्रशिक्षित मॉडल लोड नहीं है)",
               demo_txt="यह रोग पहचानने वाला मॉडल नहीं है। यह केवल अनुमान लगाता है कि पत्ती का कितना हिस्सा पीले/भूरे धब्बों जैसा दिख रहा है। CNN निदान के लिए model.keras जोड़ें (README देखें)।",
               share="अनुमानित प्रभावित क्षेत्र", sev="गंभीरता", none="कोई नहीं", mild="हल्की", moderate="मध्यम", severe="गंभीर",
               noleaf="इस फोटो में पत्ती नहीं मिली। कृपया दोबारा फोटो लें।",
               disclaimer="एग्रीविज़न AI मार्गदर्शन देता है, अंतिम निदान नहीं। कुछ भी छिड़कने से पहले कृषि विशेषज्ञ से पुष्टि करें।",
               model_perf="मॉडल प्रदर्शन (टेस्ट सेट)", healthy="स्वस्थ"),
}

st.set_page_config(page_title="AgriVision AI", page_icon="🌿", layout="centered")


@st.cache_resource(show_spinner=False)
def load_model():
    if not (os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH)):
        return None, None
    import tensorflow as tf
    model = tf.keras.models.load_model(MODEL_PATH)
    labels = json.load(open(LABELS_PATH))
    return model, labels


def predict(model, labels, img):
    x = np.asarray(img.convert("RGB").resize((224, 224)), dtype="float32")[None]
    p = model.predict(x, verbose=0)[0]
    idx = np.argsort(p)[::-1][:3]
    return [(labels[i], float(p[i])) for i in idx]


lang = st.sidebar.radio("Language / भाषा", ["en", "hi"], format_func=lambda x: "English" if x == "en" else "हिन्दी")
t = T[lang]
model, labels = load_model()

if os.path.exists(METRICS_PATH):
    m = json.load(open(METRICS_PATH))
    st.sidebar.subheader(t["model_perf"])
    for k in ("accuracy", "precision", "recall", "f1"):
        if k in m:
            st.sidebar.metric(k.upper() if k == "f1" else k.capitalize(), f"{m[k]*100:.1f}%")

st.title("🌿 " + t["title"])
st.caption(t["tag"])

if model is None:
    st.warning(f"**{t['demo_title']}**\n\n{t['demo_txt']}")

st.subheader(t["photo"])
tab1, tab2 = st.tabs([t["upload"], t["camera"]])
with tab1:
    up = st.file_uploader(t["upload"], type=["jpg", "jpeg", "png"], label_visibility="collapsed")
with tab2:
    cam = st.camera_input(t["camera"], label_visibility="collapsed")
src = up or cam

if src:
    img = Image.open(src)
    st.image(img, use_container_width=True)
    with st.spinner(t["analyse"]):
        report = [f"AgriVision AI report - {datetime.now():%Y-%m-%d %H:%M}"]
        st.header(t["result"])
        if model is not None:
            preds = predict(model, labels, img)
            label, conf = preds[0]
            crop, disease = parse_label(label)
            disease_show = t["healthy"] if category(disease) == "healthy" else disease
            c1, c2, c3 = st.columns(3)
            c1.metric(t["crop"], crop); c2.metric(t["disease"], disease_show); c3.metric(t["conf"], f"{conf*100:.0f}%")
            st.progress(min(conf, 1.0))
            if conf < CONF_THRESHOLD:
                st.error(t["low"])
            st.write(f"**{t['top3']}**")
            for l, p in preds[1:]:
                cr, di = parse_label(l)
                st.write(f"- {cr}: {di} ({p*100:.0f}%)")
            actions, prevention = get_advice(label, lang)
            report += [f"{crop}: {disease} ({conf*100:.0f}% confidence)"]
        else:
            share = lesion_share(img)
            if share is None:
                st.error(t["noleaf"]); st.stop()
            sev = severity(share)
            c1, c2 = st.columns(2)
            c1.metric(t["share"], f"{share*100:.0f}%"); c2.metric(t["sev"], t[sev])
            actions, prevention = get_advice("Crop___leaf spot" if sev != "none" else "Crop___healthy", lang)
            report += [f"Demo mode - estimated affected area {share*100:.0f}% ({sev})"]

    st.subheader(t["actions"])
    for a in actions: st.write("- " + a)
    if prevention:
        st.subheader(t["prevent"])
        for a in prevention: st.write("- " + a)
    st.subheader(t["expert"]); st.info(t["expert_txt"])
    report += [""] + actions + prevention + ["", t["disclaimer"]]
    st.download_button(t["download"], "\n".join(report), file_name="agrivision_report.txt")

st.divider()
st.caption(t["disclaimer"])
