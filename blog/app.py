from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__= "Posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    createdat = db.Column(db.DateTime, default= db.func.now())
    updateat = db.Column(db.DateTime, default= db.func.now(), onupdate=db.func.now())


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

if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()