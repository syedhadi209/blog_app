from blog_app import app, db, mail
from flask import render_template, session, flash, redirect, url_for
from blog_app.models import User, Post
from blog_app.forms import SignUpForm, LoginForm
from blog_app.email import send_email
from flask_mail import Message
from blog_app.token import generate_token, confirm_token
from flask_login import login_user, login_required, current_user



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
        token = generate_token(form.email.data)
        verify_url = url_for('verify_email',token=token, _external=True)
        html = render_template('verify_email.html', confirm_url=verify_url)
        subject = "Please confirm your email"
        send_email(form.email.data,subject, html)
        # login_user(user)
        flash("An Email has been sent to your email please verify your account!!",
              category="success")
        return redirect(url_for('home'))
    return render_template("signup.html", title='Sign Up', form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        password_correct = user.password == form.password.data
        if password_correct:
            login_user(user)
            if current_user.is_authenticated:
                flash("Login Successfull", category="success")
                return redirect('home')
            

    return render_template('login.html', title='Login', form=form)


@app.route("/verify-email/<token>",methods=['GET','POST'])
def verify_email(token):
    try:
        email = confirm_token(token)
    except:
        flash("Link is invalid", category='danger')

    user = User.query.filter_by(email=email).first_or_404()

    if user.verified:
        flash("Account already verified",category='success')
        return redirect(url_for('login'))
    else:
        user.verified = True
        db.session.add(user)
        db.session.commit()
        flash("You account has been confirmed",category='success')
        return redirect(url_for('login'))
