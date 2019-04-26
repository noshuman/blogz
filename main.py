from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

from datetime import datetime

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Build-A-Blog:bob@localhost:8889/Build-A-Blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1500))
    created = db.Column(db.DateTime)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()

    def is_valid(self):
        if self.title and self.body and self.created:
            return True
        else:
            return False   
    
@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def blogentries():
    entryid = request.args.get('id')
    if (entryid):
        entry = Entry.query.get(entryid)
        return render_template('singleentry.html', title="Blog Post", entry=entry)
    sort = request.args.get('sort')
    if (sort == "newest"):
        all_entries = Entry.query.order_by(Entry.created.desc()).all()
    else:
        all_entries = Entry.query.all()

    return render_template('allentries.html', title="All Blog Entries", all_entries=all_entries)    

@app.route('/newentry', methods = ['GET', 'POST'])

def newentry():
    if request.method == 'POST':
        newtitle = request.form['title']
        newbody = request.form['body']
        newentry = Entry(newtitle, newbody)

        if newentry.is_valid():
            db.session.add(newentry)
            db.session.commit()
            url = "/blog?id=" + str(newentry.id)
            return redirect(url)

        else:
            error = "Please check your blog post for errors. Please make sure that both a valid title and body have been included with your entry."
            return render_template('newentry.html', error=error, title="Create New Blog Post ", newtitle=newtitle, newbody=newbody)
        

    else:
        return render_template('newentry.html', title="Create New Blog Post")


if __name__ =='__main__':
app.run()