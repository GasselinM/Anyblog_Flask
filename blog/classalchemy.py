from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash




db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, nickname, email, password):
        self.nickname = nickname.title()
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)
   
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    createdat = db.Column(db.DateTime, default= db.func.now())
    updateat = db.Column(db.DateTime, default= db.func.now(), onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    author = db.Column(db.String(255))

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

    def __repr__(self):
        return '<Post %r>' % (self.content)

class Poleemploi(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    society_name = db.Column(db.Text)
    place = db.Column(db.Text)
    title = db.Column(db.Text)
    contract_type = db.Column(db.Text)
    publication_date = db.Column(db.DateTime)

    def __init__(self, society_name, place, title, contract_type, publication_date):
        self.title = title
        self.society_name = society_name
        self.place = place
        self.contract_type = contract_type
        self.publication_date = publication_date


    def __repr__(self):
        return '<Job %r>' % (self.title)