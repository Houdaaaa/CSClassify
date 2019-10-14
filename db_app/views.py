from .models import Field, Question, Database
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    allFields = Database.find_all_fields()
    return render_template('index.html', allFields=allFields)
