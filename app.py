from flask import Flask, render_template
app = Flask(__name__)

posts = [
    {
        'author': 'Alexander',
        'title': 'Pp poo poo',
        'content': 'It realy do be',
        'date_posted': '25. November 2023'
    },
    {
        
        'author': 'Daniel',
        'title': 'yes',
        'content': 'pes',
        'date_posted': '26. November 2023'
    },
    {
        
        'author': 'Adam',
        'title': 'nope',
        'content': 'coke',
        'date_posted': '27. November 2023'
    }
]

@app.route("/")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')
if __name__ == '__main__':
    app.run(debug=True)
@app.route("/profile")
def profile():
    return render_template('profile.html')
@app.route("/register")
def about():
    return render_template('register.html')