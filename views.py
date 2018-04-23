from flask import Flask, Response, redirect, url_for, request, session, abort, flash, render_template

from flask_login import LoginManager, UserMixin, \
    login_required, login_user, logout_user, current_user
from models import User, Task

from TaskScheduler import app


@app.route('/')
@login_required
def hello_world():
    return redirect('/tasks')


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user.verify_password(password):
            login_user(user)
            return redirect('/tasks')
        else:
            return abort(401)
    else:
        return render_template('login.html')


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        data = dict(
            username=request.form['username'],
            password=request.form['password'],
            email=request.form['email'],
        )

        User.create_new_user(data)
        # except Exception as e:
        #     print(e)
        #     flash("Bad userdata")
        # else:
        return redirect('/login')
    return render_template('registration.html')


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


@app.route('/tasks/', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        Task.create_task(request.form['data'])
    tasks = User.get_user_tasks_by_id(current_user.id)
    return render_template('task_table.html', tasks=tasks)
