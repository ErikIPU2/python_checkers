from flask import Flask, session, request
from flask_restful import Resource, Api
from flask_cors import CORS

from database.Database import Database
import hashlib

app = Flask(__name__)
app.secret_key = "MAZZUTTI"
CORS(app, supports_credentials=True)
api = Api(app)


def hash_string(string):
    sha_signature = hashlib.sha256(string.encode()).hexdigest()
    return sha_signature


def check_existent_username(username):
    users = Database().get_users()
    for user in users:
        if user['username'] == username:
            return True
    return False


def send_invalid_form():
    return {'status': False, 'message': 'Invalid Form'}, 400


def send_not_logged():
    return {'status': False, 'message': 'not logged'}


class Session(Resource):

    def get(self):
        if 'logged_in' in session:
            user = Database().get_user_by_id(session['id'])
            return {'status': True, 'user': user}
        else:
            return send_not_logged()


class Signup(Resource):

    def post(self):
        username = request.form['username']
        password = request.form['password']
        icon = request.form['icon']

        if username and password and icon:
            if not check_existent_username(username):
                password = hash_string(password)
                id = Database().create_user(username, password, icon)
                session['logged_in'] = True
                session['id'] = id
                return {'status': True}
            else:
                return {'status': False, 'message':'user alredy exist'}
        else:
            return send_invalid_form()


class Login(Resource):

    def post(self):
        username = request.form['username']
        password = request.form['password']

        if username and password:
            password = hash_string(password)
            user = Database().get_user(username, password)
            if user:
                session['logged_in'] = True
                session['id'] = user['id']
                return {'status': True}
            else:
                return {'status': False, 'message': "user not find"}
        else:
            return send_invalid_form()


class Logout(Resource):

    def get(self):
        session.pop('logged_in', None)
        session.pop('id', None)
        return {'status': True}



api.add_resource(Session, '/api/session')
api.add_resource(Signup, '/api/session/signup')
api.add_resource(Login, '/api/session/login')
api.add_resource(Logout, '/api/session/logout')

if __name__ == '__main__':
    app.run()
