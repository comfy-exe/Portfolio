from flask import Flask, request, jsonify, render_template, url_for, redirect, session, flash
# import bcrypt
# import psycopg2
import os
# from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/bio')
def bio():
    return render_template('bio.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contacts')
def contacts():
    contact_info = {
        "phone_1" : +265887766457,
        "phone_2" : +265997042188,
        "email" : "bandacomfo13@gmail.com"
    }

    return render_template('contacts.html', contact = contact_info)


if __name__=='__main__':
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)