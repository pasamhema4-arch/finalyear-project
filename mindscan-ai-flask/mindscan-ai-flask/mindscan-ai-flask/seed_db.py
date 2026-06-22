import random
from datetime import datetime, timedelta
from app import app
from models import db, User, Mood, JournalEntry

# Dummy Data Configuration
mock_user_email = "test@example.com"
mock_user_pass = "password123"

emotions = [
    {"label": "joy", "score": 0.95},
    {"label": "joy", "score": 0.88},
    {"label": "love", "score": 0.92},
    {"label": "fear", "score": 0.80},
    {"label": "sadness", "score": 0.85},
    {"label": "anger", "score": 0.75},
    {"label": "neutral", "score": 0.60}
]

journal_content = [
    "Had a great day at work today. Everything went smoothly.",
    "Feeling a little overwhelmed with the upcoming deadlines.",
    "Spent time with family. It was very refreshing and peaceful.",
    "I'm feeling quite anxious about the presentation tomorrow.",
    "Just a normal day, nothing special happened.",
    "Woke up feeling extremely tired and sad for no reason.",
    "I'm so angry at how they treated me at the store today!"
]

def map_emotion_to_stress(label):
    if label in ['sadness', 'anger', 'fear']:
        return random.uniform(6.0, 9.5)
    elif label in ['joy', 'love']:
        return random.uniform(1.0, 3.5)
    return random.uniform(3.0, 6.0)

def seed_data():
    with app.app_context():
        print("Initializing the database...")
        db.create_all()

        print("Creating mock user...")
        user = User.query.filter_by(email=mock_user_email).first()
        if not user:
            user = User(username="Test User", email=mock_user_email)
            user.set_password(mock_user_pass)
            db.session.add(user)
            db.session.commit()
            print(f"Created user: {mock_user_email} / {mock_user_pass}")
        else:
            print("User already exists.")
            # Clear old data for a fresh seed
            Mood.query.filter_by(user_id=user.id).delete()
            JournalEntry.query.filter_by(user_id=user.id).delete()
            db.session.commit()

        print("Seeding mood and journal data over the past 30 days...")
        now = datetime.now()  # Use timezone-naive datetime
        for i in range(30):
            # Generate a random date within the last 30 days
            delta_days = 30 - i
            record_date = now - timedelta(days=delta_days, hours=random.randint(0, 12))

            # Pick a random emotion for the day
            emotion = random.choice(emotions)
            
            # Create a mood log
            mood = Mood(
                user_id=user.id,
                text="Mock mood log for the day.",
                emotion=emotion["label"],
                confidence=emotion["score"],
                stress_level=map_emotion_to_stress(emotion["label"]),
                created_at=record_date
            )
            db.session.add(mood)

            # Sometime add a journal entry too
            if random.random() > 0.3:
                j_emotion = random.choice(emotions)
                journal = JournalEntry(
                    user_id=user.id,
                    title=f"Day {i+1} thoughts",
                    content=random.choice(journal_content),
                    emotion=j_emotion["label"],
                    confidence=j_emotion["score"],
                    created_at=record_date
                )
                db.session.add(journal)

        db.session.commit()
        print("Data seeding completed! You can now log in with test@example.com / password123")

if __name__ == "__main__":
    seed_data()
