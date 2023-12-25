#!/usr/bin/python3
import hashlib
import time

from flask import Flask, request
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
            sessions[cookie] = args['username']
            return {'message': 'Login Successful', 'token': cookie}, 201
        return {'message': 'invalid credentials'}, 401


class Logout(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True)
        parser.add_argument('cookie', type=str, required=True)
        args = parser.parse_args()
        if args['cookie'] in sessions and sessions[args['cookie']] == args['id']:
            del sessions[args['cookie']]
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
        return (True, 201) if args['cookie'] in sessions and sessions[args['cookie']] == args['id'] else (False, 401)


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
        sql = "SELECT EXISTS(SELECT 1 FROM users WHERE username = %s) AS id_exists;"
        values = (args['username'],)
        cursor.execute(sql, values)
        row = cursor.fetchone()
        if row[0] == 1:
            mydb.disconnect()
            return {'message': 'account with this username already exists'}, 401
        else:
            hpwd = hashlib.sha512(args['password'].encode()).hexdigest()
            sql = "INSERT INTO users (username, password, type) VALUES (%s, %s, 0)"
            values = (args['username'], hpwd)
            cursor.execute(sql, values)
            mydb.commit()
        mydb.disconnect()
        return {'message': 'Register successful'}, 201


class Unregister(Resource):
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
        sql = "DELETE FROM users WHERE username = %s"
        values = (args['username'],)
        try:
            cursor.execute(sql, values)
            mydb.commit()
            cursor.close()
            mydb.close()
            return {'message': 'unregister successful'}, 200
        except mysql.connector.Error as err:
            mydb.rollback()
            cursor.close()
            mydb.close()
            return {'message': 'unregister unsuccessful'}, 400



class UserInfo(Resource):
    @staticmethod
    def get():
        token = request.headers.get('Authorization')
        if token in sessions.keys():
            return {'message': 'token matched', 'data': {'user_identification': sessions[token],
                                                         'more_fields': 'to_come'}}, 200
        else:
            return {'message': 'token mismatched, make sure you are logged in'}, 401


class ListUsers(Resource):
    @staticmethod
    def get():
        token = request.headers.get('Authorization')
        if token in sessions.keys():
            return {'message': 'token matched', 'data': {'active_users': [user for user in sessions.values()]}}, 200
        else:
            return {'message': 'token mismatched, make sure you are logged in'}, 401


api.add_resource(Authentication, '/auth')
api.add_resource(Verify, '/verif')
api.add_resource(Logout, '/logout')
api.add_resource(Register, '/register')
api.add_resource(UserInfo, '/userinfo')
api.add_resource(ListUsers, '/listonlineusers')
api.add_resource(Unregister, '/unregister')

if __name__ == '__main__':
    app.run()
