from .models import Field, Question, Database
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    f= Field("os", 1)
    f2= Field("file managment",2)
    f3= Field("management", 1)
    f4=Field("os222", 2)
    q= Question("How are you?", "Houda")
    f5= Field("computer systems", 3)
    #oui = Database.find_one_field('os')
    #Database.add_field(f2)
    #Database.add_subfield_relationship(f3, f4)
    #Database.add_subfield_relationship(f3,f2)
    os = Field('operating systems', 2)
    Database.modify_field(f2, f5)
    #Database.delete_field(os)
    #Database.delete_relation(f3, f4, "subfield")
    #next(oui)['f']['name']
    return render_template('index.html', newfield = "coucou")
