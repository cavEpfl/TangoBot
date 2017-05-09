# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
baseurl='http://wikipast.epfl.ch/wikipast/'

protected_logins=["Frederickaplan","Maud","Vbuntinx","Testbot","IB","SourceBot","PageUpdaterBot","Orthobot","BioPathBot","ChronoBOT","Amonbaro","AntoineL","AntoniasBanderos","Arnau","Arnaudpannatier","Aureliver","Brunowicht","Burgerpop","Cedricviaccoz","Christophe","Claudioloureiro","Ghislain","Gregoire3245","Hirtg","Houssm","Icebaker","JenniCin","JiggyQ","JulienB","Kl","Kperrard","Leandro Kieliger","Marcus","Martin","MatteoGiorla","Mireille","Mj2905","Musluoglucem","Nacho","Nameless","Nawel","O'showa","PA","Qantik","QuentinB","Raphael.barman","Roblan11","Romain Fournier","Sbaaa","Snus","Sonia","Tboyer","Thierry","Titi","Vlaedr","Wanda"]
depuis_date='2017-05-02T16:00:00Z'

liste_pages=[]
for user in protected_logins:
    result=requests.post(baseurl+'api.php?action=query&list=usercontribs&ucuser='+user+'&format=xml&ucend='+depuis_date)
    soup=BeautifulSoup(result.content,'lxml')
    for primitive in soup.usercontribs.findAll('item'):
        liste_pages.append(primitive['title'])
        print(primitive['title'])

liste_pages=list(set(liste_pages))
for page in liste_pages:
    print(page)
print('longueur: '+str(len(liste_pages)))