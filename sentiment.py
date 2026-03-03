from textblob import TextBlob
import nltk

# Ensure required NLTK data is present
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # range -1 to 1