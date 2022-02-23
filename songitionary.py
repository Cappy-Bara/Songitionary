from rauth import OAuth2Service, OAuth2Session
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
    next_page=1;

    while next_page != None:  
        uri = "https://api.genius.com/artists/{0}/songs?per_page=50&page={1}".format(artistId,next_page)
        response = session.request("get", uri)
        parsedResponse = response.json()
        songs = parsedResponse["response"]["songs"]
        next_page = parsedResponse["response"]["next_page"]
        for song in songs:
            songAddresses.add(song["path"])
    return songAddresses

session = initializeSession("ENTER BEARER")
name = input("PODAJ WYKONAWCE: ")
id = getArtistId(session, name)
print("Jego Id to {0}".format(id))
addresses = getAllSongAddresses(session, id)
