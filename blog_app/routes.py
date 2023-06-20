from blog_app import app, db
from flask import render_template, session, flash, redirect, url_for
from blog_app.models import User, Post
from blog_app.forms import SignUpForm, LoginForm


@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("An Email has been sent to your email please verify your account!!",
              category="success")
        return redirect(url_for('login'))
    return render_template("signup.html", title='Sign Up', form=form)


@app.route("/login")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data)

    return render_template('login.html', title='Login', form=form)
