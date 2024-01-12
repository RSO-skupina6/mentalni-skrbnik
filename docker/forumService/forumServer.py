from flask import Flask, request, jsonify
import os
import mysql.connector

app = Flask(__name__)

db_host = os.environ['DB_HOST']
db_username = os.environ['DB_UNAME']
db_password = os.environ['DB_PASS']
db_name = "posts"

try:
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_username,
        password=db_password,
        database=db_name,
        connection_timeout=10
    )
except mysql.connector.Error as err:
    print(f'Access to database failed with: {err}')
    # Handle the error appropriately

cursor = mydb.cursor()

# Create a new post
@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.json
    title = data.get('title')

    if title:
        cursor.execute("INSERT INTO posts (title) VALUES (%s)", (title,))
        mydb.commit()
        return jsonify({'message': 'Post created successfully'}), 201
    else:
        return jsonify({'message': 'Title is required'}), 400


# Delete a post
@app.route('/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    mydb.commit()
    return jsonify({'message': 'Post deleted successfully'}), 200

@app.route('/edit_post/<int:post_id>', methods=['PUT'])
def edit_post(post_id):
    data = request.json
    title = data.get('title')

    cursor.execute("UPDATE posts SET title = %s WHERE id = %s", (title, post_id))
    mydb.commit()
    return jsonify({'message': 'Post edited successfully'}), 200

# Create a new comment on a post
@app.route('/create_comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    data = request.json
    username = data.get('username')
    content = data.get('content')

    cursor.execute("INSERT INTO comments (username, content, post_id) VALUES (%s, %s, %s)", (username, content, post_id))
    mydb.commit()
    return jsonify({'message': 'Comment created successfully'}), 201

# Delete a comment
@app.route('/delete_comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
    mydb.commit()
    return jsonify({'message': 'Comment deleted successfully'}), 200

# Edit a comment
@app.route('/edit_comment/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    data = request.json
    content = data.get('content')

    cursor.execute("UPDATE comments SET content = %s WHERE id = %s", (content, comment_id))
    mydb.commit()
    return jsonify({'message': 'Comment edited successfully'}), 200

# Get all posts
@app.route('/get_all_posts', methods=['GET'])
def get_all_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    post_list = [{'id': post[0], 'title': post[1]} for post in posts]
    return jsonify({'posts': post_list}), 200

# Get all comments of a certain post
@app.route('/get_all_comments/<int:post_id>', methods=['GET'])
def get_all_comments(post_id):
    cursor.execute("SELECT * FROM comments WHERE post_id = %s", (post_id,))
    comments = cursor.fetchall()
    comment_list = [{'id': comment[0], 'username': comment[1], 'content': comment[2]} for comment in comments]
    return jsonify({'comments': comment_list}), 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)