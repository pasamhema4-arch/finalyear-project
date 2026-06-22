from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Mood, JournalEntry, Notification
from analyzer import detect_mood
from modules.risk_detector import detect_risk


analysis_bp = Blueprint("analysis", __name__)



# ===== AI SUGGESTION FUNCTION =====
def generate_suggestion(emotion):

    if emotion == "sadness":
        return "Try spending time with friends or doing activities you enjoy."

    elif emotion == "anger":
        return "Take deep breaths and step away from stressful situations."

    elif emotion == "fear":
        return "Practice relaxation techniques like meditation."

    elif emotion == "joy":
        return "Great! Keep doing things that make you happy."

    elif emotion == "love":
        return "Stay connected with people who support you."

    else:
        return "Maintain balance with rest, exercise and healthy habits."
# ========================
# ANALYZE EMOTION
# ========================
@analysis_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():

    data = request.get_json()
    text = data.get("text")

    result = detect_mood(text)

    user_id = int(get_jwt_identity())

    mood = Mood(
        user_id=user_id,
        text=text,
        emotion=result["label"],
        confidence=result["score"]
    )

    db.session.add(mood)
    db.session.commit()

    suggestion = generate_suggestion(result["label"])

    return jsonify({
    "emotion": result["label"],
    "confidence": result["score"],
    "suggestion": suggestion
})


# ========================
# MOOD HISTORY
# ========================
@analysis_bp.route("/history", methods=["GET"])
@jwt_required()
def history():

    user_id = int(get_jwt_identity())

    moods = Mood.query.filter_by(user_id=user_id).all()

    result = []

    for m in moods:
        result.append({
            "text": m.text,
            "emotion": m.emotion,
            "confidence": m.confidence,
            "date": m.created_at
        })

    return jsonify(result)

# =================================
# WEEKLY REPORT
# =================================
from datetime import datetime, timedelta

@analysis_bp.route("/weekly-report", methods=["GET"])
@jwt_required()
def weekly_report():

    user_id = int(get_jwt_identity())

    last_week = datetime.now() - timedelta(days=7)

    moods = Mood.query.filter(
        Mood.user_id == user_id,
        Mood.created_at >= last_week
    ).all()

    emotion_count = {}

    for m in moods:
        emotion_count[m.emotion] = emotion_count.get(m.emotion, 0) + 1

    dominant = max(emotion_count, key=emotion_count.get) if emotion_count else "neutral"

    positive_count = sum(1 for m in moods if m.emotion in ["joy", "love"])
    negative_count = sum(1 for m in moods if m.emotion in ["sadness", "anger", "fear"])
    neutral_count = sum(1 for m in moods if m.emotion == "neutral")
    average_confidence = round(sum(m.confidence for m in moods) / len(moods), 2) if moods else 0
    average_stress = round(sum((m.stress_level or 0) for m in moods) / len(moods), 1) if moods else 0
    journal_count = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= last_week
    ).count()

    return jsonify({
        "total_posts": len(moods),
        "emotion_breakdown": emotion_count,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "dominant_emotion": dominant,
        "average_confidence": average_confidence,
        "average_stress": average_stress,
        "journal_entries_week": journal_count,
        "suggestion": generate_suggestion(dominant)
    })


# =================================
# EMOTION GRAPH
# =================================
@analysis_bp.route("/emotion-graph", methods=["GET"])
@jwt_required()
def emotion_graph():

    user_id = int(get_jwt_identity())

    moods = Mood.query.filter_by(user_id=user_id).all()

    graph = {}

    for m in moods:
        graph[m.emotion] = graph.get(m.emotion, 0) + 1

    return jsonify(graph)


@analysis_bp.route("/weekly-trends", methods=["GET"])
@jwt_required()
def weekly_trends():

    user_id = int(get_jwt_identity())
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    labels = [d.strftime("%a") for d in days]

    moods = Mood.query.filter(
        Mood.user_id == user_id,
        Mood.created_at >= today - timedelta(days=6)
    ).all()

    emotion_breakdown = {"joy": 0, "love": 0, "sadness": 0, "anger": 0, "fear": 0, "neutral": 0}
    daily_stress = {d: [] for d in days}
    daily_counts = {d: 0 for d in days}

    for m in moods:
        day = m.created_at.date()
        if day in daily_stress:
            daily_stress[day].append(m.stress_level or 0)
            daily_counts[day] += 1
        emotion_breakdown[m.emotion] = emotion_breakdown.get(m.emotion, 0) + 1

    stress_trend = [round(sum(daily_stress[d]) / len(daily_stress[d]), 1) if daily_stress[d] else 0 for d in days]
    entry_counts = [daily_counts[d] for d in days]

    dominant = max(emotion_breakdown, key=emotion_breakdown.get) if any(emotion_breakdown.values()) else "neutral"

    return jsonify({
        "labels": labels,
        "emotion_breakdown": emotion_breakdown,
        "stress_trend": stress_trend,
        "entry_counts": entry_counts,
        "dominant_emotion": dominant
    })


@analysis_bp.route("/entity-summary", methods=["GET"])
@jwt_required()
def entity_summary():
    user_id = int(get_jwt_identity())

    mood_count = Mood.query.filter_by(user_id=user_id).count()
    journal_count = JournalEntry.query.filter_by(user_id=user_id).count()
    notification_count = Notification.query.filter_by(user_id=user_id).count()
    risk = detect_risk(user_id)

    return jsonify({
        "mood_entries": mood_count,
        "journal_entries": journal_count,
        "notifications": notification_count,
        "risk_level": risk.get("risk_level"),
        "risk_message": risk.get("message")
    })


# =================================
# WELLNESS SCORE
# =================================
@analysis_bp.route("/wellness-score", methods=["GET"])
@jwt_required()
def wellness_score():

    user_id = int(get_jwt_identity())

    moods = Mood.query.filter_by(user_id=user_id).order_by(Mood.created_at.desc()).limit(10).all()
    
    if not moods:
        return jsonify({
            "score": 70,
            "trend": "stable",
            "breakdown": {
                "positive_impacts": 0,
                "negative_impacts": 0
            }
        })

    # Calculate score based on recent emotions
    positive_emotions = ["joy", "love"]
    negative_emotions = ["sadness", "anger", "fear"]
    
    positive_count = sum(1 for m in moods if m.emotion in positive_emotions)
    negative_count = sum(1 for m in moods if m.emotion in negative_emotions)
    
    # Base score of 50, +10 for each positive, -10 for each negative
    score = 50 + (positive_count * 10) - (negative_count * 10)
    score = max(0, min(100, score))  # Clamp between 0-100

    # Simple trend calculation (compare first half vs second half)
    mid = len(moods) // 2
    first_half_pos = sum(1 for m in moods[:mid] if m.emotion in positive_emotions)
    second_half_pos = sum(1 for m in moods[mid:] if m.emotion in positive_emotions)
    
    if second_half_pos > first_half_pos:
        trend = "improving"
    elif second_half_pos < first_half_pos:
        trend = "declining"
    else:
        trend = "stable"

    return jsonify({
        "score": score,
        "trend": trend,
        "breakdown": {
            "positive_impacts": positive_count,
            "negative_impacts": negative_count
        }
    })


# =================================
# STRESS LEVEL
# =================================
@analysis_bp.route("/stress-level", methods=["GET"])
@jwt_required()
def stress_level():

    user_id = int(get_jwt_identity())

    moods = Mood.query.filter_by(user_id=user_id).all()

    stress_score = 0

    for m in moods:
        if m.emotion in ["anger", "sadness", "fear"]:
            stress_score += 1

    if stress_score > 5:
        level = "High Stress"
    elif stress_score > 2:
        level = "Moderate Stress"
    else:
        level = "Low Stress"

    return jsonify({
        "stress_score": stress_score,
        "stress_level": level
    })


# =================================
# AI CHATBOT
# =================================
@analysis_bp.route("/chatbot", methods=["POST"])
@jwt_required()
def chatbot():

    data = request.get_json()
    message = data.get("message").lower()

    if "stress" in message:
        reply = "Try deep breathing and taking short breaks."

    elif "sad" in message:
        reply = "Talking to someone you trust can help."

    elif "angry" in message:
        reply = "Step away for a moment and try calming breathing."

    elif "sleep" in message:
        reply = "Maintaining a regular sleep schedule can help."

    else:
        reply = "I'm here to support you. Tell me more."

    return jsonify({"reply": reply})


# =================================
# SOCIAL POSTS ANALYSIS
# =================================
@analysis_bp.route("/analyze-posts", methods=["POST"])
@jwt_required()
def analyze_posts():

    data = request.get_json()
    posts = data.get("posts")

    results = []

    for p in posts:
        result = detect_mood(p)

        results.append({
            "post": p,
            "emotion": result["label"],
            "confidence": result["score"]
        })

    return jsonify(results)


# =================================
# MOBILE USAGE (SIMULATION)
# =================================
@analysis_bp.route("/mobile-usage", methods=["GET"])
@jwt_required()
def mobile_usage():

    usage = {
        "Instagram": "2 hours",
        "WhatsApp": "1.5 hours",
        "YouTube": "3 hours",
        "Twitter": "45 minutes"
    }

    return jsonify({
        "daily_usage": usage,
        "recommendation": "Limit social media to 2 hours per day for better mental health."
    })


# =================================
# JOURNAL ENTRIES
# =================================
@analysis_bp.route("/journal", methods=["GET", "POST"])
@jwt_required()
def journal():
    user_id = int(get_jwt_identity())

    if request.method == "POST":
        data = request.get_json() or {}
        title = data.get("title", "").strip()
        content = data.get("content", "").strip()

        if not content:
            return jsonify({"message": "Journal content cannot be empty."}), 400

        result = detect_mood(content)
        entry = JournalEntry(
            user_id=user_id,
            title=title if title else None,
            content=content,
            emotion=result["label"],
            confidence=result["score"]
        )
        db.session.add(entry)
        db.session.commit()

        return jsonify({
            "message": "Journal saved successfully.",
            "emotion": result["label"],
            "confidence": result["score"]
        }), 201

    entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).limit(10).all()
    return jsonify([
        {
            "id": e.id,
            "title": e.title,
            "content": e.content,
            "emotion": e.emotion,
            "confidence": e.confidence,
            "date": e.created_at.isoformat()
        }
        for e in entries
    ])


# =================================
# NOTIFICATIONS
# =================================
@analysis_bp.route("/notifications", methods=["GET"])
@jwt_required()
def notifications():
    user_id = int(get_jwt_identity())

    # Always generate notifications based on recent moods
    moods = Mood.query.filter_by(user_id=user_id).order_by(Mood.created_at.desc()).limit(5).all()
    
    # Clear old notifications and create new ones
    Notification.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    if moods:
        for mood in moods:
            if mood.emotion in ["sadness", "anger", "fear"]:
                message = f"Your recent mood was {mood.emotion}. Take a short break if you need one."
                notif_type = "alert"
            else:
                message = f"Great job! Keep the positive energy going after feeling {mood.emotion}."
                notif_type = "info"
            
            notification = Notification(
                user_id=user_id,
                message=message,
                type=notif_type
            )
            db.session.add(notification)
        db.session.commit()
    
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()
    
    if not notifs:
        return jsonify([
            {
                "id": None,
                "message": "Welcome to MindScan AI! Start journaling to receive personalized alerts.",
                "type": "info",
                "date": None
            }
        ])

    return jsonify([
        {
            "id": n.id,
            "message": n.message,
            "type": n.type,
            "date": n.created_at.isoformat()
        }
        for n in notifs
    ])


@analysis_bp.route("/risk-report", methods=["GET"])
@jwt_required()
def risk_report():

    user_id = int(get_jwt_identity())

    result = detect_risk(user_id)

    return jsonify(result)


@analysis_bp.route("/social", methods=["POST", "OPTIONS"])
def analyze_social():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()
    text = data.get("text")

    result = detect_mood(text)

    return jsonify(result)