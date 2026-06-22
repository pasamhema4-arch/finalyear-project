def detect_mood(text):
    text = text.lower()

    # Expanded keyword lists for better detection
    sadness_keywords = ['sad', 'depressed', 'unhappy', 'down', 'blue', 'miserable', 'gloomy', 'heartbroken', 'disappointed', 'lonely']
    joy_keywords = ['happy', 'good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic', 'excited', 'joyful', 'cheerful', 'delighted']
    anger_keywords = ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'rage', 'hate', 'pissed']
    fear_keywords = ['fear', 'scared', 'afraid', 'anxious', 'worried', 'terrified', 'nervous', 'panic', 'frightened']
    love_keywords = ['love', 'loving', 'caring', 'affectionate', 'romantic', 'passionate', 'fond', 'adoring']

    if any(word in text for word in sadness_keywords):
        return {"label": "sadness", "score": 0.8}
    elif any(word in text for word in joy_keywords):
        return {"label": "joy", "score": 0.8}
    elif any(word in text for word in anger_keywords):
        return {"label": "anger", "score": 0.8}
    elif any(word in text for word in fear_keywords):
        return {"label": "fear", "score": 0.8}
    elif any(word in text for word in love_keywords):
        return {"label": "love", "score": 0.8}
    else:
        return {"label": "neutral", "score": 0.5}
