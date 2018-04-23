from hashlib import sha512

import pika
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from TaskScheduler import db, login_manager
from sqlalchemy import text


class User(db.Model, UserMixin):
    __tablename__ = "users"
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True, )
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwd_hash = db.Column(db.String(40))

    def __init__(self, **kwargs):
        super(User, self).__init__()
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        return '<User %r>' % self.username

    def get_id(self):
        return str(self.id)

    @classmethod
    def create_new_user(cls, data):
        db.engine.execute(text("""
            INSERT INTO users (username, email, passwd_hash) VALUES (:username, :email, :passwd_hash)
        """).params(
            username=data['username'],
            email=data['email'],
            passwd_hash=sha512(data['password'].encode('utf-8')).hexdigest(),
        ))

    @classmethod
    def get_user_by_username(cls, username):
        result = db.engine.execute(text("""
            SELECT * FROM users WHERE username = :username
        """).params(username=username))
        return User(**dict(result))

    @staticmethod
    def get_user_tasks_by_id(user_id):
        result = db.engine.execute(text("""
            SELECT * FROM tasks WHERE user_id = :user_id;
        """).params(user_id=user_id)).fetchall()
        return result

    def verify_password(self, password: str):
        if sha512(password.encode('utf-8')).hexdigest() == self.passwd_hash:
            return True
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


parameters = pika.ConnectionParameters()
connection_out = pika.BlockingConnection(parameters)
channel_out = connection_out.channel()
channel_out.exchange_declare('tasks')
channel_out.queue_declare(
    queue="tasks_data",
    durable=True,
    exclusive=False,
    auto_delete=True,
)


class Task(db.Model):
    __tablename__ = "tasks"
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(128))
    # TODO: Add foreign key for Users
    user_id = db.Column(db.Integer)
    status = db.Column(db.String(10))
    result = db.Column(db.String(100))

    @staticmethod
    def create_task(data):
        db.engine.execute(text("""
            INSERT INTO tasks (user_id, status, result, data) VALUES (:user_id, :status, :result, :data);
        """).params(user_id=current_user.id, status="PENDING", result="", data=data))
        task_id = db.engine.execute("""SELECT MAX(id) AS id FROM tasks;""").first().id
        channel_out.queue_bind('tasks_data', 'tasks', 'tasks_data')
        channel_out.basic_publish(
            body=data,
            exchange='tasks',
            routing_key='tasks_data',
            properties=pika.BasicProperties(headers={'task_id': task_id}),
        )
