import pymongo
from datetime import datetime


class DB:

    def __init__(self, users, quacks):
        self.users = users
        self.quacks = quacks


    def add_quack(self, user_id, body):
        """Funkce pro pridani quacku ktera bere jako argument ID uzivatele a obsahu quacku,
        pokud neexistuje tak mu neumozni prispevek vytvorit.
        @user_id: id aktualniho uzivatele
        @body: obsah quacku, ktery uzivatel na vstupu zadal
        """
        current_user = self.users.find_one({"_id": user_id})
        if len(body) > 255:
            return 1 # too long
        if len(body) == 0:
            return 2 # empty
        latest_quack = self.quacks.find().sort({"_id": -1}).limit(1)
        try:
            latest_id = latest_quack[0].get("_id")
        except IndexError:
            latest_id = 0
        quack = {
            "_id": latest_id + 1,
            "user_id": user_id,
            "username": current_user["username"],
            "quack_content": self.replace_f_words(body),
            "date_quacked": datetime.now().isoformat(),
            "likes": 0
        }
        self.quacks.insert_one(quack)
        return 0


    def del_quack(self, quack_id, user_id):
        """Funkce posila pozadavek na vymazani quacku podle ID.
        @quack_id: ID quacku, ktery chceme vymazat
        @user_id: ID (aktualniho) uzivatele, ktery chce prispevek vymazat,
        pro overeni zda je puvodnim autorem
        """
        current_quack = self.quacks.find_one({"_id": quack_id})
        owner = current_quack["user_id"]
        if current_quack is None:
            return None
        if owner != user_id:
            return None

        self.quacks.delete_one({"_id": quack_id})


    def update_bio(self, user_id, new_bio):
        """Funkce posila pozadavek na updatenuti biografie uzivatele podle ID,
        prijima novou biografii.
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
        @user_id: ID (aktualniho) uzivatele,
        ktery chce prispevek aktualizovat, pro overeni zda je puvodnim autorem
        """
        current_quack = self.quacks.find_one({"_id": quack_id})
        quack_author = current_quack.get("user_id")
        if current_quack is None:
            return None
        if quack_author != user_id:
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
            return None
        return user


    def like_quack(self, user_id, quack_id):
        """Funkce umoznuje uzivateli interagovat s quackem. Prida ID quacku do pole likedQuacks daneho uzivatele a vice versa.
        @user_id: ID aktualniho uzivatele
        @quack_id: ID quacku, ktery chce uzivatel "likenout"
        """
        if self.quacks.find_one({"_id": quack_id}) is None:
            return None

        self.users.update_one({"_id": user_id}, {"$push": {"liked_quacks": quack_id}})
        self.quacks.update_one({"_id": quack_id}, {"$inc": {"likes": 1}})
        return 0


    def unlike_quack(self, user_id, quack_id):
        """Funkce umoznuje uzivateli interagovat s quackem. Odebere ID quacku z pole likedQuacks daneho uzivatele a vice versa.
        @user_id: ID aktualniho uzivatele
        @quack_id: ID quacku, ktery chce uzivatel "unlikenout"
        """
        if self.quacks.find_one({"_id": quack_id}) is None:
            return None

        self.users.update_one({"_id": user_id}, {"$pull": {"liked_quacks": quack_id}})
        self.quacks.update_one({"_id": quack_id}, {"$inc": {"likes": -1}})
        return 0


    def my_liked_posts(self, user_id):
        """Funkce vraci pole ID quacku, ktere uzivatel likenul.
        @user_id: ID aktualniho uzivatele
        $return: pole ID quacku, ktere uzivatel likenul
        """
        user = self.users.find_one({"_id": user_id})
        try:
            posts = user["liked_quacks"]
        except AttributeError:
            posts = []
        return posts


    def is_quack_liked(self, quack_id, user_id):
        """Funkce kontroluje zdali je dany quack uzivatelem jiz olikeovany.
        @quack_id: ID quacku, ktery chceme overit
        @userID: ID aktualniho uzivatele
        $return: True, pokud je quack olikeovany, jinak False
        """
        quacks_liked = self.my_liked_posts(user_id)
        try:
            if quack_id in quacks_liked:
                return True
        except TypeError:
            return False
        return False


    def register_user(self, username, password):
        """Funkce pro vytvoreni noveho uzivatele.
        @username: uzivatelske jmeno, ktere klient zadal na vstupu
        @password: heslo, ktere klient zadal na vstupu
        """
        if self.users.find_one({"username": username}) is not None:
            return False

        else:
            latest_user = self.users.find_one(sort=[("_id", pymongo.DESCENDING)])
            if latest_user is None:
                latest_id = 0
            else:
                latest_id = latest_user.get("_id")
            user = {
                "_id": latest_id + 1,
                "username": username,
                "password": password,
                "liked_quacks": []
            }
            self.users.insert_one(user)
            return True


    def login_user(self, username, password):
        """Funkce pro prihlaseni uzivatele.
        @username: uzivatelske jmeno, ktere klient zadal na vstupu
        @password: heslo, ktere klient zadal na vstupu
        $return: vraci objekt uzivatele
        """
        user = self.users.find_one({"username": username, "password": password})
        if user is None:
            return False
        return user


    def global_recent_twenty_quacks(self, range):
        """Funkce vraci "nejcerstvejsich" 20 quacku.
        $return: kolekce 20 quacku, ktere jsou nejnovejsi
        """
        offset = range * 20
        limit = 20
        paginated_quacks = self.quacks.find().sort("date_quacked", -1).skip(offset).limit(limit)
        return paginated_quacks


    def my_recent_twenty_quacks(self, user_id, range):
    def my_recent_twenty_quacks(self, user_id, range):
        """Funkce vraci "nejcerstvejsich" 20 quacku pridanych konkretnim uzivatelem.
        @user_id: ID uzivatele, jehoz quacks chceme zobrazit
        $return: kolekce 20 quacku, ktere jsou nejnovejsi u konkretniho uzivatele
        """
        filter = {"user_id": user_id}
        offset = range * 20
        limit = 20
        paginated_quacks = self.quacks.find(filter).sort("date_quacked", -1).skip(offset).limit(limit)
        return paginated_quacks
    

    def replace_f_words(self, post):
        """Funkce pro nahradeni f-words na vstupu."""
        replace_dict = {'fuck': 'duck', 'fucking': 'ducking', 'fucker': 'ducker'}
        for word, replacement in replace_dict.items():
            post = post.replace(word, replacement)
            post = post.replace(word.upper(), replacement.capitalize())
        return post