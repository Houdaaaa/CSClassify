from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from models import *
from flask import Flask, render_template, url_for, request, flash
from forms import LoginForm, RegistrationForm


# Database.database_creation()

@app.route('/', defaults={'bw': 'Cloud computing'})  # to pre-select a buzz word
@app.route('/<bw>')
def index(bw):

    all_fields = Database.find_all_fields()

    buzzwords = Database.find_buzz_words()[0]['names']

    if bw is not None:
        buzzword_fields = Database.find_buzz_word_fields(bw)
    else:
        buzzword_fields = None

    return render_template('index.html', allFields=all_fields, buzzWords=buzzwords, buzzWordFields=buzzword_fields,
                           word=bw)


@app.route('/questions/<field_name>/')
def display_questions(field_name):
    questions_list = Database.find_questions(field_name)
    subfields = Database.find_subfields(field_name)
    concerned_fields_name = Database.find_concerned_fields(field_name)  # return list of dictionaries
                                                                        # example: [{'name' : 'os'}, {}]

    concerned_fields = []  # list of dictionaries --> one dict for each concerned_field
                                               #  --> key "subfields is a list of subfields
    for field in concerned_fields_name:
        concerned_field = {}
        concerned_field['name'] = field['name']
        uuid = field['uuid']
        print(uuid)
        concerned_field['subfields'] = (Database.find_subfields(field['name']))  # return list of dictionaries
        concerned_fields.append(concerned_field)

    return render_template('questions.html', field=field_name, questionsList=questions_list, subfields=subfields,
                           concernedFields=concerned_fields)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():           #Si GET return False
        user = mongo.db.Users.find_one_or_404({"username": form.username.data})
        if user and User.check_password(user['password'], form.password.data):
            user_obj = User( username=user['username'])
            user_obj.set_var(lastname=user['lastname'], firstname=user['firstname'], email=user['email'],
                                        job=user['job'], website_url=user['website_url'])
            login_user(user_obj, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            return redirect(url_for('login'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user_obj = User(username=form.username.data)
        user_obj.set_var(form.lastname.data, form.firstname.data, form.email.data, form.job.data,
                                        form.website_url.data)
        user_obj.set_password(form.password.data)
        user_doc = user_obj.convert_to_doc()
        mongo.db.Users.insert_one(user_doc)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


if __name__ == "__main__":
    app.secret_key = 'mysecret'  # to change and to securise
    app.run(debug=True)