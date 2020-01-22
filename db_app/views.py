from .models import Database
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', defaults={'bw': 'Cloud computing'})  # to pre-select a buzz word
@app.route('/<bw>')
def index(bw):
    #Database.database_creation()

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
        concerned_field['subfields'] = (Database.find_subfields(field['name']))  # return list of dictionaries
        concerned_fields.append(concerned_field)

    return render_template('questions.html', field=field_name, questionsList=questions_list, subfields=subfields,
                           concernedFields=concerned_fields)


if __name__ == "__main__":
    app.run()