from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from hashlib import sha256
from random import randbytes
from flask_migrate import Migrate
import os


app = Flask(__name__)
app.secret_key = str(randbytes(16))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)



ROLE_USER = 0
ROLE_ADMIN = 1
ROLE_MAIN_ADMIN = 2

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    usersname = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Integer, nullable=False, default = ROLE_ADMIN)

    def __repr__(self):
        return f'User(username={self.usersname}, password={self.password}, role={self.role})'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    viewed = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        # return '%r' % self.account_id
        return f'Note(name={self.name}, comment={self.comment}'


@app.route('/')
def main():
    if None in ((username := session.get('usename')), (u_id :=session.get('id')), session.get('role', None)):
        return redirect('/login')

    q_notes = Note.query.filter_by(u_id=u_id).all()
    notes = {i.id: {'name': i.name, 'comment': i.comment} for i in q_notes if q_notes}
    return render_template("main.html", notes=notes, hex=hex)

@app.route('/add', methods=["POST", "GET"])
def page_add():
    if None in ((username := session.get('usename')), (u_id :=session.get('id')), session.get('role', None)):
        return redirect('/login')
    if request.method == "POST":
        print(str(request.form))

        
    return render_template('add.html')
    


@app.route('/note/<id>')
def page_nate(id: int):
    if  None in ((username := session.get('usename')), (u_id :=session.get('id')), session.get('role', None)):
        return rederect('login')
    files = list(filter(lambda x: id in x, os.listdir('static/notes')))
    if not files:
        return "not such file"
    file_s = files[0]
    q_note = Note.query.filter_by(id=int(id, base=16)).first()
    if not q_note:
        return "not such file"
    # if file_s.split('.')[-1].lower() in ('gif', 'jpeg', 'png'):
    #     return " "

@app.route("/login", methods=['POST', 'GET'])
def login():
    # query = User(usersname="artem", password='d9cc3330ec40a15465b0e9d348a20a3a6270c3788320ed5be734ef2bfda9d4de', role = ROLE_ADMIN)
    # db.session.add(query)
    # db.session.commit()

    msg = ''
    if request.method == "POST":
        user_name = str(request.form.get('username'))
        password = str(request.form.get('password'))

        user = User.query.filter_by(usersname=user_name).first()
        if user and user.password == str(sha256(password.encode()).hexdigest()):
            session['usename'] = user.usersname
            session['id'] = user.id
            session['role'] = user.role
            return redirect("/")
        else:
            msg = "error with username and password"
    return render_template("login.html", msg=msg)



admin = Admin(app)
admin.add_view(ModelView(User, db.session))


if __name__ == "__main__":
    db.create_all()
    app.run("localhost", port=8080, debug=True)
    
