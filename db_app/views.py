from datetime import datetime
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from models import *
from flask import render_template, url_for, request, jsonify
from forms import *
from wtforms import FieldList, StringField
from wtforms.validators import DataRequired

# Database.database_creation()

#Spécial Editx + buzz words
#Aller chercher le graph spécifique à Editx pour ça ?
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


@app.route('/all_classifications', defaults={'user': ''})
@app.route('/<user>/all_classifications')
def all_classifications(user):
    classifications_names = MongoDB.find_all_classifications_names()  #uuid + name?
    print(classifications_names)

    return render_template('classifications_titles.html', classifications_names=classifications_names, title='all classifications')


@app.route('/<user>/my_classifications')  # classification's user only (member'space)
@login_required
def my_classifications(user):
    user_id = current_user.get_id_2()    # graphs_id = current_user.get_graphs_id()
    classifications_names = MongoDB.find_classifications_names(user_id)
    is_user_connected = True

    return render_template('classifications_titles.html', classifications_names=classifications_names,
                           title='My classifications', is_user_connected=is_user_connected)


@app.route('/classification/<name>/', defaults={'bw': 'Cloud computing'})
@app.route('/classification/<name>/<bw>')
def display_classification(name, bw):  # id au lieu de name?
    infos = MongoDB.find_classification_info(name)
    uuid_classification = str(infos['_id']) #on a qd mm besoin de uuid pour graphs
    classification = Database.find_classification(uuid_classification)
    #verifier if classification == [] (veut dire pas de uuid synchro entre mongoDB et NEo4J, ou classif vide)

    buzzwords = Database.find_buzz_words()[0]['names']

    if bw is not None:
        buzzword_fields = Database.find_buzz_word_fields(bw)
    else:
        buzzword_fields = None

    #pas obligé d'être logué : si forker --> redigige vers la page suivante et si page suivante login_required
    # --> login d'abord
    is_user_classification = False
    if current_user.is_authenticated:  #page utilisé pour all user et quand je me co (via my_classif)
        user_id = infos['user_id']
        if user_id == current_user.get_id_2():
            is_user_classification = True

        #user_classifications = current_user.get_graphs_id()
        #if uuid_classification in user_classifications:
         #   is_user_classification = True

    #If bouton traduire submit:
        # on fork ou pas?
        # redirect ou? à reflechir

    return render_template('classification.html', classification=classification, buzzWords=buzzwords,
                           buzzWordFields=buzzword_fields,
                           word=bw, name=name, uuid_classification=uuid_classification,
                           is_user_classification=is_user_classification)


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


@app.route('/add/classification/', defaults={'uuid_ancestor': None}, methods=['GET', 'POST'])
@app.route('/fork/<uuid_ancestor>/', methods=['GET', 'POST'])
@login_required
def fork(uuid_ancestor):
    form = AddClassificationForm()

    if form.validate_on_submit():       # lien avec add_classification !
        classification = {
            'name': form.name.data,
            'is_forked': True,
            'details': form.presentation.data,
            'user_id': current_user.get_id_2(),  # regler pb solution
            'logs': []
        }

        uuid_classification = MongoDB.add_classification(classification)
        if uuid_ancestor is not None:
            Database.add_fork_relationship(uuid_classification, uuid_ancestor)
        return redirect(url_for('my_classifications', user=current_user.get_username()))
    return render_template('add_classification.html', title='Add classification', form=form)

@app.route('/add_subgraph/<uuid_classification>/<new_root>/', methods=['GET', 'POST'])
@app.route('/add_subgraph/<uuid_classification>/', defaults={'new_root': None}, methods=['GET', 'POST'])
@login_required
def add_subgraph(uuid_classification, new_root):
    form = AddSubGraphForm()

    if form.add_root.data:
        #verif que juste stringfield ok !
        new_root = form.name_root.data
        Database.add_root_field(new_root, uuid_classification) #la vraie request car ne part de rien
        return redirect(url_for('add_subgraph', uuid_classification=uuid_classification, new_root=new_root))

    if form.add_field.data:
        form.name_l2.validators = [DataRequired()]
        if form.validate_on_submit():
            fields = {}
            field_l2 = form.name_l2.data
            fields_l3 = form.flist.data
            fields['level2'] = field_l2
            fields['level3'] = fields_l3
            Database.add_subgraph(new_root, fields, uuid_classification)

            #  clear the form
            form.name_l2.data = ''
            form.flist.entries.clear()
            return render_template('add_subgraph.html', new_root=new_root, form=form)

    if form.submit.data:
        return redirect(url_for('my_classifications', user=current_user.get_username()))

    return render_template('add_subgraph.html', form=form, new_root=new_root)


@app.route('/add_translation/<uuid_classification>/<language>/', methods=['GET', 'POST'])
@app.route('/add_translation/<uuid_classification>/', defaults={'language': None}, methods=['GET', 'POST'])
@login_required
def add_translation(uuid_classification, language):
    form = AddTranslationForm()
    classification_name = MongoDB.find_classification_name(uuid_classification) #Verifier que classification existe

    root_fields = Database.find_root_fields()  # préciser la classification non?
    form.root_field.choices += [(root_field['uuid'], root_field['name']) for root_field in root_fields]

    if form.valid.data:
        language = form.language.data
        return redirect(url_for('add_translation', uuid_classification=uuid_classification, language=language))

    if form.valid2.data:
        uuid_root_selected = form.root_field.data # renvoyer à html uuid ou autre chose ?
        root_selected = Database.find_name(uuid_root_selected) #id : username ou uuid????????
        field_l2 = Database.find_subfields_2(uuid_root_selected) #return dico

        return render_template('add_translation.html', form=form, field_l2=field_l2, language=language,
                               classification_name=classification_name, root_selected=root_selected)

    if form.valid3.data: #comme valid  normal
        print(request.form.items())
        for key, val in request.form.items():
            if key.startswith("f-"):
                name_field = (key.partition('-')[2]).strip()     #  Change name into uuid or not ?
                Database.add_translation(name_field, val, language)   #  Préciser quelle classification ?
        return redirect(url_for('add_translation', uuid_classification=uuid_classification, language=language))

    if form.finish.data:
        return redirect(url_for('my_classifications', user=current_user.get_username()))

    return render_template('add_translation.html', form=form, classification_name=classification_name,
                           language=language)


@app.route('/add_field/<classification_uuid>', methods=['GET', 'POST'])
@login_required
def add_field(classification_uuid):
    form = AddFieldForm()

    root_fields = Database.find_root_fields()
    level2_fields = Database.find_same_level_fields(2)

    form.root_field_attached.choices += [(root_field['uuid'], root_field['name']) for root_field in root_fields]
    form.level2_field.choices += [(field['uuid'], field['name']) for field in level2_fields] # a afficher + executer que qd nécessaire

    if form.submit.data:  #for verification
        if form.level.data == '2':
            form.root_field_attached.validators = [DataRequired()]
        if form.level.data == '3':
            form.root_field_attached.validators = [DataRequired()]
            form.level2_field.validators = [DataRequired()]
        if form.validate_on_submit():
            name = form.name.data
            level = form.level.data
            req = ""
            if form.level.data == '2':
                uuid_root = form.root_field_attached.data
                req = Database.add_field_request(name, level, 'include', uuid_root)

            if form.level.data == '3':
                uuid_level2_field = form.level2_field.data
                req = Database.add_field_request(name, level, 'include', uuid_level2_field)

            mongo.db.Classification.update_one({'_id': ObjectId(classification_uuid)},
                                               {"$push": {'logs': {'timestamp': datetime.utcnow(), 'request': req}}},
                                               upsert=False)

            return redirect(url_for('my_classifications', user=current_user.get_username()))

    return render_template('add_field.html', form=form)


@app.route('/add_relation/<classification_uuid>', methods=['GET', 'POST'])
@login_required
def add_relation(classification_uuid):
    form = AddRelForm()

    root_fields = Database.find_root_fields()
    all_fields = Database.find_all_fieldsss()
    form.root_field1.choices += [(root_field['uuid'], root_field['name']) for root_field in root_fields]
    form.field1.choices += [(field['uuid'], field['name']) for field in all_fields]
    form.root_field2.choices += [(root_field['uuid'], root_field['name']) for root_field in root_fields]
    form.field2.choices += [(field['uuid'], field['name']) for field in all_fields]

    if form.submit.data:
        if form.validate_on_submit():
            uuid_field1 = form.field1.data
            uuid_field2 = form.field2.data
            rel = form.type_rel.data

            req = Database.add_rel_request(uuid_field1, uuid_field2, rel)
            mongo.db.Classification.update_one({'_id': ObjectId(classification_uuid)},
                                               {"$push": {'logs': {'timestamp': datetime.utcnow(), 'request': req}}},
                                               upsert=False)
            # upsert parameter will insert instead of updating if the post is not found in the database.
            return redirect(url_for('my_classifications', user=current_user.get_username()))  # bonne page?

    return render_template('add_relation.html', form=form)


@app.route('/edit_relation/<classification_uuid>', methods=['GET', 'POST'])
@login_required
def edit_relation(classification_uuid):
    form = EditRelForm()

    root_fields = Database.find_root_fields()
    all_fields = Database.find_all_fieldsss()
    form.root_field1.choices += [(root_field['uuid'], root_field['name']) for root_field in root_fields]
    form.field1.choices += [(field['uuid'], field['name']) for field in all_fields]
    form.root_field2.choices += [(root_field['uuid'], root_field['name']) for root_field in root_fields]
    form.field2.choices += [(field['uuid'], field['name']) for field in all_fields]

    if form.delete.data:
        if form.validate_on_submit(): #validation in form.py est suffisante?
            uuid_field1 = form.field1.data
            uuid_field2 = form.field2.data
            rel = form.actual_rel.data
            req = Database.delete_relation_request(uuid_field1, uuid_field2, rel)
            mongo.db.Classification.update_one({'_id': ObjectId(classification_uuid)},
                                               {"$push": {'logs': {'timestamp': datetime.utcnow(), 'request': req}}},
                                               upsert=False)
            return redirect(url_for('my_classifications', user=current_user.get_username()))
    if form.edit.data:
        form.type_rel.validators = [DataRequired()]
        if form.validate_on_submit():
            uuid_field1 = form.field1.data
            uuid_field2 = form.field2.data
            new_rel = form.type_rel.data

            req = Database.edit_rel_request(uuid_field1, uuid_field2, form.actual_rel.data, new_rel)
            mongo.db.Classification.update_one({'_id': ObjectId(classification_uuid)},
                                               {"$push": {'logs': {'timestamp': datetime.utcnow(), 'request': req}}},
                                               upsert=False)
            # upsert parameter will insert instead of updating if the post is not found in the database.
            return redirect(url_for('my_classifications', user=current_user.get_username()))  # bonne page?

    return render_template('edit_relation.html', form=form)

@app.route('/edit_field/<classification_uuid>', methods=['GET', 'POST'])
@login_required
def edit_field(classification_uuid):
    form = EditFieldForm()

    # print(form.errors)
    root_fields = Database.find_root_fields()    #IL FAUT RECONSTRUIRE LA DB ICI
    all_fields = Database.find_all_fieldsss()
    form.root.choices += [(root_field['uuid'], root_field['name']) for root_field in root_fields]
    form.fields.choices += [(field['uuid'], field['name']) for field in all_fields]

    if form.delete.data:
        if form.validate_on_submit():
            uuid_field = form.fields.data
            req = Database.delete_field_request(uuid_field)
            timestamp = datetime.utcnow()
            mongo.db.Classification.update_one({'_id': ObjectId(classification_uuid)},
                                               {"$push": {'logs': {'timestamp': timestamp, 'request': req}}},
                                               upsert=False)
            return redirect(url_for('all_classifications'))  # redirect to la même page? pour autre modification

    if form.edit.data:
        form.new_field.validators = [DataRequired()]
        if form.validate_on_submit():
            uuid_field = form.fields.data
            new_name = form.new_field.data
            req = Database.edit_field_request(uuid_field, new_name)
            timestamp = datetime.utcnow()
            mongo.db.Classification.update_one({'_id': ObjectId(classification_uuid)},
                                               {"$push": {'logs': {'timestamp': timestamp, 'request': req}}},
                                               upsert=False)
            # upsert parameter will insert instead of updating if the post is not found in the database.
            return redirect(url_for('all_classifications'))  # bonne page?

    return render_template('edit_classification.html', form=form)


@app.route('/get_fields/<id_root>')
def get_fields(id_root):
    fields = Database.find_fields(id_root)
    if not fields:  # si le dico est vide
        return jsonify([])
    else:
        return jsonify(fields)


@app.route('/get_rel/<id_field1>/<id_field2>')
def get_rel(id_field1, id_field2):
    rel = Database.find_rel(id_field1, id_field2)
    print(rel)
    if not rel:  # si le dico est vide
        return jsonify([])
    else:
        return jsonify(rel) #rel est juste un mot, transforme en liste or not?


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():  # Si GET return False
        user = mongo.db.Users.find_one_or_404({"username": form.username.data})
        print(user['_id'])
        if user and User.check_password(user['password'], form.password.data):
            user_obj = User(username=user['username'])
            user_obj.set_var(lastname=user['lastname'], firstname=user['firstname'], email=user['email'],
                             job=user['job'], website_url=user['website_url'], graphs_id=user['graphs_id'], id=user['_id'])
            # redondance avec load_user?? juste username et c ok normalement
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
