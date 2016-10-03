from functools import wraps
from flask import request, Response
from flask import Flask, render_template, redirect, url_for, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
db = SQLAlchemy(app)

class user(db.Model):
    name = db.Column('name_user', db.String(80), primary_key=True)
    pillar = db.Column(db.String(10))
    availability = db.Column(db.String(15))

    def __init__(self, name, pillar, availability):
        self.name = name
        self.pillar = pillar
        self.availability = availability

    def __repr__(self):
        return '<user %r>' % self.name

@app.route('/')
def index():
    datalist = []
    for u in user.query.order_by(user.name):
        l = []
        l.append(u.name)
        l.append(u.pillar)
        l.append(u.availability)
        datalist.append(l)
    s={"title": ['Professor', 'Pillar', 'Availability'], "data": datalist}
    return render_template('capstone.html', s=s)

@app.route('/dashboard/<name>')
# auth required
def dashboard(name):
    return render_template('dashboard.html', name=name)

# API CALL 1
@app.route('/updatedb', methods=["POST"])
def update():
    checked=request.form['selector']
    username=request.form['user']
    tochange = user.query.filter_by(name=username).first()
    tochange.availability = checked
    db.session.commit()
    return jsonify({"availability": tochange.availability})

# API CALL 2
@app.route('/userinfo/<name>')
# auth required
def userinfo(name):
    usertoget = user.query.filter_by(name=name).first()
    return jsonify({"name": usertoget.name, "pillar": usertoget.pillar, "availability": usertoget.availability})

if __name__=='__main__':
    user.query.delete()
    db.create_all()
    db.session.commit()
    x = user("Someprof", "ISTD", "No")
    db.session.add(x)
    db.session.commit()

    app.run(debug=True, use_reloader=True, host='0.0.0.0')



