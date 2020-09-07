from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms.fields.html5 import DateField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    year = SelectField('Select Year of study', choices = [('Year 1', 'Year 1'), ('Year 2', 'Year 2'), ('Year 3', 'Year 3'), ('Year 4', 'Year 4')])                               
    picture = FileField('Upload receipt', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    submit = SubmitField('SAVE PORTFOLIO WORK')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class Update_Post(FlaskForm):
    receipt = SelectField('Receipt', choices = [('Yes-Soft Copy', 'Yes-Soft Copy'), ('Yes-Hard Copy', 'Yes-Hard Copy'), ('No-Receipt', 'No-Receipt')])
    category = SelectField('Category', choices = [('Employee Rewards', 'Employee Rewards'), ('Consumables', 'Consumables'),
                                                 ('General Office Expenses', 'General Office Expenses'), ('General Travel: Accommodation', 'General Travel: Accommodation'), 
                                                 ('General Travel: Travel', 'General Travel: Travel'),('General Travel: Subsistence', 'General Travel: Subsistence'),
                                                 ('Sales Travel: Accommodation', 'Sales Travel: Accommodation'), ('Sales Travel: Travel', 'Sales Travel: Travel'), 
                                                 ('Sales Travel: Subsistence', 'Sales Travel: Subsistence'), ('Sales Entertaining', 'Sales Entertaining'), 
                                                 ('Staff Entertaining', 'Staff Entertaining'), ('Recruitment Fees', 'Recruitment Fees'), ('Visa Immigration', 'Visa Immigration'), 
                                                 ('Software And IT', 'Software And IT'), ('Staff Training', 'Staff Training'), ('Stationary And Office Supplies', 'Stationary And Office Supplies'),
                                                 ('Telephone And Conference', 'Telephone And Conference'), ('Other', 'Other')])
    client_project = StringField('Client Project', validators=[DataRequired()])
    billable_to = SelectField('Billable to client ?', choices = [('Yes', 'Yes'), ('No', 'No')])
    payment = SelectField('Payment Method', choices = [('Own Payment', 'Own Payment'), ('Corporate Card', 'Corporate Card')])
    client_or_saggezza = SelectField('Client or Saggezza:', choices = [('Saggezza UK', 'Saggezza UK'), ('Saggezza US', 'Saggezza US'), ('Client', 'Client')])
    submit = SubmitField('Update Expense')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')