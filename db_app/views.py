from .models import Field, Question, Database
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    rootFieldsList = Database.find_same_level_fields('1')

    return render_template('index.html', rootFieldsList=rootFieldsList)
