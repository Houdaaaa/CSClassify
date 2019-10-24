from .models import Field, Question, Database
from flask import Flask, request, session, redirect, url_for, render_template, flash
import json
import os

app = Flask(__name__)

@app.route('/', defaults={'bw': 'Cloud computing'})
@app.route('/<bw>')
def index(bw):
    allFields = Database.find_all_fields()

    q1 = Question('titre1','reponse1')
    q2 = Question('titre2','reponse2')
    q3 = Question('titre3','reponse3')
    q4 = Question('titre4','reponse4')
    q5 = Question('titre5', 'reponse5')
    q6 = Question('titre6', 'reponse6')
    q7 = Question('titre7', 'reponse7')
    q8 = Question('titre8', 'reponse8')

    '''Database.add_buzz_word('cloud computing')
    Database.add_is_linked_to_relationship('cloud computing', 'memory management' )
    Database.add_is_linked_to_relationship('cloud computing', 'files systems')
    Database.add_is_linked_to_relationship('cloud computing', 'object-oriented')
    Database.add_is_linked_to_relationship('cloud computing', 'threads')
    Database.add_is_linked_to_relationship('cloud computing', 'Computer systems')
    Database.add_is_linked_to_relationship('cloud computing', 'real-time systems')'''

    #Database.database_creation()

    if bw != None:
        buzzWordFields = Database.find_buzz_word_fields(bw)
    else:
        buzzWordFields = None

    buzzWords = Database.find_buzz_words()[0]['names']
    print("zero")
    print(buzzWordFields)

    return render_template('index.html', allFields=allFields, buzzWordFields=buzzWordFields, buzzWords=buzzWords, word=bw )

@app.route('/questions/<fieldName>/')
def display_questions(fieldName):
    field = Field(fieldName, 0) #A t-on besoin du level? à voir
    questionsList= Database.find_questions(field)
    subfields= Database.find_subfields(fieldName)
    concernedFieldsName = Database.find_concerned_fields(fieldName) #return list of dico [{'name' : 'os'}, {}]
    concernedFields = []
    for field in concernedFieldsName:
        concernedField = {}
        concernedField['name'] = field['name']
        concernedField['subfields'] = (Database.find_subfields(field['name']))# liste de dico
        concernedFields.append(concernedField)
    print(concernedFields) #Liste de dico (un dico pour chaque concernedFieldsName), dans ce dico la clé subfields est une liste de subfields (rpzté en dico)

    return render_template('questions.html', field=fieldName, questionsList=questionsList, subfields=subfields, concernedFields=concernedFields)
