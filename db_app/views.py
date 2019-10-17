from .models import Field, Question, Database
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    allFields = Database.find_all_fields()
    q1 = Question('titre1','reponse1')
    q2 = Question('titre2','reponse2')
    q3 = Question('titre3','reponse3')
    q4 = Question('titre4','reponse4')
    q5 = Question('titre5', 'reponse5')
    q6 = Question('titre6', 'reponse6')
    q7 = Question('titre7', 'reponse7')
    q8 = Question('titre8', 'reponse8')

    return render_template('index.html', allFields=allFields)

@app.route('/questions/<fieldName>')
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
