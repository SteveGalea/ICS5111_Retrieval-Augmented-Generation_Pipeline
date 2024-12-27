
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re
from nltk.stem import WordNetLemmatizer
import neattext.functions as nfx

nltk.download('wordnet')
nltk.download('punkt')
lemmatizer = WordNetLemmatizer()
tknzr = nltk.tokenize
def lemmatize_text(text):
    return [lemmatizer.lemmatize(w) for w in tknzr.word_tokenize(text)]

def lemmatise(df):
    corpus = df['full_text'].astype(str)
    corpus = corpus.apply(nfx.remove_stopwords)
    corpus = corpus.apply(nfx.remove_special_characters)
    corpus = corpus.apply(nfx.remove_multiple_spaces)
    corpus = corpus.str.lower()
    corpus = corpus.apply(lemmatize_text)
    df['full_text'] = corpus

