import nltk
import string
import math

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
    #All the stop words are stripped away since they don't bring anymore information
    filtered = [w for w in tokens if not w in stopwords.words('french')]
    stems = stem_tokens(filtered, stemmer)
    return stems

#Creates Pairs of the indexes of similar entries
def similarityPairs(baseStrings):

    setLength = len(baseStrings)

    tokens = get_tokens(baseStrings)

    # Tf–idf, short for term frequency–inverse document frequency
    # reflects  how important a word is to a document in a collection or corpus.
    # The tf-idf value increases proportionally to the number of times a word appears in the document,
    # but is often offset by the frequency of the word in the corpus,
    # which helps to adjust for the fact that some words appear more frequently in general.
    tfidf = TfidfVectorizer(tokenizer=tokenize)
    tfs = tfidf.fit_transform(tokens.values())

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

    totalLength = setLength*setLength
    avgCosine = avgCosine / (totalLength)

    sumOfSquares = 0

    #Standard deviation formula
    for array in cosine_similarites:
        for x in array:
            diff = x-avgCosine
            sumOfSquares += diff*diff

    stdDeviation = math.sqrt(sumOfSquares/(totalLength-1.0))

    #Threshold of similarity is chosen here
    #min=avg(sim)+α⋅σ(sim)
    threshold = avgCosine + 0.75*stdDeviation
    #This threshold corresponds better to the dataset of wikipast
    threshold1 = 0.5

    duplicatePairs = []

    #Only need to iterate on half of list so we don't count same pairs twice
    halfLength = int(math.floor(setLength/2))

    #Creation of Index Pairs satisfying threshold
    for i in range(0, halfLength):
        for j in range(0, setLength):
            if i != j and cosine_similarites[i][j] > threshold1:
                duplicatePairs.append((i, j))

    return duplicatePairs
