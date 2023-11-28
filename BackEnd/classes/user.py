from db import DB
from dotenv import load_dotenv
# from pymongo import MongoClient
import pymongo
from datetime import datetime


load_dotenv()

# Ustanoveni connection k jednotlivym kolekcim
uzivatele = DB("Users")
tweety = DB("MockTweets")


def addTweet(userID, body):
    """Funkce pro pridani tweetu ktera bere jako argument ID uzivatele a obsahu tweetu,
    pokud neexistuje tak mu neumozni prispevek vytvorit."""
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
        "likesCount": 0,
    }
    return tweety.insert_one(tweet)


def delTweet(tweetID, userID):
    """Funkce posila pozadavek na vymazani tweetu podle ID."""
    currentTweet = tweety.find_one({"_id": tweetID})
    # print(currentTweet)
    if currentTweet.get("userID") != userID:
        print(f"currentUser: {uzivatele.find_one({'_id': userID})}")
        print(f"author: {currentTweet.get('userID')}")
        print("You cannot delete a tweet that is not yours!")
        return None
    if currentTweet is None:
        print("You cannot delete a tweet that does not exist!")
        return None
    # print(f"Uspesne jsem tweet znicil {tweetID}:{userID}")
    return tweety.delete_one({"_id": tweetID})


def updateTweet(tweetID, newContent):
    """Funkce posila pozadavek na aktualizaci tweetu podle ID, prijima novy obsah tweetu."""
    # currentTweet = tweety.find_one({"_id": tweetID})
    #!TODO Maybe ?
    pass


def myTweets(myID):
    """Funkce vraci veskere tweety ktery uzivatel s danym ID pridal."""
    mojeTweets = tweety.find({"userID": myID})
    return mojeTweets


def whoAmI(myID):
    """Funkce vraci zaznam o uzivateli s danym ID."""
    return uzivatele.find_one({"_id": myID})


def registerUser(username, password):
    """Funkce pro vytvoreni noveho uzivatele."""
    latestUser = uzivatele.find_one(sort=[("_id", pymongo.DESCENDING)])
    maxID = latestUser.get("_id")
    user = {
        "_id": maxID + 1,
        "userName": username,
        "password": password,
    }
    return uzivatele.insert_one(user)


def loginUser(username, password):
    """Funkce pro prihlaseni uzivatele."""
    user = uzivatele.find_one({"userName": username, "password": password})
    if user is None:
        print("Wrong username or password!")
        return False
    return user

def recentTwentyTweets():
    #!TODO - Funkce vraci poslednich 20 tweetu zaznamu v databazi 
    pass




# print(loginUser("hokus", "pokus"))
# addTweet(1, "Test tweet")

# for tweet in myTweets(18):
#    print(tweet)
# print(whoAmI(1))
