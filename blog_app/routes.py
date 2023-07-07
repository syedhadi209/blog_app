from blog_app import app, db, mail
from flask import render_template, session, flash, redirect, url_for, request
from blog_app.models import User, Post, Like, Comment
from blog_app.forms import SignUpForm, LoginForm, NewPost, CommentForm, UpdatePostForm, ReplyForm
from blog_app.email import send_email
from flask_mail import Message
from blog_app.token import generate_token, confirm_token
from flask_login import login_user, login_required, current_user, logout_user
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url



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
                return redirect(url_for('dashboard'))
        else:
            flash("Incorrct Credentials",category='danger')
            return redirect(url_for('login'))
            

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
    

@app.route("/new-post", methods=['GET','POST'])
@login_required
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        if form.attachment.data:
            picture_url = upload(form.attachment.data)['url']
            post = Post(title=form.title.data,content=form.content.data,attachement=picture_url,user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("New Post Created Successfully",category='success')
            return redirect(url_for('dashboard'))
        if not form.attachment.data:
            post = Post(title=form.title.data,content=form.content.data,attachement=None,user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("New Post Created Successfully",category='success')
            return redirect(url_for('dashboard'))

    return render_template("newpost.html",form=form)
    

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form = CommentForm()
    posts = Post.query.all()
    if form.validate_on_submit():
        if request.method == 'POST':
            user_id = current_user.id
            parent_id = request.form.get('post-id')
            parent_type = request.form.get('parent-type')
            comment = Comment(content=form.comment.data,user_id=user_id,parent_id=parent_id,parent_type=parent_type)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('dashboard.html',title=current_user.username,posts=posts, form=form,Comments=Comment,Likes=Like)
                                                                                                 
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/like/<int:parentId>/<int:userId>/<string:parentType>", methods=['GET','POST'])
@login_required
def like(parentId,userId,parentType):
    isLiked = Like.query.filter_by(user_id=userId,parent_id=parentId,parent_type=parentType).first()
    if not isLiked:
        liked = Like(user_id=userId,parent_id=parentId,parent_type=parentType)
        db.session.add(liked)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    if isLiked:
        Like.query.filter_by(user_id=userId,parent_id=parentId,parent_type=parentType).delete()
        db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route("/delete/<int:postId>")
@login_required
def delete_post(postId):
    post = Post.query.get(postId)
    comments = Comment.query.filter_by(parent_id=postId).all()
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    flash("Post Deleted Successfully", category='success')
    return redirect(url_for('dashboard'))


@app.route("/update-post/<int:postId>",methods=['GET','POST'])
@login_required
def update_post(postId):
    form = UpdatePostForm()
    post = Post.query.get_or_404(postId)
    
    
    if form.validate_on_submit():
        if form.attachment.data:
            picture_url = upload(form.attachment.data)['url']
            post.attachement = picture_url
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post Updated Successfully",category='success')
        return redirect(url_for('dashboard'))
    
    form.title.data = post.title
    form.content.data = post.content

    return render_template('update_post.html',title='Update Post', form=form)


@app.route("/reply/<int:parentId>/<string:parentType>",methods=['GET','POST'])
@login_required
def reply(parentId,parentType):
    comment = Comment.query.filter_by(comment_id=parentId).first()
    form = ReplyForm()
    if form.validate_on_submit():
        print(form.reply.data)
        newReply = Comment(user_id=current_user.id, parent_id=parentId,parent_type=parentType,content=form.reply.data)
        db.session.add(newReply)
        db.session.commit()
        flash("Replied Successfully",category="success")
        return redirect(url_for('dashboard'))

    return render_template('reply.html', title='Reply', form=form,comment_content = comment.content)
