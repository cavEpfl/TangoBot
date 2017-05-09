import urllib
import requests
import configparser
from bs4 import BeautifulSoup
from datetime import datetime
from difflib import Differ


config = configparser.ConfigParser()
config.read('config.ini')

#Login data
user=config['DEFAULT']['userName']
passw=config['DEFAULT']["password"]
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'

#Replace this using listepagesbot.py to get all page names to go through
names=['Naissance']

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

    # 1. retrouver le contenu et l'imprimer

    for name in names:
        result = requests.post(baseurl + 'api.php?action=query&titles=' + name + '&export&exportnowrap')
        soup = BeautifulSoup(result.text, "lxml")
        # soup=BeautifulSoup(result.text)
        dataStr = ''
        for primitive in soup.findAll("text"):
            if primitive.string is not None:
                dataStr += primitive.string

        entries = getEntries(dataStr)
        removeDuplicates(entries)

def getEntries(data):
    lines = data.split('\n')
    entries = []
    for line in lines:
        if isValidEntry(line):
            entries.append(line)
    return entries


def isValidEntry(entry):
    if entry[0:3] == '*[[' and (entry[3:7] + entry[8:10] + entry[11:13]).isdigit() and entry[13:15] == ']]' and entry[7] == '.' and entry[10] == '.':
        return True
    else:
        return False


def removeDuplicates(entries):

    finalEntries = list(set(entries)).sort(key=lambda x: datetime.strptime(cleanDate(x), '%Y%m%d'))

    print(finalEntries)

    code2 = ''
    for entry in finalEntries:
        code2 += entry

    print("\nAfter:\n" + code2)

def cleanDate(str):

    finalStr = ''
    dateStr = str.partition("/")[0]
    finalStr.join(e for e in dateStr if e.isalnum())
    print(finalStr)
    return "20000203"

main()