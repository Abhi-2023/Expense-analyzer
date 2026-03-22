import re
import nltk
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize

stop_words = STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "it", "this", "that"
}

def text_preprocessing(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z]", " ", text)
    text = re.sub(r"\s+" , " ", text).strip()
    tokenized = word_tokenize(text)
    filtered_tokens = [word for word in tokenized if word not in stop_words]
    text = " ".join(filtered_tokens)
    return text