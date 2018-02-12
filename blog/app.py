from flask import Flask, render_template, abort, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from forms import LoginForm
import os

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

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    createdat = db.Column(db.DateTime, default= db.func.now())
    updateat = db.Column(db.DateTime, default= db.func.now(), onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<Post %r>' % (self.content)



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
        post.constent = content

        db.session.commit()

        return redirect(url_for('post', id=id))
    else:
        return render_template('edit.html', post=post)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()