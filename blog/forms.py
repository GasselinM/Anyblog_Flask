from flask_wtf import FlaskForm
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import TextField, TextAreaField, SubmitField
import wtforms

#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PostForm(Form):
    title = TextField('Title')
    Content = TextAreaField('Content')
    submit = SubmitField('Submit')
