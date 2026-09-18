from flask import Flask, request, jsonify, render_template, url_for, redirect, session, flash
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = '12345678'

hash_salt = bcrypt.gensalt()

DB_CONFIG = {
    "dbname" : "postgres",
    "user" : "postgres",
    "password" : "comfy.exe@1234",
    "host" : "localhost",
    "port" : "5432"
}

def get_db_conn():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    
    username = 'Comfy'
    password = 'admin@1234'
    email = 'bandacomfo13@gmail.com'
    password_hash = bcrypt.hashpw(password.encode("utf-8"), hash_salt).decode("utf-8")

    with conn.cursor() as cursor:
        query = 'INSERT INTO admin_user (username, password, email) VALUES(%s, %s, %s) ON CONFLICT(username) DO NOTHING;'
        cursor.execute(query, (username, password_hash, email))
        conn.commit()

    return conn


@app.route('/admin_logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_encoding = password.encode("utf-8")

        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin_user WHERE username=%s::text;', (username, ))
        user = cursor.fetchone()
        
        if user:
            conn.close()

            user_password_hash = user['password']
            User_Password_Hash_Encoding = user_password_hash.encode("utf-8")

            if bcrypt.checkpw(password_encoding, User_Password_Hash_Encoding):
                session['logged_in'] = True
                return redirect(url_for('admin_dashboard'))
        
        else:
            return render_template('admin_login.html', error='Invalid Credentials! Try again...')
        
    return render_template('admin_login.html')
   

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')


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
    app.run(debug=True)