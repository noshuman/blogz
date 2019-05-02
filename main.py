from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

from datetime import datetime

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Build-A-Blog:bob@localhost:8889/Build-A-Blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1500))
    created = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()  
        self.owner = owner

    def is_valid(self):
        if self.title and self.body and self.created and self.owner:
            return True
        else:
            return False   

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(15))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password    

@app.before_request
def require_login():
    allowed_routes = ['index','blog','login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return redirect('index.html', users=users)

@app.route('/blog', methods=['POST','GET'])
def blogentries():
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("singleuser.html", page_title = user.username + " 's Blog Posts", user_blogs=user_blogs)

    singlepost = request.args.get('id')
    if singlepost:
        blog = Blog.query.get(singlepost)
        return render_template("viewpost.html", blog=blog)

    else:
        blogs = Blog.query.all()
        return render_template('index.html', page_title="All Blog Posts", blogs=blogs)
        

@app.route('/newblog', methods = ['GET', 'POST'])

def newblog():
    if request.method == 'GET':
        return render_template('newblog.html')

    if request.method == 'POST':
        newtitle = request.form['title']
        newbody = request.form['body']
        newblog = Blog(newtitle, newbody)

        if newblog.is_valid():
            owner = User.query.filter_by(username=session['username']).first()
            newblog = Blog(newtitle, newbody, newblog, owner)
            db.session.add(newblog)
            db.session.commit()
            url = "/blog?id=" + str(newblog.id)
            return redirect(url)

        else:
            error = "Please check your blog post for errors. Please make sure that both a valid title and body have been included with your blog."
            return render_template('newblog.html', error=error, title="Create New Blog Post ", newtitle=newtitle, newbody=newbody)
        

    else:
        return render_template('newblog.html', title="Create New Blog Post")

@ app.route ("/signup", methods= ['GET', 'POST'])

def error():
    
    username_error = ""
    password_error = ""
    verifypassword_error = ""


    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verifypassword']

    
        if len(username) == 0:
            username_error = "Please enter a username."

        if len(username)  <=2 or len(username) >=20:
            username_error = "Your username does not meet the length requirements, usernames must be at least 3 characters long and cannot exeed 20 charaters."

        if username.count(" ") != 0:
            username_error = "Spaces are invalid for usernames, please re-enter your username without any spaces."   

        if len(password) == 0:
           password_error = "Please enter a password"

        if len(password)  <=2 or len(password) >=20:
            password_error = "Your password does not meet the length requirements, usernames must be at least 3 characters long and cannot exeed 20 charaters."

        if password.count(" ") !=0: 
            pasword_error = "Spaces are invalid for passwords, please re-enter your password without any spaces"  

        if len(verifypassword) == 0:
            verifypassword_error = "Please verify your password."

        if password != verifypassword:
            password_error ="Your entry does not match your password entry, please re-enter your password." 

        if len(username_error) != 0 or len(password_error) !=0  or len(verifypassword_error) != 0:
            return render_template("index.html", username_error=username_error, password_error=password_error, verifypassword_error=verifypassword_error)

        existinguser = User.query.filter_by(username=username).first()
        if existinguser:
            username_error = "That name already exists, please select another name."
            return render_template('signup.html', username_error=username_error)

        if not existinguser:
            newuser = User(username, password)
            db.session.add(newuser)
            db.session.commit()
            session['username'] = username
            return redirect('/newblog')     
    else: 
        return render_template("signup.html", username=username)    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html", pagetitle='Login')
        else:
            return redirect('/newblog')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newblog')

        if user and user.password != password:
            password_error = "Incorrect Password"
            return render_template('login.html', password_error=password_error)

        if not user:
            username_error = "The User Name is Incorrect"
            return render_template('login.html', username_error=username_error)

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ =='__main__':
    app.run()