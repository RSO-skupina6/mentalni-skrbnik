# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship

# db = SQLAlchemy()

# class CommentModel(db.Model):
#     __tablename__ = 'comments'

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String)
#     content = db.Column(db.String(1000))
#     post_id = db.Column(db.Integer, ForeignKey('posts.id'))

# class PostModel(db.Model):
#     __tablename__ = 'posts'

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String)
#     content = db.Column(db.String(1000))
#     comments = relationship('CommentModel', backref='post', lazy=True)