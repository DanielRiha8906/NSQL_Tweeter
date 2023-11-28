from db import DB
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime


load_dotenv()

# Ustanoveni connection k jednotlivym kolekcim
uzivatele = DB("Users")
tweety = DB("MockTweets")

def addTweet(userID, body):
    """ Funkce pro pridani tweetu ktera bere jako argument ID uzivatele a obsahu tweetu,
    pokud neexistuje tak mu neumozni prispevek vytvorit. """
    currentUser = uzivatele.find_one({"_id": userID})
    if currentUser is None:
        print("You have to login, to be able to add a tweet!")
        return None
    tweet = {
        "_id": tweety.count_documents({}) + 1,
        "userID": userID,
        "userName": currentUser["userName"],
        "tweetContent": body,
        "dateTweeted": datetime.now().strftime("%H:%M:%d:%m:%Y"),
        "likesCount": 0
    }
    return tweety.insert_one(tweet)


def delTweet(tweetID, userID):
    """Funkce posila pozadavek na vymazani tweetu podle ID."""
    currentTweet = tweety.find_one({"_id": tweetID})
    if currentTweet.get("userID") != uzivatele.find_one({"_id": userID}):
        print("You cannot delete a tweet that is not yours!")
        return None
    if currentTweet is None:
        print("You cannot delete a tweet that does not exist!")
        return None
    return uzivatele.delete_one({"_id": tweetID})


def updateTweet(tweetID, newContent): 
    """Funkce posila pozadavek na aktualizaci tweetu podle ID, prijima novy obsah tweetu."""
    # currentTweet = tweety.find_one({"_id": tweetID})
    #!TODO
    pass


def myTweets(myID):
    """Funkce vraci veskere tweety ktery uzivatel s danym ID pridal."""
    mojeTweets = tweety.find({"userID": myID})
    return mojeTweets


def whoAmI(myID):
    """Funkce vraci zaznam o uzivateli s danym ID."""
    return uzivatele.find_one({"_id": myID})




#addTweet(1, "Test tweet")

#for tweet in myTweets(18):
#    print(tweet)
#print(whoAmI(1))