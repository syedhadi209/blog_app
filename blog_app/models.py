from blog_app import db, login_manager
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, ForeignKey, Column
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=True)
    admin = db.Column(db.Boolean, default=False, nullable=True)
    posts = db.relationship('Post', backref='user')
    comments = db.relationship('Comment', backref='user')
    likes = db.relationship('Like', backref='user')

    def __repr__(self):
        return f'{self.username} {self.email} {self.password}'


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    attachement = Column(String(1000), nullable=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post')
    likes = db.relationship('Like', backref='post')


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50), nullable=False)
    post_id = db.Column(db.Integer, ForeignKey('post.post_id'))
    user_id = db.Column(Integer, ForeignKey('user.id'))
    replied = db.Column(db.Boolean, default=False)
    replies = db.relationship('Reply', backref='comment')


class Like(db.Model):
    like_id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, ForeignKey('user.id'))
    post_id = Column(db.Integer, ForeignKey('post.post_id'))


class Reply(db.Model):
    reply_id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, ForeignKey('comment.comment_id'))
