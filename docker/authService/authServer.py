import hashlib
import time

from flask import Flask
from flask_restful import Api, Resource, reqparse
import mysql.connector
import os
app = Flask(__name__)
api = Api(app)

secret_uname = os.environ['DB_UNAME']
secret_pass = os.environ['DB_PASS']
secret_database = "data"
secret_host = os.environ['DB_HOST']

sessions = dict()


class Authentication(Resource):
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        mydb = mysql.connector.connect(
            host=secret_host,
            user=secret_uname,
            password=secret_pass,
            database=secret_database
        )

        cursor = mydb.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = '{args['username']}'")
        row = cursor.fetchone()
        mydb.disconnect()
        hpwd = hashlib.sha512(args['password'].encode()).hexdigest()
        if hpwd == row[1]:
            cookie = hashlib.sha256((args['username']+args['password']+str(time.time())).encode('utf-8')).hexdigest()
            sessions[args['username']] = cookie
            return cookie, 201
        return "incorrect password", 401


class Logout(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True)
        parser.add_argument('cookie', type=str, required=True)
        args = parser.parse_args()
        if args['id'] in sessions and sessions[args['id']] == args['cookie']:
            del sessions[args['id']]
            return True, 201
        else:
            return False, 401


class Verify(Resource):
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True)
        parser.add_argument('cookie', type=str, required=True)
        args = parser.parse_args()
        return True, 201 if args['id'] in sessions and sessions[args['id']] == args['cookie'] else False, 401


class Register(Resource):
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        mydb = mysql.connector.connect(
            host=secret_host,
            user=secret_uname,
            password=secret_pass,
            database=secret_database
        )
        cursor = mydb.cursor()
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE username = '{args['username']}') AS id_exists;")
        row = cursor.fetchone()
        if row[0] == 1:
            mydb.disconnect()
            return "account with this username already exists", 401
        else:
            hpwd = hashlib.sha512(args['password'].encode()).hexdigest()
            cursor.execute(f"INSERT INTO users (username, password, type) VALUES ('{args['username']}', '{hpwd}', 0);")
            mydb.commit()
        mydb.disconnect()
        return 'Register successful', 201


api.add_resource(Authentication, '/auth')
api.add_resource(Verify, '/verif')
api.add_resource(Logout, '/logout')
api.add_resource(Register, '/register')

if __name__ == '__main__':
    app.run(debug=True)
