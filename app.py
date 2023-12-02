from flask import Flask, render_template, request, redirect
from BackEnd.classes.user import F
from BackEnd.classes.userdocker import FD
from redis import Redis
from pymongo import MongoClient

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

def DBD(collectionName):
    client = MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
    dbname = client["nsql_sem"]
    collection = dbname[collectionName]
    return collection


db = FD(DBD("Users"), DBD("Quacks")) # pouziti docker mongo
#db = F() # pouziti mongo pres railway


@app.route("/")
def home():
    quacks = db.globalRecentTwentyQuacks()
    posts = load_20_quacks(quacks)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/profile")
def profile():
    userID = redis.get("logged_in")
    if userID is None:
        return redirect('/login')
    tweets = db.myRecentTwentyQuacks(int(userID))
    posts = load_20_quacks(tweets)
    return render_template('profile.html', posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = str(request.form['username'])
        passw = str(request.form['password'])
        userID = (db.loginUser(user, passw))["_id"]
        redis.set("logged_in", str(userID))
        return redirect('/profile')
    else:
        return render_template('login.html')

def load_20_quacks(quacks):
    return [
        {
            'author': quack['userName'],
            'title': "title",
            'content': quack['quackContent'],
            'date_posted': quack['dateTweeted']
        }
        for quack in quacks
    ]


if __name__ == '__main__':
    app.run(host= "0.0.0.0", port=5000, debug=True)