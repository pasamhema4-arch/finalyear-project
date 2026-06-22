import matplotlib.pyplot as plt
from models import Mood
from datetime import datetime, timedelta
import io, base64


def plot_emotion_graph(user_id):
    today = datetime.utcnow()
    week_start = today - timedelta(days=7)
    moods = Mood.query.filter(Mood.user_id == user_id, Mood.created_at >= week_start).order_by(Mood.created_at).all()

    if not moods:
        return ""

    dates = [m.created_at.date() for m in moods]
    intensities = [m.confidence * 100 for m in moods]
    stress_levels = [m.stress_level for m in moods]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, intensities, label="Emotion Confidence", marker='o')
    plt.plot(dates, stress_levels, label="Stress Level", marker='x')
    plt.xlabel("Date")
    plt.ylabel("Score")
    plt.title("Weekly Emotion & Stress Graph")
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return img_base64  # Can embed in HTML <img src="data:image/png;base64,...">