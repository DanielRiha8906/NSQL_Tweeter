from flask import Flask, render_template, request, redirect, flash, session
from BackEnd.classes.userdocker import DB
from redis import Redis
from pymongo import MongoClient
from datetime import datetime
from flask_debug import Debug
import json

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
app.secret_key = 'quack'

client = MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
dbname = client["nsql_sem"]
db = DB(dbname["users"], dbname["quacks"])
Debug(app)


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"]) 
def home():
    if request.method == "GET":
        try:
            page = int(session['home_page_coefficient'])
        except KeyError:
            session['home_page_coefficient'] = 0
            page = 0
        
        if page == 0:
            posts = cached()
            if posts is None:
                cache_it()
                posts = load_20_quacks(db.global_recent_twenty_quacks(0))
        else:
            posts = load_20_quacks(db.global_recent_twenty_quacks(page))
        account_name = get_user()
        if account_name is None:
            return render_template('home.html', posts=posts)
        else:
            user = account_name['username']
            return render_template('home.html', posts=posts, account_name=user)
    if request.method == "POST":
        return post_quack('home')  


@app.route("/TOS")
def tos():
    return render_template('terms_of_service.html')


@app.route("/about")
def about():
    if get_user() is None:
        return render_template('about.html', title='About')
    else:
        account_name = {}
        account_name = db.who_am_i(session['user_id'])
        user = account_name['username']
        return render_template('about.html',title='About', account_name=user)
    

@app.route("/like/<int:quack_id>", methods=["GET", "POST"])
def like(quack_id):
    user_id = session["user_id"]
    upvote = db.upvote_quack(user_id, quack_id)


@app.route("/delete/<int:quack_id>", methods=["GET","POST"])
def delete_quack(quack_id):
    """Metoda pro vymazani quacku na FrontEndu provazanim s metodou z BackEndu. Kontrola jestli je uzivatel prihlasen, pokud ne tak ho odkaze na loginpage. 
    """
    user_id = session['user_id']
    if user_id is None:
        flash('You cannot delete a quack, if you are not logged in!', 'danger')
        return redirect("/login")
    elif user_id is not None:
        db.del_quack(quack_id, user_id)
        flash('Your quack has been deleted!', 'success')
        cache_it()
        return redirect("/profile")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Metoda pro zobrazovani profilu. Kontrola jestli je uzivatel prihlasen, pokud ne tak ho odkaze na loginpage."""
    if request.method == "POST":
        cache_it()
        return post_quack('profile')
    if request.method == "GET":
        user_id = session['user_id']
        if user_id is None:
            return redirect('/login')
        
        account_name = db.who_am_i(session['user_id'])
        user = account_name['username']
        posts = load_20_quacks(db.my_recent_twenty_quacks(int(user_id), session['profile_pages_coefficient']))
        return render_template('profile.html', posts=posts, account_name=user, title=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    session['profile_pages_coefficient'] = 0
    if request.method == "POST":
        user = str(request.form['username'])
        passw = str(request.form['password'])
        user = db.login_user(user, passw)
        if user:
            user_id = user["_id"]
            session['user_id'] = user_id
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
        reg = db.register_user(user, passw)
        if reg:
            flash('You are now registered and can log in', 'success')
            return redirect('/login')
        else:
            flash('The username is already taken', 'danger')
            return redirect('/register')
    else:
        return render_template('register.html')


@app.route("/<page>/next", methods=["GET"])
def next_page(page):
    if page == 'home':
        session['home_pages_coefficient'] += 1
        if not can_i_go_next(session['home_pages_coefficient']):
            session['home_pages_coefficient'] -= 1
        return redirect('/')
    elif page == 'profile':
        session['profile_pages_coefficient'] += 1
        if not can_i_go_next(session['profile_pages_coefficient']):
            session['profile_pages_coefficient'] -= 1
        return redirect('/profile')


@app.route("/<page>/previous", methods=["GET"])
def previous_page(page):
    if page == 'home':
        if session['home_pages_coefficient'] == 0:
            return redirect('/')
        session['home_pages_coefficient'] -= 1
        return redirect('/')
    elif page == 'profile':
        if session['profile_pages_coefficient'] == 0:
            return redirect('/profile')
        session['profile_pages_coefficient'] -= 1
        return redirect('/profile')
    

@app.route("/logout")
def logout():
    session['home_page_coefficient'] = 0
    session['profile_page_coefficient'] = 0
    session['user_id'] = None
    return redirect('/login')


def load_20_quacks(quacks):
    """Metoda pro ziskani 20 nejnovensich quacku."""
    return [ {
            'id': quack['_id'],
            'author': quack['username'],
            'title': "title",
            'content': quack['quack_content'],
            'date_posted': datetime.strptime(quack['date_quacked'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%H:%M - %d/%m/%Y"),
            'likes': quack['likes'],
        } for quack in quacks][::-1]


def cache_it():
    """Metoda pro cacheovani vsech 20 nejnovensich quacku.""" 
    try:
        redis.set("quacks", json.dumps(load_20_quacks(db.global_recent_twenty_quacks(0))))
    except TypeError:
        pass


def cached():
    """Metoda pro ziskani vsech 20 nejnovensich quacku z cache."""
    try:
        return json.loads(redis.get("quacks"))
    except TypeError:
        return None


def post_quack(to_page):
    """Metoda pro postovani novych quacku na FrontEndu provazanim s metodou z BackEndu.
    Kontrola jestli je uzivatel prihlasen, pokud ne tak ho odkaze na loginpage. A kontrola jestli neprekrocil maximalni delku quacku(255),
    tento check je aktualne 'duplicitni'.
    """
    user_id = session["user_id"]
    if user_id is None:
        flash("You cannot post a quack, if you are not logged in!")
        return redirect("/login")
    else:
        content = str(request.form["quack_content"])
        posted = db.add_quack(user_id, content)

        if posted == 2:
            flash("Your cannot post an empty quack!", "danger")
            return redirect(f"/{to_page}")
        elif posted == 1:
            flash("Your quack is too long!", "danger")
            return redirect(f"/{to_page}")
        else:
            cache_it()
            flash("Your quack has been successfully posted!", "success")
            return redirect(f"/{to_page}")
        

def get_user():
    """Metoda pro ziskani aktualniho uzivatele."""
    if 'user_id' in session:
        return db.who_am_i(session['user_id'])
    return None


def can_i_go_next(page_number):
    """Metoda pro ziskani jestli je mozne pokracovat na dalsi stranku."""
    max_page = db.count_quacks() // 20 + 0 if (db.count_quacks() % 20) == 0 else 1
    if page_number < max_page:
        return True
    return False

if __name__ == '__main__':
    app.run(host= "0.0.0.0", port=5000, debug=True)