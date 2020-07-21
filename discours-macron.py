# To do web requests in python, use "requests" library
# https://requests.readthedocs.io/en/master/user/quickstart/#make-a-request
import requests
# To navigate in the dom and get the needed info, use "BeautifulSoup" library
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup
# To create a csv through a datagrame, use "pandas" library
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
import pandas as pd
import numpy as np

# Library to save data
import pickle
import os.path

import time
import random
TIME_MIN_RANDOM_SEC = 2
TIME_MAX_RANDOM_SEC = 6

# Website used : vie-publique.fr
# Config headers and cookies for this website
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
cookies = {'cookie-agreed': '2'}

## Goal number 1 : getting all the "discours" links of Macron
links = []
if os.path.isfile('links.pickle'):
    with open('links.pickle','rb') as fp:
        links = pickle.load(fp)
else:
    name = "Macron"

    # Preparing the request
    page = 0
    maxPage = 0

    while page <= maxPage:
        url = "https://www.vie-publique.fr/recherche?search_api_fulltext=" + name + "&sort_by=field_update_date&f%5B0%5D=categories%3Adiscours&page=" + str(page)
        # Making the request
        r = requests.get(url, headers=headers, cookies=cookies)

        # Ckecking the request
        if r.status_code != 200:
            print('Error webpage status code : ' + r.status_code)
            r.raise_for_status()
            raise

        # Parse the dom
        soup = BeautifulSoup(r.text, 'html5lib') 
        # Getting the number of page from the number of results
        if maxPage == 0:
            searchCount = soup.find("p", class_="count-search")
            nbResultsByPage = 10
            nbTotalResults = searchCount.text.split(' ')[0]
            maxPage = int(int(nbTotalResults)/nbResultsByPage)
            print("Nb page: ", maxPage)
            
            #only for testing
            #maxPage = 1
        
        # Getting the links from the current page
        searchA = soup.find_all("a", class_="link-multiple")
        for tagA in searchA:
            links.append(tagA.get('href'))
        
        page+=1
        time.sleep(random.randint(TIME_MIN_RANDOM_SEC,TIME_MAX_RANDOM_SEC))
        print(page)

    print("Downloading links done")
    with open('links.pickle','wb') as fp:
        pickle.dump(links,fp)
    print("Saving links into links.pickle done")

#print(links)
# Creating a new DataFrame
# Columns : title: str, date: datetime, text: str, speakers: str (delimiter: ';'), monologue: true/false, 
# theme: str, occasion: str, tags: str (delimiter: ';', url)

df = None
if os.path.isfile('discours_macron.pickle'):
    df = pd.read_pickle('discours_macron.pickle')
else:
    df = pd.DataFrame(columns=['title','date','text','speakers','monologue','theme','occasion','tags','url'])

i = 0
for url in links[len(df):]:
    i+=1
    print(i)
    # only for testing
    #if i == 5:
    #    break

    r = requests.get(url, headers=headers, cookies=cookies)

    # Ckecking the request
    if r.status_code != 200:
        print('Error webpage status code : ' + r.status_code)
        r.raise_for_status()
        raise

    # Parse the dom
    soup = BeautifulSoup(r.text, 'html5lib')

    title = soup.h1.text.strip()
    
    dateSoup = soup.find("div", class_="dateBox")
    date = dateSoup.p.span.time.get("datetime") if dateSoup else np.nan
    
    # get the text, replace <br> with \n (use text.replace("\n", " ") to remove the "\n"), also escape the apostrophe ie. replace ' by \'
    textSoup = soup.find("span", class_="field--name-field-texte-integral")
    text = textSoup.text if textSoup else np.nan
    """
    # Other method to get all the text
    t = soup.find("span", class_="field--name-field-texte-integral").p.stripped_strings
    text = [txt for txt in t]
    " ".join(text)
    """
    
    speakersSoup = soup.find("ul", class_="line-intervenant")
    speakersArray = speakersSoup.find_all("li") if speakersSoup else False
    speakers = np.nan
    monologue = np.nan
    if speakersArray:
        speakers = ""
        for speaker in speakersArray:
            speakers += speaker.a.text + ";"
        speakers = speakers[:-1] # Removing the last ";" (unuseful)
        monologue = True if len(speakers.split(";")) == 1 else False
    
    themeSoup = soup.find("div", class_="thematicBox")
    theme = np.nan
    if themeSoup:
        theme = ""
        for t in themeSoup.find_all("li"):
            theme += t.a.text + ";"
        theme = theme[:-1]
    
    occasionSoup = soup.find("span", class_="field--name-field-circonstance")
    occasion = occasionSoup.text if occasionSoup else np.nan
    
    tagsSoup = soup.find("div", class_="tagsBox")
    tags = np.nan
    if tagsSoup:
        tags = ""
        for t in tagsSoup.find_all("li"):
                tags += t.a.text + ";"
        tags = tags[:-1]
    # other method :
    # tags = soup.find("div", class_="tagsBox").ul.text.strip().replace("  ", "").replace("\n\n", "").replace("\n",";")

    # add line
    df = df.append({'title': title,'date': date,'text': text,'speakers': speakers,'monologue': monologue,
                    'theme': theme,'occasion': occasion,'tags': tags, 'url': url}, ignore_index=True)
    
    df.to_pickle("discours_macron.pickle")
    time.sleep(random.randint(TIME_MIN_RANDOM_SEC,TIME_MAX_RANDOM_SEC))

print("Downloading discours done")
df.to_csv("discours_macron.csv", index = False)
print("Writing df in csv done")


