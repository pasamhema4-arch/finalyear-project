from langdetect import detect
from transformers import pipeline
from deep_translator import GoogleTranslator

# Load models once
sentiment_model = pipeline("sentiment-analysis")
emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)

def analyze_text(text):
    lang = detect(text)

    # Translate to English if needed
    translated = (
        GoogleTranslator(source='auto', target='en').translate(text)
        if lang != "en" else text
    )

    sentiment = sentiment_model(translated)[0]
    emotion = emotion_model(translated)[0]

    stress = "HIGH" if sentiment["label"] == "NEGATIVE" else "LOW"

    return {
        "original_text": text,
        "language": lang,
        "translated_text": translated,
        "sentiment": sentiment["label"],
        "emotion": emotion["label"],
        "stress_level": stress
    }