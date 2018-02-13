from flask import Flask, render_template, abort, flash, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from wtforms import Form
import forms
import os
from flask import render_template, request, flash
from flask_login import LoginManager
from flask_login import login_required



#from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

#from flaskext.mail import Mail, Message


app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
#basedir = os.path.abspath(os.path.dirname(__file__))



#admin = Admin(app, name='microblog', template_mode='bootstrap3')
#admin.add_view(ModelView(title, db.session))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite3'
#app.config.from_object('config')
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

admin = Admin(app)
login_manager = LoginManager()
login_manager.init_app(app)


db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    #posts = db.relationship('Post', backref='author', lazy='dynamic')
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

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<Post %r>' % (self.content)

admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(User, db.session))



@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/contact")
def contact():
    return render_template("pages/contact.html")

@app.route("/aboutme")
def aboutme():
    return render_template("pages/aboutme.html")

@app.route("/blog")
def posts_index():
    posts = Post.query.all()
    return render_template("posts/index.html", posts=posts)

@app.route('/blog/posts/<int:id>')
def posts_show(id):
    post= Post.query.get(id)
    if post is None :
        abort(404)
    return render_template('posts/show.html', post=post)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('pages/error404.html'), 404


@app.route('/new', methods = ['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['content'] or not request.form['title']:
            flash('Please enter all the fields', 'error')
        else:
            postarticle = Post(request.form['title'], request.form['content'])
            db.session.add(postarticle)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('posts_index'))
    return render_template('form.html')


@app.route('/editpost/<int:id>', methods=['GET', 'POST'])
def editpost(id):
    post = db.session.query(Post).filter(Post.id==id).first()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        post.title = title
        post.content = content

        db.session.commit()
        flash('Record was successfully edited')

        return redirect(url_for('posts_show', id=id))
    else:
        return render_template('edit.html', post=post)



@app.route('/deletepost/<int:id>', methods=['GET'])
def deletepost(id):
    post = db.session.query(Post).filter(Post.id==id).first()
    toto = db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted!")
    return redirect(url_for('posts_index'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = forms.SignupForm()
   
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.nickname.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            session['email'] = newuser.email       
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(email = session['email']).first()
    if user is None:
        return redirect(url_for('signin'))
    else:
        return render_template('pages/profile.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = forms.SigninForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            session['email'] = form.email.data
            return redirect(url_for('profile'))                    
    elif request.method == 'GET':
        return render_template('signin.html', form=form)

@app.route('/signout')
def signout():
    if 'email' not in session:
        return redirect(url_for('signin'))
    session.pop('email', None)
    flash("You have been logged out")
    return redirect(url_for('home'))
    

if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()