from BackEnd.classes.db import DB
from dotenv import load_dotenv

# from pymongo import MongoClient
import pymongo
from datetime import datetime


class F:
    users: DB
    quacks: DB

    def __init__(self):
        self.users = DB("Users")
        self.quacks = DB("MockTweets")

    def addQuack(self, userID, body):
        """Funkce pro pridani quacku ktera bere jako argument ID uzivatele a obsahu quacku,
        pokud neexistuje tak mu neumozni prispevek vytvorit.
            @userID: id aktualniho uzivatele
            @body: obsah quacku, ktery uzivatel na vstupu zadal
        """
        currentUser = self.users.find_one({"_id": userID})
        if currentUser is None:
            print("You have to login, to be able to add a quack!")
            return None
        if body.len() > 255:
            print("Quack text is too long!")
            return None
        quack = {
            "_id": self.quacks.count_documents({}) + 1,
            "userID": userID,
            "userName": currentUser["userName"],
            "tweetContent": body,
            "dateTweeted": datetime.now().strftime("%H:%M:%d:%m:%Y"),
            "likesCount": 0,
        }
        self.quacks.insert_one(quack)

    def delQuack(self, quackID, userID):
        """Funkce posila pozadavek na vymazani quacku podle ID.
            @quackID: ID quacku, ktery chceme vymazat
            @UserID: ID (aktualniho) uzivatele, ktery chce prispevek vymazat, pro overeni zda je puvodnim autorem
        """
        currentQuack = self.quacks.find_one({"_id": quackID})
        user = currentQuack.get("userID")
        if currentQuack is None:
            print("You cannot delete a quack that does not exist!")
            return None
        if user != userID:
            print("You cannot delete a quack that is not yours!")
            return None

        self.quacks.delete_one({"_id": quackID})

    def updateBio(self, userID, newBIO):
        """Funkce posila pozadavek na updatenuti biografie uzivatele podle ID, prijima novou biografii.
            @userID: ID (aktualniho) uzivatele, ktery chce biografii aktualizovat.
            @newBIO: obsah nove biografie
        """
        filter = {"_id": userID}
        self.quacks.update_one(filter, {"$set": {"bio": newBIO}})

    def updateName(self, userID, newName):
        """Funkce pro aktualizovani username uzivatele
            @userID: ID (aktualniho) uzivatele, ktery chce username aktualizovat
            @newName: nove jmeno, ktere si uzivatel zvolil
        """
        filter = {"_id": userID}
        self.quacks.update_one(filter, {"$set": {"userName": newName}})

    def updateQuack(self, quackID, newContent, userID):
        """Funkce posila pozadavek na aktualizaci quacku podle ID, prijima novy obsah quacku.
            @quackID: ID quacku, ktery chceme aktualizovat
            @newContent: novy obsah quacku ktery aktualizujeme
            @userID: ID (aktualniho) uzivatele, ktery chce prispevek aktualizovat, pro overeni zda je puvodnim autorem
        """
        currentQuack = self.quacks.find_one({"_id": quackID})
        quackAuthor = currentQuack.get("userID")
        if currentQuack is None:
            print("You cannot update a quack that does not exist!")
            return None
        if quackAuthor != userID:
            print("You cannot update a quack that is not yours!")
            return None
        filter = {"_id": quackID}
        newBody = {"$set": {"tweetContent": newContent}}
        self.quacks.update_one(filter, newBody)

    def myQuacks(self, userID):
        """Funkce vraci veskere quacky ktery uzivatel s danym ID pridal.
            @userID: ID aktualniho uzivatele
            $return: vraci veskere jeho pridane quacky
        """
        if self.users.find_one({"_id": userID}) is None or userID is None:
            print("You are not logged in!")
            return None
        mojeQuacks = self.quacks.find({"userID": userID})
        return mojeQuacks
    def whoAmI(self, userID):
        """Funkce vraci zaznam o uzivateli s danym ID.
            @userID: ID aktualniho uzivatele
            $return: vraci veskere info o uzivateli s danym ID
        """
        user = self.users.find_one({"_id": userID})
        if user is None:
            print("You are not logged in!")
            return None
        return user

    def upvoteQuack(self, userID, quackID):
        """Funkce umoznuje uzivateli interagovat s quackem. Prida ID quacku do pole likedQuacks daneho uzivatele a vice versa.
            @userID: ID aktualniho uzivatele
            @quackID: ID quacku, ktery chce uzivatel "likenout"
        """
        user = self.users.find_one({"_id": userID})
        if user is None:
            print("You are not logged in!")
            return None
        if self.quacks.find_one({"_id": quackID}) is None:
            print("You cannot upvote a quack that does not exist!")
            return None
        if userID in self.quacks.find_one({"_id": quackID}).get("likedBy"):
            print(
                "You have already upvoted this quack, do you want to cancel your upvote?")
            return False
        self.users.update_one(
            {"_id": userID}, {"$push": {"upvotedQuacsk": quackID}})
        self.quacks.update_one(
            {"_id": quackID}, {"$inc": {"upvotes": 1}, "$push": {"upvotedBy": userID}})

    def registerUser(self, username, password):
        """Funkce pro vytvoreni noveho uzivatele.
            @username: uzivatelske jmeno, ktere klient zadal na vstupu
            @password: heslo, ktere klient zadal na vstupu
        """
        if self.users.find_one({"userName": username}) is not None:
            print("Username is already taken!")
            return None

        latestUser = self.users.find_one(
            sort=[("_id", pymongo.DESCENDING)])
        latestID = latestUser.get("_id")
        user = {
            "_id": latestID + 1,
            "userName": username,
            "password": password,
        }
        self.users.insert_one(user)

    def loginUser(self, username, password):
        """Funkce pro prihlaseni uzivatele.
            @username: uzivatelske jmeno, ktere klient zadal na vstupu
            @password: heslo, ktere klient zadal na vstupu
            $return: vraci objekt uzivatele
        """
        user = self.users.find_one(
            {"userName": username, "password": password})
        if user is None:
            print("Wrong username or password!")
            return False
        return user

    def globalRecentTwentyQuacks(self):
        """Funkce vraci "nejcerstvejsich" 20 quacku.
            $return: kolekce 20 quacku, ktere jsou nejnovejsi
        """
        last20 = self.quacks.find().sort("dateQuacked", -1).limit(20)
        return last20

    def myRecentTwentyQuacks(self, userID):
        """Funkce vraci "nejcerstvejsich" 20 quacku pridanych konkretnim uzivatelem.
            @userID: ID uzivatele, jehoz quacks chceme zobrazit
            $return: kolekce 20 quacku, ktere jsou nejnovejsi u konkretniho uzivatele
        """
        filter = {"userID": userID}
        last20 = self.quacks.find(filter).sort("dateQuacked", -1).limit(20)
        return last20