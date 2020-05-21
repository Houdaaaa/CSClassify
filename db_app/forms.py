from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FieldList
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from models import *  # pour mongo et Database
from wtforms.widgets import TextArea


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

class AddClassificationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    presentation = StringField('Presentation text', validators=[DataRequired()], widget=TextArea())

    submit = SubmitField('Submit')

class AddFieldForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    level = SelectField('Level', choices=[("", "-- select an option --"), ('1', '1'), ('2', '2'), ('3', '3')], validators=[DataRequired()])
    root_field_attached = SelectField('Associated root field',
                                choices=[("", "-- select an option --")]) # enlever DataRequired
    level2_field = SelectField('Associated level 2 field',
                               choices=[("", "-- select an option --")])  # enlever DataRequired
    submit = SubmitField('Submit')


class AddRelForm(FlaskForm):
    root_field1 = SelectField('Root field 1', choices=[("", "-- select an option --")], validators=[DataRequired()])
    root_field2 = SelectField('Root field 2', choices=[("", "-- select an option --")], validators=[DataRequired()])
    field1 = SelectField('Field 1', choices=[("", "-- select an option --")], validators=[DataRequired()])
    field2 = SelectField('Field 2', choices=[("", "-- select an option --")], validators=[DataRequired()])
    type_rel = SelectField('Relation to add',
                           choices=[("", "-- select an option --"), ('include', 'include'), ('concerns', 'concerns'),],
                           validators=[DataRequired()])
    actual_rel = StringField('Actual relation', render_kw={'readonly': True})

    submit = SubmitField('Add')

    def validate_actual_rel(self, actual_rel):
        if (actual_rel.data != '') and (actual_rel.data == self.type_rel.data):
            raise ValidationError('The relation already exist ')

    def validate_type_rel(self, type_rel):
        uuid_field1 = self.field1.data
        uuid_field2 = self.field2.data
        level_field1 = Database.find_level(uuid_field1)
        level_field2 = Database.find_level(uuid_field2)
        if type_rel.data == 'include':
            if level_field1 > level_field2:    # un level1 peut-il include un level3 ?
                raise ValidationError('The relation can exist only if field1 level < field2 level ')

class EditRelForm(FlaskForm):
    root_field1 = SelectField('Root field 1', choices=[("", "-- select an option --")], validators=[DataRequired()])
    root_field2 = SelectField('Root field 2', choices=[("", "-- select an option --")], validators=[DataRequired()])
    field1 = SelectField('Field 1', choices=[("", "-- select an option --")], validators=[DataRequired()])
    field2 = SelectField('Field 2', choices=[("", "-- select an option --")], validators=[DataRequired()])
    type_rel = SelectField('Edit in ',
                           choices=[("", "-- select an option --"), ('include', 'include'), ('concerns', 'concerns')])
    actual_rel = StringField('Actual relation', render_kw={'readonly': True})

    edit = SubmitField('Edit')
    delete = SubmitField('Delete')

    def validate_actual_rel(self, actual_rel):
        if actual_rel.data == '':
            raise ValidationError('There is no relationship between the two fields. '
                                  ' Please select two fields that are related to each other. ')


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


class AddSubGraphForm(FlaskForm):
    name_root = StringField('Name of the root field', validators=[DataRequired()]) # forcément level = 1
    name_l2 = StringField('Name of the level 2 field')
    flist = FieldList(StringField())

    add_root = SubmitField('valid root')
    add_field = SubmitField('add another field level 2')  # level 2
    submit = SubmitField('Finish')


class AddTranslationForm(FlaskForm):
    language = SelectField('Language', choices=[('FR', 'French'), ('EN', 'English'), ('SP', 'Spain'), ('NL', 'Dutch')], validators=[DataRequired()])
    root_field = SelectField('Choose the root field that you want to translate', choices=[("", "-- select an option --")], validators=[DataRequired()])
    root_translation = StringField('Root traduction', validators=[DataRequired()])

    valid = SubmitField('Validate')
    valid2 = SubmitField('Validate')
    valid3 = SubmitField('Save and translate a new subgraph')
    finish = SubmitField('Finish')