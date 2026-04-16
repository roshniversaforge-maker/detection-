import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# We safely wrap the download inside a try-except so it downloads smoothly if missing
for package in ['stopwords', 'punkt', 'punkt_tab']:
    try:
        if package == 'stopwords':
            nltk.data.find('corpora/stopwords')
        else:
            nltk.data.find(f'tokenizers/{package}')
    except Exception:
        nltk.download(package, quiet=True)

STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    """
    Lowercase the text, remove special characters, and remove stopwords.
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove punctuation and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenization and Stopword removal
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in STOPWORDS]
    
    return " ".join(filtered_tokens)
