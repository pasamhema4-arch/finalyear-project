from textblob import TextBlob

def analyze_social_posts(posts):
    """
    posts: list of strings (social media posts)
    """
    if not posts:
        return 0.0

    sentiments = [TextBlob(post).sentiment.polarity for post in posts]
    return sum(sentiments)/len(sentiments)