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

def get_user():
    if 'user_id' in session:
        return db.who_am_i(session['user_id'])
    return None
@app.route("/") 
def home():
    try:
        page = int(session['home_pages_coefficient'])
    except KeyError:
        session['home_pages_coefficient'] = 0
        page = 0
    quacks = db.global_recent_twenty_quacks(session['home_pages_coefficient'])
    posts = load_20_quacks(quacks)
    if get_user() is None:
        return render_template('home.html', posts=posts)
    else:
        account_name = {}
        account_name=db.who_am_i(session['user_id'])
        user = account_name['userName']
        return render_template('home.html', posts=posts, account_name=user)


@app.route("/TOS")
def tos():
    return render_template('terms_of_service.html')

@app.route("/about")
def about():
    if get_user() is None:
        return render_template('about.html', title='About')
    else:
        account_name = {}
        account_name=db.who_am_i(session['user_id'])
        user = account_name['userName']
        return render_template('about.html',title='About', account_name=user)
    

@app.route("/delete/<int:quack_id>", methods=["GET","POST"])
def delete_quack(quack_id):
    """Metoda pro vymazani quacku na FrontEndu provazanim s metodou z BackEndu. Kontrola jestli je uzivatel prihlasen, pokud ne tak ho odkaze na loginpage. 
    @quack_id: ID quacku, ktery chceme vymazat
    """
    print('deleted succsessfully')
    user_id = session['user_id']
    if user_id is None:
        flash('You cannot delete a quack, if you are not logged in!', 'danger')
        return redirect("/login")
    elif user_id is not None:
        db.del_quack(quack_id, user_id)
        flash('Your quack has been deleted!', 'success')
        return redirect("/profile")

@app.route("/like/<int:quack_id>", methods=["GET","POST"])
def like_quack(quack_id):
    """Metoda pro like/unlike na FrontEndu provazanim s metodou z BackEndu. Kontrola jestli je uzivatel prihlasen, pokud ne tak ho odkaze na loginpage. 
    @quack_id: ID quacku, ktery chceme like/unlike
    """
    user_id = session['user_id']
    if user_id is None:
        flash('You cannot like/unlike a quack, if you are not logged in!', 'danger')
        return redirect("/login")
    elif db.quacks.find_one({"_id": quack_id}) is None:
        flash('Quack does not exist!', 'danger')
        print('quack does not exist')
        return redirect (request.referrer)
    elif db.is_quack_liked(quack_id, user_id) is True:
        db.unlike_quack(user_id,quack_id)
        flash('Quack has been unliked!', 'success')
        print('quack has been unliked')
        return redirect (request.referrer)
    elif db.is_quack_liked(quack_id,user_id) is False:
        db.like_quack(user_id,quack_id)
        flash('Quack has been liked!', 'success')
        print('quack has been liked')
        return redirect (request.referrer)
        
@app.route("/quack", methods=["GET", "POST"])
def post_quack():
    """Metoda pro postovani novych quacku na FrontEndu provazanim s metodou z BackEndu.
    Kontrola jestli je uzivatel prihlasen, pokud ne tak ho odkaze na loginpage. A kontrola jestli neprekrocil maximalni delku quacku(255), tento check je aktualne 'duplicitni'.
    """
    user_id = session["user_id"]
    if user_id is None:
        flash("You cannot post a quack, if you are not logged in!")
        return redirect("/login")
    elif user_id is not None and request.method == "POST":
        content = str(request.form["quack_content"])
        if len(content) == 0:
            flash("Your cannot quack an empty tweet!", "danger")
            return redirect("/profile")
        elif len(content) > 255:
            flash("Your quack is too long!", "danger")
            return redirect("/profile")
        else:
            flash("Your quack has been successfully posted!", "success")
            db.add_quack(user_id, content)
            return redirect("/profile")

@app.route('/<page>/next', methods=["GET"])
def next_page(page):
    """Funkce pro presun na dalsi stranku.
    @page: cislo stranky, kterou chceme presunout
    """
    if page == 'home':
        session['home_pages_coefficient'] += 1
        return redirect('/')
    elif page == 'profile':
        session['profile_pages_coefficient'] += 1
        return redirect('/profile')

@app.route('/<page>/previous', methods=["GET"])
def previous_page(page):
    """Funkce pro presun na predchozi stranku.
    @page: cislo stranky, kterou chceme presunout
    """
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

@app.route("/profile")
def profile():
    user_id = session['user_id']
    if user_id is None:
        return redirect('/login')
    account_name = {}
    account_name=db.who_am_i(session['user_id'])
    user = account_name['userName']
    quacks = db.my_recent_twenty_quacks(int(user_id), session['profile_pages_coefficient'])
    posts = load_20_quacks(quacks)
    return render_template('profile.html', posts=posts, account_name=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    session['home_pages_coefficient'] = 0
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
        if reg != None:
            flash('You are now registered and can log in', 'success')
            return redirect('/login')
        else:
            flash('The username is already taken', 'danger')
            return redirect('/register')
    else:
        return render_template('register.html')


@app.route("/logout")
def logout():
    session['home_pages_coefficient'] = None
    session['profile_pages_coefficient'] = None
    session['user_id'] = None
    return redirect('/login')


def load_20_quacks(quacks):
    return [ {
            'id': quack['_id'],
            'author': quack['userName'],
            'title': "title",
            'content': quack['tweetContent'],
            'date_posted': quack['dateTweeted'],
            'likes': quack['likes']
        } for quack in quacks]


if __name__ == '__main__':
    app.run(host= "0.0.0.0", port=5000, debug=True)