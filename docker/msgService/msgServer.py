#!/usr/bin/python3
import hashlib
import time

from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import requests
import mysql.connector
import os
app = Flask(__name__)
api = Api(app)

secret_uname = os.environ['DB_UNAME']
secret_pass = os.environ['DB_PASS']
secret_database = "messages"
secret_host = os.environ['DB_HOST']


def verify(sender: str, sender_hash: str) -> bool:
    data = {"id": sender, "cookie": sender_hash}
    url = "http://172.17.0.2:5000/verif"
    response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
    if response.status_code == 201:
        return True
    return False

class GetMessages(Resource):
    @staticmethod
    def get(user):
        token = request.headers.get('Authorization')
        if verify(user, token):
            mydb = mysql.connector.connect(
                host=secret_host,
                user=secret_uname,
                password=secret_pass,
                database=secret_database
            )
            cursor = mydb.cursor()
            sql = "SELECT * FROM messages WHERE receiver = %s"
            values = (user,)
            try:
                cursor.execute(sql, values)
                data = cursor.fetchall()
                cursor.close()
                mydb.close()
                return ({'message': 'token matched', 'data': {'messages': [{'sender': message[1],
                                                                           'timestamp':message[3].timestamp(),
                                                                           'message':message[4]} for message in data]}},
                        200)
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                cursor.close()
                mydb.close()
                return {'message': 'Server error'}, 500
        return {'message': 'unauthorized access'}, 403


class SendMessage(Resource):
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('sender', type=str, required=True)
        parser.add_argument('receiver', type=str, required=True)
        parser.add_argument('hash', type=str, required=True)
        parser.add_argument('message', type=str, required=True)
        args = parser.parse_args()
        if verify(args['sender'], args['hash']):
            mydb = mysql.connector.connect(
                host=secret_host,
                user=secret_uname,
                password=secret_pass,
                database=secret_database
            )
            cursor = mydb.cursor()
            sql = "INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)"
            values = (args['sender'], args['receiver'], args['message'])
            try:
                cursor.execute(sql, values)
                mydb.commit()
                cursor.close()
                mydb.close()
                # TODO: notify other party
                return True, 200
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                mydb.rollback()
                cursor.close()
                mydb.close()
                return False, 400
        return False, 401


api.add_resource(SendMessage, '/message')
api.add_resource(GetMessages, '/messages/<string:user>')

if __name__ == '__main__':
    app.run(port=4000)

