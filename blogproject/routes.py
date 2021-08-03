from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.util.langhelpers import NoneType
from blogproject import app, db
from functools import wraps
from PIL import Image
from blogproject.models import User, BlogPost, Comment, Profile
from blogproject.forms import (LoginForm, RegisterForm, CreatePostForm, CommentForm, 
                               UpdateProfileForm, UpdateUserImage, UpdateUserForm, 
                               RequestResetForm, ResetPasswordForm, SendCommetnForm)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
import smtplib
import secrets
import os


ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)


login_manager = LoginManager()
login_manager.init_app(app)

#db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

# resize picture
def save_resize_picture(fileName):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(fileName.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (125, 125)
    i = Image.open(fileName)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# save large picture
def save_picture(fileName):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(fileName.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    fileName.save(picture_path)
    return picture_fn

@app.route('/', methods=['GET','POST'])
def main():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.paginate(page=page, per_page=5)
    form = SendCommetnForm()
    # posts = BlogPost.query.all()
    return render_template('index.html',  posts = posts, form = form)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            flash("You've already signed up with that email, log in instead!", "danger")
            return redirect(url_for('register'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        up_profile = Profile(
            designation = "-",
            bday = "-",
            address = "-",
            zipcode = "-",
            phone = "-",
            job = "-",
            user_profile = current_user,
        )
        db.session.add(up_profile)
        db.session.commit()
        flash(f'Account created for {form.name.data}!', 'success')
        return redirect(url_for('main'))

    return render_template('register.html', title = 'Register', form = form, current_user=current_user)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.", 'danger')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', 'danger')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main'))

    return render_template('login.html', title = 'Login', form = form, current_user=current_user)

@app.route('/addblog', methods=['GET','POST'])
@login_required
def addblog():
    form = CreatePostForm()
    if form.validate_on_submit():
        if form.img_url.data:
            picture_file = save_picture(form.img_url.data)
            
            new_blog = BlogPost(
                title = form.title.data,
                subtitle = form.subtitle.data,
                img_url = picture_file,
                author = current_user,
                body = form.body.data,
            )
            db.session.add(new_blog)
            db.session.commit()
            flash('New Blog has been added!', 'success')
            return redirect(url_for('blog'))
        else:
            flash('Sorry something went wrong!', 'danger')

    return render_template('addblog.html', form = form, 
                            title = 'Create Post',
                            legend = 'Create a New Post',
                            current_user=current_user)

@app.route('/updateblog/<int:blog_id>', methods=['GET','POST'])
@login_required
def updateblog(blog_id):
    blog = BlogPost.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    form = CreatePostForm()
    if form.validate_on_submit():
        if form.img_url.data:
            picture_file = save_picture(form.img_url.data)
            blog.img_url = picture_file        
        blog.title = form.title.data
        blog.subtitle = form.subtitle.data
        blog.author = current_user
        blog.body = form.body.data
        db.session.commit()
        flash('New Blog has been added!', 'success')
        return redirect(url_for('blog', blog_id = blog.id))
    elif request.method == 'GET':
        form.title.data = blog.title
        form.subtitle.data = blog.subtitle
        form.body.data = blog.body
        form.img_url.data = blog.img_url

    return render_template('addblog.html', form = form, 
                            title = 'Update Post',
                            legend = 'Update Post',
                            current_user=current_user)

@app.route('/updateaccount', methods=['GET','POST'])
@login_required
def updateaccount():
    img_form = UpdateUserImage()
    user_form = UpdateUserForm()
    # Updating Profile Image
    if img_form.is_submitted():
        if img_form.img_user.data:
            new_profile_pic = save_resize_picture(img_form.img_user.data)
            current_user.img_user = new_profile_pic
            db.session.commit()
            flash('Your Profile picture has been successfully updated.', 'success')
            return redirect(url_for('updateaccount'))   
    # Updating Profile email and name
    if user_form.validate_on_submit():
        user = User.query.filter_by(email=user_form.email.data).first()
        if user:
            flash('Name/email already exist.', 'danger')
            return redirect(url_for('updateaccount'))

        else:
            current_user.name = user_form.name.data
            current_user.email = user_form.email.data
            db.session.commit()
            flash('Name/email successfully updated.', 'success')
            return redirect(url_for('updateaccount'))   
    elif request.method == 'GET':
        user_form.name.data = current_user.name
        user_form.email.data = current_user.email

    form = UpdateProfileForm()
    user_id = current_user.id
    profile_info = Profile.query.get(user_id)
    if form.is_submitted():
        if profile_info.user_id == current_user.id:
            profile_info.designation = form.designation.data
            profile_info.bday = form.bday.data
            profile_info.address = form.address.data
            profile_info.zipcode = form.zipcode.data
            profile_info.phone = form.phone.data
            profile_info.job = form.job.data

            db.session.commit()
            flash('Your Profile has been successfully updated.', 'success')
            return redirect(url_for('updateaccount'))
    elif request.method == 'GET':
        if  profile_info.user_id == current_user.id:
            form.designation.data = profile_info.designation
            form.bday.data = profile_info.bday
            form.address.data = profile_info.address
            form.zipcode.data = profile_info.zipcode
            form.phone.data = profile_info.phone
            form.job.data = profile_info.job  
            def_job = profile_info.designation

    return render_template('updateaccount.html', def_job = def_job,
                                        user_form = user_form, form=form, 
                                        current_user=current_user, img_form = img_form)


@app.route('/showblog/<int:id>', methods=["GET", "POST"])
@login_required
def showblog(id):
    form = CommentForm()
    requested_post = BlogPost.query.get(id)
    blog = BlogPost.query.filter_by(id = id).first()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template('showblog.html', post = requested_post, blog = blog, form = form, current_user = current_user)

@app.route('/deleteblog/<int:blog_id>', methods=['GET','POST'])
@login_required
def deleteblog(blog_id):
    blog = BlogPost.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    db.session.delete(blog)
    db.session.commit()
    flash('Your blog has been deleted!.', 'success')
    return redirect(url_for('main'))

@app.route('/delcomment/<int:comment_id>', methods=['GET','POST'])
@login_required
def delcomment(comment_id):
    comment_data = Comment.query.get_or_404(comment_id)
    if comment_data.comment_author != current_user:
        abort(403)
    db.session.delete(comment_data)
    db.session.commit()
    flash('Your comment has been deleted!.', 'success')
    return redirect(url_for('main'))

@app.route('/profile')
def profile():
    profile_data = Profile.query.filter_by(user_id = current_user.id).first()
    return render_template('profile.html', title='Profile', current_user=current_user, 
                                                profile_data = profile_data)


@app.route('/blog')
@login_required
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.paginate(page=page, per_page=5)
    # posts = BlogPost.query.all()
    return render_template('blog.html', posts = posts, current_user=current_user)

@app.route('/userblog/<int:user_id>')
@login_required
def userblog(user_id):
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(author_id=user_id).paginate(page=page, per_page=5)
    return render_template('blog.html', posts = posts, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

def send_reset_email(msg, user):
    my_email = os.environ.get('MY_EMAIL')
    password = os.environ.get('MY_EMAIL_PASSWORD')

    if user == None:
        user_email = my_email
    else:
        user_email = user.email    

    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
        from_addr=my_email, 
        to_addrs=user_email, 
        msg=f"{msg}"
        )

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = SendCommetnForm()
    user = None
    if form.validate_on_submit():
        msg =f"Subject: {form.name.data} - {form.email.data}  \n\n {form.message.data}."
        send_reset_email(msg, user)
        flash('We received you message, Please give us time respond. Thank you.!.')
    return render_template('contact.html', form = form)
            
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('There is no account with that email. You must register first..')
            return redirect(url_for('reset_request'))
        #create token and message then send
        token = user.get_reset_token()
        msg =f"Subject: Password Reset Email  \n\n To reset your password, visit the following link: \n{url_for('reset_token', token=token, _external=True)} \n\nIf you did not make this request then simply ignore this email and no changes will be made."
        send_reset_email(msg, user)
        flash('An email has been sent with instructions to reset you password!.')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'danger')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        ) 
        user.password=hash_and_salted_password        
        db.session.commit()
        flash('Your password has been updated! ou are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title = 'Reset Password', form = form)
