from db import DB
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# Ustanoveni connection k jednotlivym kolekcim
uzivatele = DB("Users")
tweety = DB("MockTweets")

# Funkce pro pridani tweetu ktera bere jako argument ID uzivatele a obsahu tweetu,
# pokud neexistuje tak mu neumozni prispevek vytvorit.
def addTweet(userID, body):
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

# Funkce posila pozadavek na vymazani tweetu podle ID
def delTweet(tweetID):
    currentTweet = tweety.find_one({"_id": tweetID})
    #!TODO - resit jestli je autor aktualni uzivatel
    if currentTweet is None:
        print("You cannot delete a tweet that does not exist!")
        return None
    return uzivatele.delete_one({"_id": tweetID})
def updateTweet(tweetID, newContent): 
    # currentTweet = tweety.find_one({"_id": tweetID})
    #!TODO
    pass

# Funkce vraci veskere tweety ktery uzivatel s danym ID pridal.
def myTweets(myID):
    mojeTweets = tweety.find({"userID": myID})
    return mojeTweets

# Funkce vraci zaznam o uzivateli s danym ID
def whoAmI(myID):
    return uzivatele.find_one({"_id": myID})




# addTweet(1, "Test tweet")

# for tweet in myTweets(18):
#     print(tweet)
# print(whoAmI(1))