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

    '''for field in rootFieldsList:
        for field2 in Database.find_sub_nodes_node(field, 'subfield'):
            fieldsL2List[field['name'] = field2['name']
            for field3 in Database.find_sub_nodes_node(field2, 'subfield'):
                fieldsL2List[field['name'] = [field2['name']] 
                = field3['name']  # --> {'storage management': 'files systems'}
                #fieldsL2List[field2['name']] = {'name':field3['name'], 'level':field3['level']}  --> #{'storage management': {'name': 'files systems', 'level': 3}}
    '''


    print(fieldsL2List)



    return render_template('index.html', rootFieldsList=rootFieldsList)
