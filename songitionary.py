from rauth import OAuth2Service, OAuth2Session
from bs4 import BeautifulSoup
import re
import json

def getQueryParams(queryPhrase):
    return queryPhrase.replace(" ","%20")

def initializeSession(bearer):
    return OAuth2Session(123,123,bearer)

def getArtistId(session, artistName):
    queryPhrase = getQueryParams(artistName)

    uri = "https://api.genius.com/search?q={0}".format(queryPhrase)
    
    response = session.request("get", uri)

    parsedResponse = response.json()

    for song in parsedResponse["response"]["hits"]:
        if song["result"]["primary_artist"]["name"].lower() == artistName.lower():
            id = song["result"]["primary_artist"]["id"]
            print("Nazwa wykonawcy to: {0}".format(song["result"]["primary_artist"]["name"]))
            return id
    return None     
    
def getAllSongAddresses(session, artistId):

    songAddresses = set()
    next_page=1

    while next_page != None:
        print("*",end='')  
        uri = "https://api.genius.com/artists/{0}/songs?per_page=50&page={1}".format(artistId,next_page)
        response = session.request("get", uri)
        parsedResponse = response.json()
        songs = parsedResponse["response"]["songs"]
        next_page = parsedResponse["response"]["next_page"]
        for song in songs:
            songAddresses.add(song["path"])
    print("")
    print("Znaleziono {0} piosenek.".format(len(songAddresses)))
    return songAddresses

def getSongLyrics(session, path):
    print("PROCESSING SONG: {0}".format(path))
    uri = "https://genius.com{0}".format(path)
    page = session.request("get", uri)
    html = BeautifulSoup(page.text, "html.parser")

    for br in html.find_all("br"):
        br.replace_with("\n")

    lyricsParts = html.find_all("div",{"data-lyrics-container":True})
    lyrics = ""
    for part in lyricsParts:
        text = part.get_text()
        print(text)
        text = re.sub("\[( *(\w|&|:|-)* *)*\]|,|!|\?|\.|\(|\)", "", text)
        text = text.lower()
        lyrics += text
    return lyrics

def countWords(text):
    counter = {}
    text = text.split()
    for word in text:
        amount = counter.get(word)
        amount = 1 if (amount == None) else amount + 1
        counter.update({word:amount})
    return counter

def addToDictionary(main,dict2):
    for word in dict2:
        value = main.get(word)
        value = dict2[word] if (value == None) else value+dict2[word]
        main.update({word:value})


session = initializeSession("BEARER TOKEN")
name = input("PODAJ WYKONAWCE: ")
id = getArtistId(session, name)
if(id == None):
    print("Nie znaleziono artysty.")
    exit()
print("Jego Id to {0}".format(id))
allWords = {}
addresses = getAllSongAddresses(session, id)
for address in addresses:
    lyrics = getSongLyrics(session,address)
    #print(lyrics)
    counter = countWords(lyrics)
    #print(counter)
    addToDictionary(allWords, counter)
print(allWords)