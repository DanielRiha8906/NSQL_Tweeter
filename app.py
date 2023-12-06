from flask import Flask, render_template, request, redirect, flash, session
from BackEnd.classes.user import F
from BackEnd.classes.userdocker import DB
from redis import Redis


app = Flask(__name__)
redis = Redis(host='redis', port=6379)
app.secret_key = 'quack'

#client = MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
#dbname = client["nsql_sem"]
#db = DB(dbname["Users"], dbname["Quacks"]) # pouziti docker mongo
db = F() # pouziti mongo pres railway


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
    userID = session['user_ID']
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
        user = db.loginUser(user, passw)
        if user != False:
            userID = user["_id"]
            session['user_ID'] = userID
            flash('You are now logged in', 'success')
            return redirect('/profile')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = str(request.form['username'])
        passw = str(request.form['password'])
        reg = db.registerUser(user, passw)
        if reg != None:
            flash('You are now registered and can log in')
            return redirect('/login')
        else:
            flash('The username is already taken')
            return redirect('/register')
    else:
        return render_template('register.html')


@app.route("/logout")
def logout():
    session['user_ID'] = None
    return redirect('/login')


def load_20_quacks(quacks):
    return [ {
            'author': quack['userName'],
            'title': "title",
            'content': quack['tweetContent'],
            'date_posted': quack['dateTweeted'],
        } for quack in quacks]


if __name__ == '__main__':
    app.run(host= "0.0.0.0", port=5000, debug=True)