import sys
import re
import numpy as np
import spacy
from nltk.stem import WordNetLemmatizer 

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from string import punctuation, printable
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS


## count vectorizer expects a list of strings
text1 = "oh the thinks you can thing if only you try"
text2 = "you can think up a guff going by if you try"
text3 = "i am a guff you are a guff we are all guffs"


STOPLIST = ENGLISH_STOP_WORDS
STOPLIST = set(list(STOPLIST) + ["foo"])

if not 'nlp' in locals():
    print("Loading English Module...")
    nlp = spacy.load('en')


def nltk_lemmatize(doc,stop_words=None):
    
    lemmatizer = WordNetLemmatizer() 
      
    if not stop_words:
        stop_words = set([])
  
    ## ensure working with string
    doc = str(doc)
    print(doc)
    
    # First remove punctuation form string
    if sys.version_info.major == 3:
        PUNCT_DICT = {ord(punc): None for punc in punctuation}
        doc = doc.translate(PUNCT_DICT)

    # remove unicode
    doc = "".join([char for char in doc if char in printable])
            
    # Lemmatize and lower text
    print(doc)
    tokens = [re.sub("\W+","",lemmatizer.lemmatize(token.lower())) for token in doc]
    tokens = [t for t in tokens if len(t) > 1]
    
    return ' '.join(w for w in tokens if w not in stop_words)  

        
def spacy_lemmatize(doc, stop_words=None):
    """
    takes a list of strings where each string is a document
    returns a processed list of strings
    """

    if not stop_words:
        stop_words = set([])
  
    ## ensure working with string
    doc = str(doc)

    # First remove punctuation form string
    if sys.version_info.major == 3:
        PUNCT_DICT = {ord(punc): None for punc in punctuation}
        doc = doc.translate(PUNCT_DICT)

    # remove unicode
    clean_doc = "".join([char for char in doc if char in printable])
            
    # Run the doc through spaCy
    doc = nlp(clean_doc)

    # Lemmatize and lower text
    tokens = [re.sub("\W+","",token.lemma_.lower()) for token in doc ]
    tokens = [t for t in tokens if len(t) > 1]
    
    return ' '.join(w for w in tokens if w not in stop_words)  


corpus = [text1,text2,text3]
s_processed = [spacy_lemmatize(doc, STOPLIST) for doc in corpus]
n_processed = [nltk_lemmatize(doc, STOPLIST) for doc in corpus]

for c,doc in enumerate(corpus):
    print('orig: ', doc)
    print('spacy:', s_processed[c])
    
sys.exit()

## count vectorizer for 1-grame
vectorizer = CountVectorizer()
counts = vectorizer.fit_transform(corpus)
features = vectorizer.get_feature_names()
matrix = counts.toarray()
print(features)
print(matrix)

## count vectorizer for bi-grams
bigram_vectorizer = CountVectorizer(ngram_range=(1, 2),token_pattern=r'\b\w+\b', min_df=1)
counts = bigram_vectorizer.fit_transform(corpus)
features = bigram_vectorizer.get_feature_names()
matrix = counts.toarray() 
print(features)
print(matrix)

## use tfidf to transform the occurances into relative frequencies
transformer = TfidfTransformer(smooth_idf=False)
tfidf = transformer.fit_transform(counts)
tfidf_matrix = tfidf.toarray()
print(np.round(tfidf_matrix,2))

## the same result can be obtained with the tfidf class
## Occurrence count is a good start but there is an issue: l
## longer documents will have higher average count values than shorter documents, even though they might talk about the same topics.

