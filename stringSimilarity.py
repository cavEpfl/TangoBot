import nltk
import string

from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

#Stemming is the process of linguistic normalisation,
# in which the variant forms of a word are reduced to a common form
# Here we use a FrenchStemmer from nltk
stemmer = FrenchStemmer()

#Returns all the entries in lower case stripped of special characters and punctuation
def get_tokens(entries):
    token_dict = {}
    for i,entry in enumerate(entries):
        #to lowerCase
        lowers = entry.lower()
        #Remove any punctuation with a translator
        translator = str.maketrans('', '', string.punctuation)
        token_dict[i] = lowers.translate(translator)
    return token_dict

#Stemming words: reducing inflected (or sometimes derived) words to their word stem, base or root form
def stem_tokens(tokens, stemmer):
    stemmed = []

    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#Extracts all the words of a given string
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    tokensClean = [str for str in tokens if not str.startswith("http")]
    #All the stop words are stripped away since they don't bring anymore information
    filtered = [w for w in tokensClean if not w in stopwords.words('french')]
    stems = stem_tokens(filtered, stemmer)
    return stems

#Creates Pairs of the indexes of similar entries
def similarityPairs(baseStrings):

    setLength = len(baseStrings)

    if setLength == 0:
        return []

    tokens = get_tokens(baseStrings)

    if len(tokens) == 0:
        return []

    # Tf–idf, short for term frequency–inverse document frequency
    # reflects  how important a word is to a document in a collection or corpus.
    # The tf-idf value increases proportionally to the number of times a word appears in the document,
    # but is often offset by the frequency of the word in the corpus,
    # which helps to adjust for the fact that some words appear more frequently in general.
    try:
        tfidf = TfidfVectorizer(tokenizer=tokenize)
        tfs = tfidf.fit_transform(tokens.values())
    except ValueError:
        print(tokens)
        print(baseStrings)
    #Cosine similarity is a measure of similarity between two non-zero vectors of
    # an inner product space that measures the cosine of the angle between them.
    cosine_similarites = []
    avgCosine = 0

    for i in range (0, setLength):
        # To find the cosine distances of one document and all of the others we
        # compute the dot products of the first vector with all of the others.
        # We slice the tfs matrix row-wise to get a submatrix with a single row: the first vector
        cosine_similarites.append(linear_kernel(tfs[i:i+1], tfs).flatten())
        avgCosine += sum(cosine_similarites[i])

    #Threshold of similarity is chosen here
    #This threshold corresponds better to the dataset of wikipast
    threshold1 = 0.7

    duplicatePairs = []

    #Creation of Index Pairs satisfying threshold
    for i in range(0, setLength):
        for j in range(0, setLength):
            if i != j and cosine_similarites[i][j] > threshold1:
                duplicatePairs.append((i, j))

    return list(set([tuple(sorted(item)) for item in duplicatePairs]))