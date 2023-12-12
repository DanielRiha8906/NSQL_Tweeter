import pymongo
from datetime import datetime


class DB:

    def __init__(self, users, quacks):
        # Ustanoveni connection k jednotlivym kolekcim
        self.users = users
        self.quacks = quacks


    def add_quack(self, user_id, body):
        """Funkce pro pridani quacku ktera bere jako argument ID uzivatele a obsahu quacku,
        pokud neexistuje tak mu neumozni prispevek vytvorit.
        @user_id: id aktualniho uzivatele
        @body: obsah quacku, ktery uzivatel na vstupu zadal
        """
        current_user = self.users.find_one({"_id": user_id})
        if current_user is None:
            print("You have to login, to be able to post a quack!")
            return None
        if len(body) > 255:
            print("Quack is too long!")
            return None
        latest_quack = self.quacks.find().sort({"_id": -1}).limit(1)
        latest_id = latest_quack[0].get("_id")
        quack = {
            "_id": latest_id + 1,
            "userID": user_id,
            "userName": current_user["userName"],
            "quackContent": body,
            "dateQuacked": datetime.now().isoformat(),
        }
        self.quacks.insert_one(quack)

    def del_quack(self, quack_id, user_id):
        """Funkce posila pozadavek na vymazani quacku podle ID.
        @quack_id: ID quacku, ktery chceme vymazat
        @user_id: ID (aktualniho) uzivatele, ktery chce prispevek vymazat, pro overeni zda je puvodnim autorem
        """
        current_quack = self.quacks.find_one({"_id": quack_id})
        user = current_quack.get("user_id")
        if current_quack is None:
            print("You cannot delete a quack that does not exist!")
            return None
        if user != user_id:
            print("You cannot delete a quack that is not yours!")
            return None

        self.quacks.delete_one({"_id": quack_id})

    def update_bio(self, user_id, new_bio):
        """Funkce posila pozadavek na updatenuti biografie uzivatele podle ID, prijima novou biografii.
        @user_id: ID (aktualniho) uzivatele, ktery chce biografii aktualizovat.
        @new_bio: obsah nove biografie
        """
        filter = {"_id": user_id}
        self.quacks.update_one(filter, {"$set": {"bio": new_bio}})

    def update_name(self, user_id, new_name):
        """Funkce pro aktualizovani username uzivatele
        @user_id: ID (aktualniho) uzivatele, ktery chce username aktualizovat
        @new_name: nove jmeno, ktere si uzivatel zvolil
        """
        filter = {"_id": user_id}
        self.quacks.update_one(filter, {"$set": {"username": new_name}})

    def update_quack(self, quack_id, new_content, user_id):
        """Funkce posila pozadavek na aktualizaci quacku podle ID, prijima novy obsah quacku.
        @quack_id: ID quacku, ktery chceme aktualizovat
        @new_content: novy obsah quacku ktery aktualizujeme
        @user_id: ID (aktualniho) uzivatele, ktery chce prispevek aktualizovat, pro overeni zda je puvodnim autorem
        """
        current_quack = self.quacks.find_one({"_id": quack_id})
        quack_author = current_quack.get("user_id")
        if current_quack is None:
            print("You cannot update a quack that does not exist!")
            return None
        if quack_author != user_id:
            print("You cannot update a quack that is not yours!")
            return None
        filter = {"_id": quack_id}
        new_body = {"$set": {"quack_content": new_content}}
        self.quacks.update_one(filter, new_body)

    def my_quacks(self, user_id):
        """Funkce vraci veskere quacky ktery uzivatel s danym ID pridal.
        @user_id: ID aktualniho uzivatele
        $return: vraci veskere jeho pridane quacky
        """
        if self.users.find_one({"_id": user_id}) is None or user_id is None:
            print("You are not logged in!")
            return None
        my_quacks = self.quacks.find(user_id)
        return my_quacks

    def who_am_i(self, user_id):
        """Funkce vraci zaznam o uzivateli s danym ID.
        @user_id: ID aktualniho uzivatele
        $return: vraci veskere info o uzivateli s danym ID
        """
        user = self.users.find_one({"_id": user_id})
        if user is None:
            print("You are not logged in!")
            return None
        return user

    def upvote_quack(self, user_id, quack_id):
        """Funkce umoznuje uzivateli interagovat s quackem. Prida ID quacku do pole likedQuacks daneho uzivatele a vice versa.
        @user_id: ID aktualniho uzivatele
        @quack_id: ID quacku, ktery chce uzivatel "likenout"
        """
        user = self.users.find_one({"_id": user_id})
        if user is None:
            print("You are not logged in!")
            return None
        if self.quacks.find_one({"_id": quack_id}) is None:
            print("You cannot upvote a quack that does not exist!")
            return None
        if user_id in self.quacks.find_one({"_id": quack_id}).get("likedBy"):
            print(
                "You have already upvoted this quack, do you want to cancel your upvote?"
            )
            return False
        self.users.update_one({"_id": user_id}, {"$push": {"upvotedQuacsk": quack_id}})
        self.quacks.update_one(
            {"_id": quack_id}, {"$inc": {"upvotes": 1}, "$push": {"upvotedBy": user_id}}
        )

    def register_user(self, username, password):
        """Funkce pro vytvoreni noveho uzivatele.
        @username: uzivatelske jmeno, ktere klient zadal na vstupu
        @password: heslo, ktere klient zadal na vstupu
        """
        if self.users.find_one({"username": username}) is not None:
            print("This username is already taken!")
            return None

        latest_user = self.users.find_one(sort=[("_id", pymongo.DESCENDING)])
        latest_id = latest_user.get("_id")
        user = {
            "_id": latest_id + 1,
            "username": username,
            "password": password,
        }
        self.users.insert_one(user)

    def login_user(self, username, password):
        """Funkce pro prihlaseni uzivatele.
        @username: uzivatelske jmeno, ktere klient zadal na vstupu
        @password: heslo, ktere klient zadal na vstupu
        $return: vraci objekt uzivatele
        """
        user = self.users.find_one({"userName": username, "password": password})
        if user is None:
            print("Wrong username or password!")
            return False
        return user

    def global_recent_twenty_quacks(self):
        """Funkce vraci "nejcerstvejsich" 20 quacku.
        $return: kolekce 20 quacku, ktere jsou nejnovejsi
        """
        last20 = (self.quacks.find().sort("dateQuacked", -1).limit(20))
        return last20

    def my_recent_twenty_quacks(self, user_id):
        """Funkce vraci "nejcerstvejsich" 20 quacku pridanych konkretnim uzivatelem.
        @user_id: ID uzivatele, jehoz quacks chceme zobrazit
        $return: kolekce 20 quacku, ktere jsou nejnovejsi u konkretniho uzivatele
        """
        filter = {"user_id": user_id}
        last20 = self.quacks.find(filter).sort("dateQuacked", -1).limit(20)
        return last20


