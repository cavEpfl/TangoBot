import requests
import configparser
import stringSimilarity
from bs4 import BeautifulSoup
from re import findall

config = configparser.ConfigParser()
config.read('config.ini')

#Login data
user=config['DEFAULT']['userName']
passw=config['DEFAULT']["password"]
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'

#Replace this using listepagesbot.py to get all page names to go through
names=['TangoBotTest']

# Login request
payload={'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
r1=requests.post(baseurl + 'api.php', data=payload)

#login confirm
login_token=r1.json()['query']['tokens']['logintoken']
payload={'action':'login','format':'json','utf8':'','lgname':user,'lgpassword':passw,'lgtoken':login_token}
r2=requests.post(baseurl + 'api.php', data=payload, cookies=r1.cookies)

#get edit token2
params3='?format=json&action=query&meta=tokens&continue='
r3=requests.get(baseurl + 'api.php' + params3, cookies=r2.cookies)
edit_token=r3.json()['query']['tokens']['csrftoken']

edit_cookie=r2.cookies.copy()
edit_cookie.update(r3.cookies)

def main():

    #Iterating through pages
    for name in names:
        result = requests.post(baseurl + 'api.php?action=query&titles=' + name + '&export&exportnowrap')
        soup = BeautifulSoup(result.text, "lxml")
        # soup=BeautifulSoup(result.text)
        dataStr = ''
        for primitive in soup.findAll("text"):
            if primitive.string is not None:
                dataStr += primitive.string

        #Seperation of valid entries and normal text
        entries, nonEntries = getEntries(dataStr)
        finalEntries = removeDuplicates(entries, name)

        newContent = nonEntries + finalEntries
        #Text is reorganized in corrected order with non-entry text
        newContent.sort(key=lambda x: x[0])

        updateContent('\n'.join([e for (i,e) in newContent]), name)

#Returns all the entries as a list from the text data
def getEntries(data):
    lines = data.split('\n')
    i = 0
    entries = []
    nonEntries = []
    for line in lines:
        if isValidEntry(line):
            entries.append((i, line))
        else:
            nonEntries.append((i, line))
        i = i + 1
    return (entries, nonEntries)

#Checks if entry is a correctly formated entry
def isValidEntry(entry):
    #Remove any spaces to get correct format
    entry = entry.replace(" ", "")
    if entry[0:3] == '*[[' and (entry[3:7] + entry[8:10] + entry[11:13]).isdigit() and entry[13:15] == ']]' and entry[7] == '.' and entry[10] == '.':
        return True
    elif entry[0:3] == '*[[' and entry[3:7].isdigit() and entry[7:12] == ']]/-.':
        return True
    else:
        return False

#Removes duplicates in list of entries
def removeDuplicates(entries, pageTitle):

    entriesNoIndex = [e for (i, e) in entries]
    #Duplicate Pairs are computed
    duplicateIndexes = stringSimilarity.similarityPairs(entriesNoIndex)
    entriesToRemove = []

    for i in range(0, len(entries)):
        duplicatesForI = [x for x in duplicateIndexes if i in x]
        #For each entry in conflict the number of hyperlink is calculated
        duplicates = list(set([(getNumberOfHyperLinks(entriesNoIndex[index], pageTitle), index) for pair in duplicatesForI for index in pair]))
        duplicates.sort(key=lambda x: x[0], reverse=True)

        #The duplicate with the most hyperlinks stays the others are removed
        for (_, index) in duplicates[1:]:
            entriesToRemove.append(entries[index])

    finalEntries = []
    for x in entries:
        #All duplicate entries must be removed in entries
        if x in entriesToRemove:
            entriesToRemoveNew = []
            found = False
            for e in entriesToRemove:
                if x == e and not found:
                    found = True
                else:
                    entriesToRemoveNew.append(e)
            entriesToRemove = entriesToRemoveNew
        else:
            finalEntries.append(x)

    return finalEntries

#Returns the number of hyperlinks in a given entry while ignoring the pageTitle as a valid hyperlink
def getNumberOfHyperLinks(entry, pageTitle):
    hyperLinks = findall('\[\[(.*?)\]\]', entry)
    hyperLinks = set([x.split('|')[0] for x in hyperLinks])
    if pageTitle in hyperLinks:
        hyperLinks.remove(pageTitle)
    return len(hyperLinks)

#Cleans date from special characters
def cleanDate(str):
    dateStr = str.partition("/")[0]
    #removes all special characters
    return ''.join(e for e in dateStr if e.isalnum())

#Updates the page online
def updateContent(content, name):
    payload = {'action': 'edit', 'assert': 'user', 'format': 'json', 'utf8': '', 'text': content, 'summary': summary,
               'title': name, 'token': edit_token}
    r4 = requests.post(baseurl + 'api.php', data=payload, cookies=edit_cookie)

main()