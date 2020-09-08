import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm, Update_Post)
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from base64 import b64encode, b64decode

@app.route("/")
@app.route("/home" , methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('The account has been created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/portfolio", methods=['GET', 'POST'])
@login_required
def portfolio():
    posts = Post.query.all()
    return render_template('portfolio.html', title='portfolio', posts=posts, post=post)

@app.route("/add_portfolio_work/new", methods=['GET', 'POST'])
@login_required
def new_portfolio_work():
    form = PostForm()
    if form.validate_on_submit():
        image = b64encode(form.picture.data)
        post = Post(title=form.title.data, year=form.year.data, image_file=image,
                     description=form.description.data, author=current_user)
        
        if form.picture.data:
            print("form.picture.data")
        db.session.add(post)
        print("pass")
        db.session.commit()
        flash('Portfolio work has been uploaded!', 'success')
        return redirect(url_for('portfolio'))
    else:
        flash('Something went wrong', 'danger')
    return render_template('add_portfolio_work.html', form=form, title='Add Portfolio Work')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/new/portfolio_work", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, year=form.year.data, picture=form.picture.data,
                     description=form.description.data, author=current_user)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.receipt_file = picture_file
        db.session.add(post)
        db.session.commit()
        flash('Portfolio work has been uploaded!', 'success')
        return redirect(url_for('portfolio'))
    return render_template('portfolio.html', title='New Portfolio Work',
                         form=form, legend='New portfolio work')


@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        image = b64encode(post.receipt_file)
        return render_template('post.html', client_name=post.client_name, post=post, image=image.decode('ascii'))
    except:
        post = Post.query.get_or_404(post_id)
        return render_template('post.html', client_name=post.client_name, post=post)

@app.route("/post/<int:post_id>/upload", methods=['GET', 'POST'])
@login_required
def upload(post_id):
    if request.method == 'POST': 
        post = Post.query.get_or_404(post_id)
        file = request.files['inputFile']
        post.receipt_file=file.read()
        db.session.commit()
        image = b64encode(post.receipt_file)
        flash('Saved ' + file.filename + ' to the database!', 'success')
        return render_template('post.html', client_name=post.client_name, post=post, file=file, image=image.decode('ascii'))
    else:
        return render_template('post.html')


@app.route("/post/<int:post_id>/verify", methods=['GET', 'POST'])
@login_required
def verify(post_id):
    post = Post.query.get_or_404(post_id)
    form = verifyForm()
    if form.validate_on_submit():
        post.verify_or_decline = 'verified'
        db.session.commit()
        flash('Your expense has been verified!', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('verify.html', title='verified',
                            legend='verified', post=post, form=form)

@app.route("/post/<int:post_id>/decline", methods=['GET', 'POST'])
@login_required
def decline(post_id):
    post = Post.query.get_or_404(post_id)
    form = declineForm()
    if form.validate_on_submit():
        post.verify_or_decline = 'declined'
        db.session.commit()
        flash('Your expense has been decline!', 'danger')
        return redirect(url_for('post', post_id=post.id))
    return render_template('decline.html', title='declined',
                            legend='declined', post=post, form=form)



@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id): 
    post = Post.query.get_or_404(post_id)
    form = Update_Post()
    if form.validate_on_submit():
        post.client_project = form.client_project.data
        post.client_or_saggezza = form.client_or_saggezza.data
        post.receipt = form.receipt.data
        post.category = form.category.data
        post.billable_to = form.billable_to.data
        post.payment = form.payment.data
        db.session.commit()
        flash('Expense has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.client_project.data = post.client_project
        form.client_or_saggezza.data = post.client_or_saggezza
        form.receipt.data = post.receipt
        form.category.data = post.category
        form.billable_to.data = post.billable_to
        form.payment.data = post.payment
    return render_template('update_post.html', title='update_post',
                            legend='Update Post', post=post, form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='athanasiou454@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been changed succefully! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)