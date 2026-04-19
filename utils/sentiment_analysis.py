from textblob import TextBlob

def get_sentiment(text):
    """
    Returns the sentiment of a text: 'Positive', 'Negative', or 'Neutral'.
    """
    if not text:
        return 'Neutral'
        
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    if polarity > 0.05:
        return 'Positive'
    elif polarity < -0.05:
        return 'Negative'
    else:
        return 'Neutral'
