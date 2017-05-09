import urllib
import requests
import configparser
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config = config.read('config.ini')

user=config['wikipast.epfl.ch']['userName']
passw=config['wikipast.epfl.ch']['password']
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'
names=['Madame X','Monsieur Y']

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