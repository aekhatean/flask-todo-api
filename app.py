from crypt import methods
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token
)

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
import json

load_dotenv()

# App config 
host = os.getenv('APP_HOST')
port = os.getenv('APP_PORT')
app = Flask(__name__)

# Tokens config
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

# DB config
db_dialect = os.getenv('DB_DIALECT')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASS')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')


# App & DB config and combine
DATABASE_URI = f'{db_dialect}://{db_user}:{db_password}@{host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)


# Models
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    desc = db.Column(db.String)
    due = db.Column(db.DateTime)
    status = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Task("{self.title}": "{self.due}")'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
  

# Utils
def dictify(task):
    dict = {}
    dict['id'] = task.id
    dict['title'] = task.title
    dict['desc'] = task.desc
    dict['status'] = task.status
    dict['due'] = task.due

    return dict


def auth(username):
    # Return newly created user's token
    access_token = create_access_token(identity=username)
    return jsonify({
        'status': 'Authenticated',
        'data': {
            'access_token': access_token,
        }
    })


# API Endpoints
@app.route('/', methods=['GET', 'POST'])
@jwt_required()
def todo_list():
    if request.method == 'GET':
        tasks = Task.query.all()
        results = []
        for task in tasks:
            dict = dictify(task)
            results.append(dict)

        return jsonify({
            "tasks": results
        })

    elif request.method == 'POST':
        # Get request data
        track_title = request.json.get('title')
        track_desc = request.json.get('desc')
        track_time = request.json.get('due')
        task_status = request.json.get('status')

        try:
            # Create record in database
            task = Task(title=track_title, desc=track_desc, due=track_time, status=task_status)
            db.session.add(task)
            db.session.commit()

            # Return newly created task
            dict = dictify(task)
            return jsonify(dict), 201
        except:
            return jsonify({
                'msg': "This task already exists"
            })


@app.route("/<int:id>", methods=['GET', 'DELETE', 'PUT'])
@jwt_required()
def todo_task(id):
    task = Task.query.filter_by(id=id).first()
    if request.method == 'GET':
        dict = dictify(task)
        return jsonify({
            'task': dict
        })

    elif request.method == 'DELETE':
        try:
            db.session.delete(task)
            db.session.commit()
            return jsonify({
                'msg': "Task was deleted successfully!"
            })
        except:
            return jsonify({
                'msg': "There is no such record"
            })

    elif request.method == 'PUT':
        data = json.loads(request.data)

        for key, value in data.items():
            setattr(task, key, value)
        db.session.commit()

        # Return newly created task
        dict = dictify(task)
        return jsonify(dict), 201


@app.route("/register", methods=['POST'])
def register():
    # Get request data
    username = request.json.get('username')
    password = request.json.get('password')
    try:
        # Create record in database
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return auth(username)
    except:
        return jsonify({
            'msg': "Couldn't create user"
        })


@app.route("/login", methods=['POST'])
def login():
    # Get request data
    username = request.json.get('username')
    password = request.json.get('password')
    try:
        # find user in database
        user = User.query.filter_by(username=username, password=password).first()
        if (user):
            return auth(username)
        else:
            return jsonify({
                'msg': "Username name or password are wrong, or maybe register first"
            })
    except:
        return jsonify({
            'msg': "Couldn't find user"
        })



db.create_all()
app.run(host=host, port=port, debug=True)