from rauth import OAuth2Service, OAuth2Session
from bs4 import BeautifulSoup
import re
import json

def getQueryParams(queryPhrase):
    return queryPhrase.replace(" ","%20")

def initializeSession(bearer):
    return OAuth2Session(123,123,bearer)

def getArtistId(session, queryPhrase):
    queryPhrase = getQueryParams(queryPhrase)
    uri = "https://api.genius.com/search?q={0}".format(queryPhrase)
    
    response = session.request("get", uri)

    parsedResponse = response.json()
    return(parsedResponse["response"]["hits"][0]["result"]["primary_artist"]["id"])
    
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
    uri = "https://genius.com{0}".format(path)
    page = session.request("get", uri)
    html = BeautifulSoup(page.text, "html.parser")

    for br in html.find_all("br"):
        br.replace_with("\n")

    lyricsParts = html.find_all("div",{"data-lyrics-container":True})
    lyrics = ""
    for part in lyricsParts:
        text = part.get_text()
        text = re.sub("\[( *(\w|&|:|-)* *)*\]", "", text)
        text = text.replace("(","")
        text = text.replace(")","")
        text = text.replace(",","")
        text = text.replace(".","")
        text = text.replace("?","")
        text = text.replace("!","")
        text = text.lower()
        lyrics += text
    return lyrics


session = initializeSession("BEARER TOKEN")
name = input("PODAJ WYKONAWCE: ")
id = getArtistId(session, name)
print("Jego Id to {0}".format(id))
addresses = getAllSongAddresses(session, id)
lyrics = getSongLyrics(session,addresses.pop())
print(lyrics)