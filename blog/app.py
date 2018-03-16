from flask import Flask, render_template, abort, flash, redirect, request, url_for, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from wtforms import Form
import forms
from classalchemy import  User, Post, Poleemploi
import os
from flask import render_template, request, flash

import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


from weboob.core import Weboob
from weboob.capabilities.job import CapJob


app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



with app.app_context():
    db.init_app(app)

admin = Admin(app)
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(User, db.session))


@app.route('/newjobs', methods = ['GET', 'POST'])
def new_jobs():
    w = Weboob()
    w.load_backends(CapJob)
    #w['popolemploi']
    words = u'python'
    jobs=w.search_job(words)
    jobs=list(jobs)
    Poleemploi.query.delete()
    for job in jobs:
        new = Poleemploi(society_name=job.society_name, place=job.place, title=job.title , contract_type=job.contract_type , publication_date=job.publication_date )
        db.session.add(new)
        db.session.commit()
    return redirect(url_for('jobs_index'))


@app.route("/jobs")
def jobs_index():
	jobs = Poleemploi.query.order_by(Poleemploi.id.desc()).limit(10)
	return render_template("posts/jobs.html", jobs=jobs)

@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/contact")
def contact():
    return render_template("pages/contact.html")

@app.route("/aboutme")
def aboutme():
    return render_template("pages/aboutme.html")

####
@app.route("/blog")
def posts_index():
	#posts = Post.query.all()
	posts = Post.query.order_by(Post.createdat.desc()).all()
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
            auth= User.query.filter_by(email = session['email']).first()
            postarticle = Post(request.form['title'], request.form['content'], author=auth.email)
            db.session.add(postarticle)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('posts_index'))
    return render_template('form.html')


@app.route('/editpost/<int:id>', methods=['GET', 'POST'])
def editpost(id):
    post = db.session.query(Post).filter(Post.id==id).first()
    auth = User.query.filter_by(email = session['email']).first()
    if post.author == auth.email:

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
    else:
        flash('you must be the owner of the post!!')
        return  redirect(url_for('posts_show', id=id))



@app.route('/deletepost/<int:id>', methods=['GET'])
def deletepost(id):
    post = db.session.query(Post).filter(Post.id==id).first()
    auth = User.query.filter_by(email = session['email']).first()
    if post.author == auth.email:
        toto = db.session.delete(post)
        db.session.commit()
        flash("Post has been deleted!")
        return redirect(url_for('posts_index'))
    flash('you must be the owner of the post!!')
    return redirect(url_for('posts_index'))


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
            session['nickname'] = newuser.nickname
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(email = session['email']).first()
    #nickname = User.query.filter_by('nickname').first()
    if user is None:
        return redirect(url_for('signin'))
    else:
        return render_template('pages/profile.html', users=user)


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



@app.route('/user', methods=['GET'])
def get_all_users():
    if 'email' not in session:
        return redirect(url_for('signin'))

    userss = User.query.all()
    output = []

    for user in userss:
        user_data = {}
        user_data['uid'] = user.uid
        user_data['nickname'] = user.nickname
        user_data['email'] = user.email
        user_data['pwdhash'] = user.pwdhash
        output.append(user_data)

    return jsonify({'users' : output})

@app.route('/posts', methods=['GET'])
def get_all_post():
    if 'email' not in session:
        return redirect(url_for('signin'))

    posts = Post.query.all()

    output = []

    for post in posts:
        user_post = {}
        user_post['id'] = post.id
        user_post['title'] = post.title
        user_post['content'] = post.content
        user_post['createdat'] = post.createdat
        user_post['updateat'] = post.updateat
        user_post['user_id'] = post.user_id
        output.append(user_post)

    return jsonify({'posts' : output})

if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()