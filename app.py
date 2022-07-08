from flask import Flask, render_template, redirect, request, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin import BaseView
from flask_admin.contrib.sqla import ModelView
from hashlib import sha256
from random import randbytes
from flask_migrate import Migrate
from flask_security import UserMixin
import datetime as dt
import os
import re


app = Flask(__name__)
app.secret_key = "str(randbytes(16))"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


ROLE_USER = 0
ROLE_ADMIN = 1
ROLE_MAIN_ADMIN = 2

pattern = re.compile('[0123456789abcdefAB]+')


class MyAdmin(ModelView):

    def is_accessible(self):
        if (role := session.get('role')) and role == 2:
            return True
        return False


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    usersname = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=ROLE_ADMIN)

    def __repr__(self):
        return f'User(username={self.usersname}, password={self.password}, role={self.role})'


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    viewed = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        # return '%r' % self.account_id
        return f'Note(name={self.name}, comment={self.comment}'


@app.route('/')
def main():
    if None in ((username := session.get('usename')), (u_id := session.get('id')), session.get('role', None)):
        return redirect('/login')

    q_notes = Note.query.filter_by(u_id=u_id).all()
    notes = {i.id: {'name': i.name, 'comment': i.comment,
                    'viewed': i.viewed, 'time': i.time} for i in q_notes if q_notes}
    return render_template("main.html", notes=notes, hex=hex)


@app.route('/add', methods=["POST", "GET"])
def page_add():
    if None in ((username := session.get('usename')), (u_id := session.get('id')), session.get('role', None)):
        return redirect('/login')
    msg = ''
    if request.method == "POST":
        name = str(request.form.get('name'))
        time = str(request.form.get('views')) if request.form.get(
            'date/view', False) else (request.form.get('date'))

        if not name:
            msg = 'write the Name'
        elif not time:
            msg = 'write end date or count views notes'
        else:
            type = str(request.form.get('type'))
            comment = str(request.form.get('comment'))
            if type == 'txt':
                note_txt = str(request.form.get('note_txt'))
                new_note = Note(name=name, comment=comment, u_id=int(
                    session['id']), viewed=0, time=time)
                db.session.add(new_note)
                db.session.commit()
                print(new_note.id)
                open(f'static/notes/{hex(new_note.id)}.txt',
                     'w').write(note_txt)
            else:
                new_note = Note(name=name, comment=comment, u_id=int(
                    session['id']), viewed=0, time=time)
                db.session.add(new_note)
                db.session.commit()
                file = request.files['file'] if type == 'file' else request.files['file_img']
                print(request.files)
                file.save(
                    f'static/notes/{hex(new_note.id)}.{file.filename.split(".")[-1]}')
    return render_template('add.html', msg=msg)


@app.route('/note/<id>')
def page_nate(id: str):
    if None in ((username := session.get('usename')), (u_id := session.get('id')), session.get('role', None)):
        return rederect('login')
    q_note = Note.query.filter_by(
        id=int(id, base=16)).first() if pattern.search(id) else False
    dir_files = list(
        filter(lambda x: id in x[:x.rfind('.')], os.listdir('static/notes')))
    if not q_note or len(dir_files) != 0:
        msg = "not such file"
    if "-" not in q_note.time:
        if q_note.viewed >= int(q_note.time):
            msg = 'count viewed is over'
            return render_template('note.html', msg=msg)
    else:
        if dt.datetime.now() > dt.datetime.strptime(q_note.time, '%Y-%m-%d'):
            msg = 'date time is over'
            return render_template('note.html', msg=msg)
    q_note.viewed += 1
    db.session.commit()
    file = dir_files[0]
    type = file[file.rfind('.') + 1:]

    if type.lower() == 'txt':
        data = open("static/notes/" + file, 'r').read()
        return render_template('note.html', msg='', data=data, type=type, name=q_note.name)
    if type.lower() in ('png', 'jpeg', 'jpg', 'svg', 'webp'):
        return render_template('note.html', msg='', data=file, type='img', name=q_note.name)
    return render_template('note.html', msg='', data=file, type='file', name=q_note.name)
    # q_note.viewed += 1
    # if file_s.split('.')[-1].lower() in ('gif', 'jpeg', 'png'):
    #     return " "


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='static/notes', path=filename)


@app.route("/login", methods=['POST', 'GET'])
def login():
    # query = User(usersname="admin", password='d9cc3330ec40a15465b0e9d348a20a3a6270c3788320ed5be734ef2bfda9d4de', role = ROLE_MAIN_ADMIN)
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
admin.add_view(MyAdmin(User, db.session))
admin.add_view(MyAdmin(Note, db.session))


if __name__ == "__main__":
    db.create_all()
    app.run("localhost", port=8080, debug=True)
