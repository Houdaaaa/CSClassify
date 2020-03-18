from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
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




class EditFieldForm(FlaskForm):
    #level = SelectField('Field level', choices=[(1,1), (2,2), (3,3)])
    root = SelectField('Root', choices=[("", "-- select an option --")], validators=[DataRequired()])
    fields = SelectField('Fields', choices=[("", "-- select an option --")], validators=[DataRequired()])
    new_field = StringField('New field')
    edit = SubmitField('Edit')
    delete = SubmitField('Delete')

    def validate_root(self, root):
        print(root.data)
        #si = ---select option -- : choose an option please

    def validate_fields(self, fields):
        print('ok')

    def validate_edit(self, edit):
        def validate_new_field(self, new_field):
            print('oknnnn')
        print(self.new_field)
        if self.new_field.data == '' :
            raise ValidationError('Please complete the niew field field ')