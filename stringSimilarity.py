import nltk
import string
import math

from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

stemmer = FrenchStemmer()

def get_tokens(entries):
    token_dict = {}
    for i,entry in enumerate(entries):
        #to lowerCase
        lowers = entry.lower()
        #Remove any punctuation with a translator
        translator = str.maketrans('', '', string.punctuation)
        #Splits string in words

        token_dict[i] = lowers.translate(translator)
    return token_dict

#Stemming words: reducing inflected (or sometimes derived) words to their word stem, base or root form
def stem_tokens(tokens, stemmer):
    stemmed = []

    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    filtered = [w for w in tokens if not w in stopwords.words('french')]
    stems = stem_tokens(filtered, stemmer)
    return stems

def similarityPairs(baseStrings):

    setLength = len(baseStrings)

    tokens = get_tokens(baseStrings)
    #Removing unnecessary words which bring no information
    tfidf = TfidfVectorizer(tokenizer=tokenize)
    tfs = tfidf.fit_transform(tokens.values())

    cosine_similarites = []
    avgCosine = 0


    for i in range (0, setLength):
        # To find the cosine distances of one document and all of the others we
        # compute the dot products of the first vector with all of the others.
        # We slice the tfs matrix row-wise to get a submatrix with a single row: the first vector
        # cosine_similarites = linear_kernel(tfs[4:5], tfs).flatten()
        cosine_similarites.append(linear_kernel(tfs[i:i+1], tfs).flatten())
        avgCosine += sum(cosine_similarites[i])

    totalLength = setLength*setLength
    avgCosine = avgCosine / (totalLength)

    sumOfSquares = 0

    for array in cosine_similarites:
        for x in array:
            diff = x-avgCosine
            sumOfSquares += diff*diff

    stdDeviation = math.sqrt(sumOfSquares/(totalLength-1.0))

    #min=avg(sim)+α⋅σ(sim)
    threshold = avgCosine + 0.75*stdDeviation
    threshold1 = 0.5

    duplicatePairs = []

    halfLength = int(math.floor(setLength/2))

    for i in range(0, halfLength):
        for j in range(0, setLength):
            if i != j and cosine_similarites[i][j] > threshold1:
                duplicatePairs.append((i, j))

    return duplicatePairs
