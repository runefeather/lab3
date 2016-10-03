import os, click
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,\
        request,\
        redirect,\
        url_for, abort,\
        render_template,\
        g, \
        flash, \
        jsonify, \
        Response, \
        send_file

import flask_login
from flask_login import LoginManager,\
        login_user,\
        logout_user

app = Flask(__name__, static_url_path='/static', static_folder='static')

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'app.db'),
    SECRET_KEY='development_key', # you need this for login to work
    USERNAME='admin',
    PASSWORD='default'
    ))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
db = SQLAlchemy(app)


#################
# Login Manager
#################
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model):
    """
    For serializing to json
    http://stackoverflow.com/a/7103486
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('name_user', db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(55))
    pillar = db.Column(db.String(10))
    availability = db.Column(db.String(15))

    def __init__(self, name, email, password, pillar, availability):
        self.name = name
        self.email = email
        self.password = password
        self.pillar = pillar
        self.availability = availability

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'name': self.pillar,
            'availability': self.availability
        }

    @property
    def serialize_many2many(self):
        """
        Return object's relations in easily serializeable format.
        NB! Calls many2many's serialize property.
        """
        return [item.serialize for item in self.many2many]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)

    def to_string(self):
        return 'name: %s, pillar: %s, availability: %s' % (self.name, self.pillar, self.availability)
    def __repr__(self):
        return '(User %r %r %r)' % (self.name, self.email, self.password)


#############################
# DATABASE: Using sqlalchemy
#############################
def init_db():
    db.drop_all()
    db.create_all()
    seed_db()
    check_db()


def seed_db():
    u1 = User('user1', 'user1@example.com', 'password1', 'ISTD', 'no')
    u2 = User('user2', 'user2@example.com', 'password2', 'ESD', 'yes')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()


def check_db():
    users = User.query.all()
    print(users)


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.cli.command('seeddb')
def seeddb_command():
    """seeds the database"""
    seed_db()
    print('Seeded.')


@app.cli.command('checkdb')
def checkdb_command():
    """checks db"""
    check_db()
    print('Checked!.')


@app.cli.command('deletedb')
def delete_command():
    db.drop_all()
    print("Deleted!")


@app.route('/')
def index():
    datalist = []
    for user in User.query.all():
        l = []
        l.append(user.name)
        l.append(user.pillar)
        l.append(user.availability)
        datalist.append(l)

    s = {"title": ['Professor', 'Pillar', 'Availability'], "data": datalist}
    return render_template('capstone.html', s=s)


@app.route('/dashboard')
@flask_login.login_required
def dashboard():
    return render_template('dashboard.html', name=flask_login.current_user.name)


# API CALL 1
@app.route('/updatedb', methods=["POST"])
@flask_login.login_required
def update():
    checked = request.form['selector']
    tochange = User.query.filter_by(id=flask_login.current_user.id).first()
    tochange.availability = checked
    db.session.commit()
    return jsonify({"availability": tochange.availability})

#########
# LOGIN
#########

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    http://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works
    1. Checks to see if the username and password match (against your database) - you need to write this code yourself.
    2. If authentication was successful, get the id of the user and pass it to login_user()
    """
    error = None

    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pw']

        user = User.query.filter(User.email == email).first()

        if user is None:
            return render_template('login.html', error=error)
        # TODO: check if username and password match against database
        if pwd == user.password:
            # Login the user
            login_user(user)
            return redirect(url_for('protected'))
        else:
            return abort(400)

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def user_loader(email):
    """
    Loads users from database or in-memory structure.
    Flask-login will try and load a user BEFORE every request
    This in turn calls reload_user conditionally
    """
    user = User.query.filter(User.email == email).first()
    return user

@login_manager.request_loader
def request_loader(request):
    """
    Tell Flask-Login how to load a user from a Flask request and from its session
    """
    email = request.form.get('email')
    user = User.query.filter(User.email == 'email').first()
    if not user:
        return

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == user.password
    return user


@app.route('/protected')
@flask_login.login_required
def protected():
    print('Logged in as: ' + str(flask_login.current_user.email))
    current_user = flask_login.current_user.id
    return render_template('protected.html', u = current_user)


###############
# Registration
###############
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        user = User(request.form['name'], request.form['email'],
                    request.form['pw'], request.form['pillar'], request.form['availability'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return redirect(url_for('index'))

##############
# User Routes
##############
@app.route('/users')
@flask_login.login_required
def users():
    users = User.query.all()
    return jsonify(data = [i.serialize for i in users])

@app.route('/user/<uid>', methods=['GET', 'DELETE'])
@flask_login.login_required
def user(uid):
    if request.method != 'DELETE':
        user = User.query.filter(User.id == uid).first()

        if user:
            plain = request.args.get('text')
            if(plain):
                # content-type text
                return user.to_string()
            # jsonify returns a Response type with application/json content-type.
            return jsonify(data = user.serialize)
        else:
            return abort(404)

    if not uid:
        return jsonify({"error": "Invalid uid"})


    user = User.query.filter(User.id == uid).first()

    if user:
        name = user.name
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": "Deleted " + name})
    else:
        return jsonify({"error": "Invalid uid"})


@app.route('/userinfo/<name>')
@flask_login.login_required
def userinfo(name):
    usertoget = User.query.filter_by(name=name).first()

    if not usertoget:
        return abort(404)

    return jsonify({"name": usertoget.name,
                    "pillar": usertoget.pillar,
                    "availability": usertoget.availability})

###############
# Main
###############
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host='0.0.0.0')
