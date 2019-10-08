#from .models import
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
