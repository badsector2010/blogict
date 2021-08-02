from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms import validators
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Required, ValidationError
from flask_ckeditor import CKEditorField
from blogproject.models import User


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = FileField("Upload Blog Image URL", validators=[FileAllowed(['jpg', 'png', 'gif', 'svg'])])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    img_user = FileField("Profile Image", validators=[FileAllowed(['jpg', 'png', 'gif', 'svg'])])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=7, max=20)])
    confirm_password = PasswordField("Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Let Me In!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

class UpdateProfileForm(FlaskForm):
    job = TextAreaField('Job')
    designation = StringField("Profession")
    bday = StringField("Date of Birth")
    address = StringField("Address")
    zipcode = StringField("Zipcode")
    phone = StringField("Number")
    img_loc = FileField("Upload Blog Image File", validators=[FileAllowed(['jpg', 'png', 'gif', 'svg'])])
    submit = SubmitField("Update Profile!")

class UpdateUserImage(FlaskForm):
    img_user = FileField("Profile Image", validators=[FileAllowed(['jpg', 'png', 'gif', 'svg'])])
    submit = SubmitField("Update Now")

class UpdateUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField("Update User")

    # def validate_email(self, email):
    #     if email.data != current_user.email:
    #         user = User.query.filter_by(email=email).first()
    #         if user:
    #             raise ValidationError('That email is taken. Please choose a different eamil!')

class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Reset")

    # def validate_email(self, email):
    #     if email.data != current_user.email:
    #         user = User.query.filter_by(email=email).first()
    #         if user is None:
    #             raise ValidationError('There is no account with that email. You must register first.!')

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Length(min=7, max=20)])
    confirm_password = PasswordField("Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")
 
class SendCommetnForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField('Message')
    submit = SubmitField("Send message")
