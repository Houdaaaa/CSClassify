from .models import Field, Question, Database
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    allFields = Database.find_all_fields()
    q1 = Question('titre1','42')
    q2 = Question('titre2','43')
    q3 = Question('titre3','jesaispas')
    q4 = Question('titre4','qlqch')
    f1 = Field('os types', 2)
    f2 = Field('memory management', 3)

    f1 = Field('os types', 2)
    f2 = Field('memory management', 3)
    f3 = Field('operating systems', 1)


    return render_template('index.html', allFields=allFields)

@app.route('/questions/<fieldName>')
def display_questions(fieldName):
    field = Field(fieldName, 0) #A t-on besoin du level? à voir
    questionsList= Database.find_questions(field)
    subfields= Database.find_subfields(fieldName)
    return render_template('questions.html', field=fieldName, questionsList=questionsList, subfields=subfields)
