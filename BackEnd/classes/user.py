from BackEnd.classes.db import DB
from dotenv import load_dotenv

# from pymongo import MongoClient
import pymongo
from datetime import datetime


class F:
    load_dotenv()

    uzivatele: DB
    tweety: DB

    def __init__(self):
        # Ustanoveni connection k jednotlivym kolekcim
        self.uzivatele = DB("Users")
        self.tweety = DB("MockTweets")

    def addTweet(self, userID, body):
        """Funkce pro pridani tweetu ktera bere jako argument ID uzivatele a obsahu tweetu,
        pokud neexistuje tak mu neumozni prispevek vytvorit.
            @userID: id aktualniho uzivatele
            @body: obsah tweetu, ktery uzivatel na vstupu zadal
        """
        currentUser = self.uzivatele.find_one({"_id": userID})
        if currentUser is None:
            print("You have to login, to be able to add a tweet!")
            return None
        tweet = {
            "_id": self.tweety.count_documents({}) + 1,
            "userID": userID,
            "userName": currentUser["userName"],
            "tweetContent": body,
            "dateTweeted": datetime.now().strftime("%H:%M:%d:%m:%Y"),
            "likesCount": 0,
        }
        self.tweety.insert_one(tweet)

    def delTweet(self, tweetID, userID):
        """Funkce posila pozadavek na vymazani tweetu podle ID.
            @tweetID: ID tweetu, ktery chceme vymazat
            @UserID: ID (aktualniho) uzivatele, ktery chce prispevek vymazat, pro overeni zda je puvodnim autorem
        """
        currentTweet = self.tweety.find_one({"_id": tweetID})
        user = currentTweet.get("userID")
        if currentTweet is None:
            print("You cannot delete a tweet that does not exist!")
            return None
        if user != userID:
            print("You cannot delete a tweet that is not yours!")
            return None

        self.tweety.delete_one({"_id": tweetID})

    def updateBio(self, userID, newBIO):
        """Funkce posila pozadavek na updatenuti biografie uzivatele podle ID, prijima novou biografii.
            @userID: ID (aktualniho) uzivatele, ktery chce biografii aktualizovat.
            @newBIO: obsah nove biografie
        """
        filter = {"_id": userID}
        self.tweety.update_one(filter, {"$set": {"bio": newBIO}})

    def updateName(self, userID, newName):
        """Funkce pro aktualizovani username uzivatele
            @userID: ID (aktualniho) uzivatele, ktery chce username aktualizovat
            @newName: nove jmeno, ktere si uzivatel zvolil
        """
        filter = {"_id": userID}
        self.tweety.update_one(filter, {"$set": {"userName": newName}})

    def updateTweet(self, tweetID, newContent, userID):
        """Funkce posila pozadavek na aktualizaci tweetu podle ID, prijima novy obsah tweetu.
            @tweetID: ID tweetu, ktery chceme aktualizovat
            @newContent: novy obsah tweetu ktery aktualizujeme
            @userID: ID (aktualniho) uzivatele, ktery chce prispevek aktualizovat, pro overeni zda je puvodnim autorem
        """
        currentTweet = self.tweety.find_one({"_id": tweetID})
        tweetAuthor = currentTweet.get("userID")
        if currentTweet is None:
            print("You cannot update a tweet that does not exist!")
            return None
        if tweetAuthor != userID:
            print("You cannot update a tweet that is not yours!")
            return None
        filter = {"_id": tweetID}
        newBody = {"$set": {"tweetContent": newContent}}
        self.tweety.update_one(filter, newBody)

    def myTweets(self, myID):
        """Funkce vraci veskere tweety ktery uzivatel s danym ID pridal.
            @myID: ID aktualniho uzivatele
            $return: vraci veskere jeho pridane tweety
        """
        if self.uzivatele.find_one({"_id": myID}) is None or myID is None:
            print("You are not logged in!")
            return None
        mojeTweets = self.tweety.find({"userID": myID})
        return mojeTweets

    def whoAmI(self, myID):
        """Funkce vraci zaznam o uzivateli s danym ID.
            @myID: ID aktualniho uzivatele
            $return: vraci veskere info o uzivateli s danym ID
        """
        user = self.uzivatele.find_one({"_id": myID})
        if user is None:
            print("You are not logged in!")
            return None
        return user

    def registerUser(self, username, password):
        """Funkce pro vytvoreni noveho uzivatele.
            @username: uzivatelske jmeno, ktere klient zadal na vstupu
            @password: heslo, ktere klient zadal na vstupu
        """
        if self.uzivatele.find_one({"userName": username}) is not None:
            print("Username is already taken!")
            return None

        latestUser = self.uzivatele.find_one(
            sort=[("_id", pymongo.DESCENDING)])
        latestID = latestUser.get("_id")
        user = {
            "_id": latestID + 1,
            "userName": username,
            "password": password,
        }
        self.uzivatele.insert_one(user)

    def loginUser(self, username, password):
        """Funkce pro prihlaseni uzivatele.
            @username: uzivatelske jmeno, ktere klient zadal na vstupu
            @password: heslo, ktere klient zadal na vstupu
            $return: vraci objekt uzivatele
        """
        user = self.uzivatele.find_one(
            {"userName": username, "password": password})
        if user is None:
            print("Wrong username or password!")
            return False
        return user

    def globalRecentTwentyTweets(self):
        """Funkce vraci "nejcerstvejsich" 20 tweetu.
            $return: kolekce 20 tweetu, ktere jsou nejnovejsi
        """
        last20 = self.tweety.find().sort("dateTweeted", -1).limit(20)
        return last20

    def myRecentTwentyTweets(self, userID):
        """Funkce vraci "nejcerstvejsich" 20 tweetu pridanych konkretnim uzivatelem.
            @userID: ID uzivatele, jehoz tweety chceme zobrazit
            $return: kolekce 20 tweetu, ktere jsou nejnovejsi u konkretniho uzivatele
        """
        filter = {"userID": userID}
        last20 = self.tweety.find(filter).sort("dateTweeted", -1).limit(20)
        return last20

    # updateTweet(5, "Premazani zmeneneho obsahu tweetu.")

    # for tweet in recentTwentyTweets():
    #     print(tweet)
    # delTweet(22, 1)
    # print(loginUser("hokus", "pokus"))
    # addTweet(1, "Test tweet")
    # for tweet in recentTwentyTweets():
    #    print(tweet["dateTweeted"])
