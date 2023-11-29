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
        pokud neexistuje tak mu neumozni prispevek vytvorit.
        @userID: id aktualniho uzivatele
        @body: obsah tweetu, ktery uzivatel na vstupu zadal
    """
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
    tweety.insert_one(tweet)


def delTweet(tweetID, userID):
    """Funkce posila pozadavek na vymazani tweetu podle ID.
        @tweetID: ID tweetu, ktery chceme vymazat
        @UserID: ID (aktualniho) uzivatele, ktery chce prispevek vymazat, pro overeni zda je puvodnim autorem
    """
    currentTweet = tweety.find_one({"_id": tweetID})
    if currentTweet.get("userID") != userID:
        print(f"currentUser: {uzivatele.find_one({'_id': userID})}")
        print(f"author: {currentTweet.get('userID')}")
        print("You cannot delete a tweet that is not yours!")
        return None
    if currentTweet is None:
        print("You cannot delete a tweet that does not exist!")
        return None
    tweety.delete_one({"_id": tweetID})


def updateTweet(tweetID, newContent):
    """Funkce posila pozadavek na aktualizaci tweetu podle ID, prijima novy obsah tweetu.
        @tweetID: ID tweetu, ktery chceme aktualizovat
        @newContent: novy obsah tweetu ktery aktualizujeme
    """
    filter = {"_id": tweetID}
    newBody = {"$set": {"tweetContent": newContent}}
    tweety.update_one(filter, newBody)


def myTweets(myID):
    """Funkce vraci veskere tweety ktery uzivatel s danym ID pridal.
        @myID: ID aktualniho uzivatele
        $return: vraci veskere jeho pridane tweety
    """
    mojeTweets = tweety.find({"userID": myID})
    return mojeTweets


def whoAmI(myID):
    """Funkce vraci zaznam o uzivateli s danym ID.
        @myID: ID aktualniho uzivatele
        $return: vraci veskere info o uzivateli s danym ID
    """
    return uzivatele.find_one({"_id": myID})


def registerUser(username, password):
    """Funkce pro vytvoreni noveho uzivatele.
        @username: uzivatelske jmeno, ktere klient zadal na vstupu
        @password: heslo, ktere klient zadal na vstupu
    """
    latestUser = uzivatele.find_one(sort=[("_id", pymongo.DESCENDING)])
    latestID = latestUser.get("_id")
    user = {
        "_id": latestID + 1,
        "userName": username,
        "password": password,
    }
    uzivatele.insert_one(user)


def loginUser(username, password):
    """Funkce pro prihlaseni uzivatele.
        @username: uzivatelske jmeno, ktere klient zadal na vstupu
        @password: heslo, ktere klient zadal na vstupu
        $return: vraci objekt uzivatele
    """
    user = uzivatele.find_one({"userName": username, "password": password})
    if user is None:
        print("Wrong username or password!")
        return False
    return user


def globalRecentTwentyTweets():
    """Funkce vraci "nejcerstvejsich" 20 tweetu.
        $return: kolekce 20 tweetu, ktere jsou nejnovejsi
    """
    last20 = tweety.find().sort("dateTweeted", -1).limit(20)
    return last20


# updateTweet(5, "Premazani zmeneneho obsahu tweetu.")

# for tweet in recentTwentyTweets():
#     print(tweet)
# delTweet(22, 1)
# print(loginUser("hokus", "pokus"))
# addTweet(1, "Test tweet")
# for tweet in recentTwentyTweets():
#    print(tweet["dateTweeted"])
