from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
import requests
import functions as f
from pathlib import Path

app = Flask(__name__)
db_path = Path("/app/var/app-instance/website.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.secret_key = 'your_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = '/'
db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    __tablename__ = 'users'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)

@app.route('/')
def base():
    return redirect(url_for("users"))

@app.route('/handle_form', methods=['POST'])
def handle_form():
    action = request.form.get('action')
    email = request.form.get('email')
    password = request.form.get('password')
    repeat_password = request.form.get('repeat_password')
    name = request.form.get('name')

    if action == 'signup':
        if f.checks(email, password, repeat_password, name) is False:
            return render_template("error_empty.html")

        if f.is_login(email) is None:
            return render_template("error_mail.html")

        if len(password) < 6 and len(password) > 20:
            return render_template("error_pass.html")

        if password != repeat_password:
            return render_template("error_password.html")

        if Users.query.filter(Users.mail == email).first():
            return render_template("error_same_mail.html")

        user = Users(name=name, mail=email, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            return render_template("reg_success.html")
        except:
            return "При регистрации произошла ошибка"

    elif action == 'signin':
        result = Users.query.filter(Users.mail == email, Users.password == password).first()
        if result:
            login_user(result)
            users = Users.query.order_by(Users.id).all()
            return render_template("users.html", users=users)
        else:
            return render_template("error_log.html")

@app.route('/users')
@login_required
def users():
    users = Users.query.order_by(Users.id).all()
    return render_template("users.html", users=users)

@app.route('/money')
@login_required
def money():
    return render_template("money.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("base.html")

@login_manager.unauthorized_handler
def unauthorized_callback():
    return render_template("base.html")

@app.route('/calc', methods=['POST'])
@login_required
def calc():
    try:
        val = float(request.form.get("text"))
    except:
        return render_template("money.html", result="Введите число")

    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

    frm = request.form.get("From")
    to = request.form.get("In")

    first = 1 if request.form.get("From") == "RUB" else data['Valute'][frm]['Value']
    second = 1 if request.form.get("In") == "RUB" else data['Valute'][to]['Value']

    result = round((val * first) / second, 2)
    return render_template("money.html", result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
