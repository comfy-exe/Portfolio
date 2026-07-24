from flask import Flask, request, jsonify, render_template, url_for, redirect, session, flash
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import smtplib
from datetime import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email


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
    if request.method == 'POST':
        name = request.form.get('name')
        sender_email = request.form.get('email')
        message = request.form.get('message')
        valid_sender_email = validate_sender_email(sender_email)

        if not valid_sender_email:
            return flash('Email not valid!', 'danger')
        
        data = {
            "name" : name,
            "email" : valid_sender_email,
            "message" : message
        }

        success = send_email(data)

        if success == True:
            flash('Your Email as been sent successfully! I will respond to you as soon as possible!', 'success')

        else:
            flash('Error sending email! Sending failed.', 'error')


    return render_template('contacts.html')

def validate_sender_email(email):
    try:
        valid_email = validate_email(email)
        return True, valid_email.email
    except EmailNotValidError as e:
        return False, str(e)


def send_email(data):
    #Email Configuration for SMTP
    SMTP_HOST = os.environ.get('EMAIL_HOST')
    SMTP_PORT = os.environ.get('EMAIL_PORT', 587)
    SMTP_USER = os.environ.get('EMAIL_USER')
    SMTP_USER = data.get('email')
    SMTP_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    RECIPIENT_EMAIL = os.environ.get('EMAIL_RECIPIENT')

    try:
        msg = MIMEMultipart('alternative')
        msg['from'] = SMTP_USER
        msg['to'] = RECIPIENT_EMAIL

        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        plain_text = """
            NEW CONTACT FORM SUBMISSION


            Name: {name}
            Email: {email}

            Subject: PORTFOLIO CONTACT

            Message:
            {message}

            ______________
            Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        msg_part = MIMEText(plain_text, 'plain')
        msg.attach(msg_part)

        # Actual Email sending
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True

    except smtplib.SMTPAuthenticationError:
        return False, "Email Authentication failed! Check your Credentials."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, "Error sending email: (str(e))"


if __name__=='__main__':
    app.run(debug=True)