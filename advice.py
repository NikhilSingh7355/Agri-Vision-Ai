"""Plain-language guidance (English + Hindi) for PlantVillage-style class labels."""

FUNGAL = ["blight", "rust", "scab", "mildew", "mold", "leaf spot", "rot", "measles", "scorch", "black"]
BACTERIAL = ["bacterial", "canker", "greening"]
VIRAL = ["virus", "curl", "mosaic"]
PEST = ["mite"]

ACTIONS = {
    "fungal": (
        ["Remove and destroy badly infected leaves; do not leave them in the field.",
         "Avoid watering from above and avoid working in the field when plants are wet.",
         "Improve spacing and air flow between plants.",
         "Ask your local agriculture officer or KVK which fungicide is suitable before spraying."],
        ["ज्यादा संक्रमित पत्तियों को तोड़कर नष्ट करें, खेत में न छोड़ें।",
         "ऊपर से सिंचाई न करें और पौधे गीले हों तो खेत में काम करने से बचें।",
         "पौधों के बीच दूरी रखें ताकि हवा का आवागमन बना रहे।",
         "छिड़काव से पहले अपने कृषि अधिकारी या कृषि विज्ञान केंद्र से सही फफूंदनाशक की सलाह लें।"]),
    "bacterial": (
        ["Remove infected leaves and plants and keep them away from healthy ones.",
         "Use clean tools and avoid moving through the field when it is wet.",
         "Use certified, disease-free seed or seedlings next season.",
         "Ask your local agriculture officer what treatment is suitable for your crop."],
        ["संक्रमित पत्तियों और पौधों को हटाकर स्वस्थ पौधों से दूर रखें।",
         "साफ औज़ारों का उपयोग करें और गीले खेत में न घूमें।",
         "अगले मौसम में प्रमाणित, रोग-मुक्त बीज या पौध का उपयोग करें।",
         "अपनी फसल के लिए सही उपचार हेतु कृषि अधिकारी से सलाह लें।"]),
    "viral": (
        ["Remove and destroy infected plants early so the virus does not spread.",
         "Control insects such as whitefly and aphids that carry the virus.",
         "Use resistant varieties and healthy seedlings next season.",
         "Ask your local agriculture officer for insect-control advice."],
        ["संक्रमित पौधों को जल्दी हटाकर नष्ट करें ताकि वायरस न फैले।",
         "सफेद मक्खी और माहू जैसे कीट, जो वायरस फैलाते हैं, उन्हें नियंत्रित करें।",
         "अगले मौसम में प्रतिरोधी किस्में और स्वस्थ पौध लगाएँ।",
         "कीट नियंत्रण के लिए अपने कृषि अधिकारी से सलाह लें।"]),
    "pest": (
        ["Check the underside of leaves for tiny mites or webbing.",
         "Remove heavily affected leaves and keep the field free of weeds.",
         "Ask your local agriculture officer which control is suitable."],
        ["पत्तियों के नीचे की ओर छोटे कीट या जाले की जाँच करें।",
         "ज्यादा प्रभावित पत्तियाँ हटाएँ और खेत को खरपतवार से मुक्त रखें।",
         "सही नियंत्रण के लिए कृषि अधिकारी से सलाह लें।"]),
    "other": (
        ["Isolate and monitor the affected plants and compare them with healthy ones.",
         "Take clear photos in daylight and show them to an agriculture expert.",
         "Ask your local agriculture officer before applying any treatment."],
        ["प्रभावित पौधों को अलग करके निगरानी रखें और स्वस्थ पौधों से तुलना करें।",
         "दिन की रोशनी में साफ़ फोटो लेकर कृषि विशेषज्ञ को दिखाएँ।",
         "कोई भी उपचार करने से पहले कृषि अधिकारी से सलाह लें।"]),
}

PREVENTION = (
    ["Monitor the field every few days and act early.",
     "Rotate crops and use certified, healthy seed.",
     "Keep the field clean and avoid water standing on leaves."],
    ["हर कुछ दिन में खेत की निगरानी करें और जल्दी कार्रवाई करें।",
     "फसल चक्र अपनाएँ और प्रमाणित, स्वस्थ बीज का उपयोग करें।",
     "खेत साफ रखें और पत्तियों पर पानी जमा न होने दें।"])

HEALTHY = (["The leaf looks healthy. Keep monitoring regularly."],
           ["पत्ती स्वस्थ दिख रही है। नियमित निगरानी जारी रखें।"])


def parse_label(label: str):
    crop, _, disease = label.partition("___")
    crop = crop.replace("_", " ").replace(",", "").strip()
    disease = disease.replace("_", " ").strip() or "unknown"
    return crop, disease


def category(disease: str) -> str:
    d = disease.lower()
    if "healthy" in d:
        return "healthy"
    for name, words in (("viral", VIRAL), ("bacterial", BACTERIAL), ("pest", PEST), ("fungal", FUNGAL)):
        if any(w in d for w in words):
            return name
    return "other"


def get_advice(label: str, lang: str):
    """Returns (actions, prevention) lists in the chosen language ('en' or 'hi')."""
    _, disease = parse_label(label)
    cat = category(disease)
    i = 0 if lang == "en" else 1
    if cat == "healthy":
        return HEALTHY[i], []
    return ACTIONS[cat][i], PREVENTION[i]
