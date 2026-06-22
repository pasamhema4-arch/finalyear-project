from datetime import datetime, timedelta
from models import Mood, db

def generate_weekly_report(user_id):
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=7)
    moods = Mood.query.filter(Mood.user_id == user_id, Mood.created_at >= week_start).all()
    
    if not moods:
        return "No data available for this week."
    
    report = {
        "average_stress": round(sum(m.stress_level for m in moods) / len(moods), 1),
        "average_emotion_confidence": round(sum(m.confidence * 100 for m in moods) / len(moods), 1),
        "social_sentiment_trend": round(sum(m.social_sentiment for m in moods) / len(moods), 2),
        "screen_time_hours": round(sum(m.screen_time for m in moods), 1),
        "entry_count": len(moods)
    }
    return report