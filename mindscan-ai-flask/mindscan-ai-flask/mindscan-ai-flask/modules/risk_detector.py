from models import Mood

def detect_risk(user_id):
    moods = Mood.query.filter_by(user_id=user_id).all()

    total = len(moods)
    if total == 0:
        return {"risk_level": "low", "message": "Not enough data yet."}

    counts = {}
    for m in moods:
        counts[m.emotion] = counts.get(m.emotion, 0) + 1

    sadness = counts.get("sadness", 0)
    anger = counts.get("anger", 0)
    fear = counts.get("fear", 0)

    negative = sadness + anger + fear
    ratio = negative / total

    if ratio > 0.6:
        return {
            "risk_level": "high",
            "message": "Your recent emotional patterns show high stress. Consider talking to someone you trust or a professional."
        }

    elif ratio > 0.3:
        return {
            "risk_level": "moderate",
            "message": "Some stress indicators detected. Try relaxation techniques and maintain a healthy routine."
        }

    else:
        return {
            "risk_level": "low",
            "message": "Your emotional patterns look generally positive. Keep maintaining good habits."
        }