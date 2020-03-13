from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from models import *  #pour mongo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    lastname = StringField('Lastname', validators=[DataRequired()])
    firstname = StringField('Firstname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    job = StringField('Job', validators=[DataRequired()])
    website_url = StringField('Website url', validators=[DataRequired()])  #Optionnal?
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    #Pas de graphs_id : l'ajouter dans users

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = mongo.db.Users.find_one({"username": username.data}) #.first()?
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = mongo.db.Users.find_one({"email": email.data})
        if user is not None:
            raise ValidationError('Please use a different email address.')