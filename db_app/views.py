from .models import Field, Question, Database
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    # if Database.find_sub_nodes(field, 'subfield') != None
    rootFieldsList = Database.find_same_level_fields(1)
    fieldsL2List = {}

    f1 = Field('operating systems',1)
    f2 = Field('computer systems', 1)
    f3 = Field('programming', 1)
    f4 = Field('storage management', 2)
    f5 = Field('files systems', 3)
    f6 = Field('memory management', 3)
    f7 = Field('os types', 2)
    f8 = Field('languages', 2)
    f9 = Field('paradigms', 2)
    f10 = Field('imperative', 3)


    levels_1_2, levels_2_3 = Database.find_subfields_2(f1)
    allFields = Database.find_subfields_3()



    return render_template('index.html', allFields=allFields )
