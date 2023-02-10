from wtforms import Form, StringField, TextAreaField, validators, RadioField, SelectField, widgets
from wtforms.fields import EmailField, FloatField, DateField
from wtforms.validators import Regexp, InputRequired, Length, ValidationError
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField


class Create_General_Feedback(Form):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    no = FloatField('Phone Number', [validators.Length(min=8, max=8), validators.DataRequired()])
    feedback = TextAreaField('Feedback', [validators.DataRequired()])


class Create_Student_Feedback(Form):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', [validators.DataRequired()], choices=[('M', 'Male'), ('F', 'Female')], widget=widgets.TableWidget(with_table_tag=True))
    level = SelectField('Education Level',[validators.DataRequired()], choices=[('P1', 'Primary 1'), ('P2', 'Primary 2'), ('P3', 'Primary 3'),
                                                   ('P4', 'Primary 4'), ('P5', 'Primary 5'), ('P6', 'Primary 6')])
    subject = SelectField('Subjects', [validators.DataRequired()], choices=[('EL', 'English'), ('MA', 'Maths'), ('Science', 'Science')])
    day = SelectField('Lesson Day', [validators.DataRequired()],
                      choices=[('Mon', 'Monday'), ('Tues', 'Tuesday'), ('Wed', 'Wednesday'),
                               ('Thurs', 'Thurday'), ('Fri', 'Friday'), ('Satuday', 'Satuday'), ('Sunday', 'Sunday')],
                      default='Mon')
    timing = SelectField('Lesson Timing', [validators.DataRequired()], choices=[('09 00', '9am - 11am'), ('13 30 - 15 30', '1.30pm - 3.30pm'),
                                                   ('17 00 - 19 00', '5pm - 7pm')])
    tutor = StringField('Tutor', [validators.Length(min=1, max=150), validators.DataRequired()])
    topic = StringField('Topic Conducted today', [validators.Length(min=1, max=150), validators.DataRequired()])
    rating = RadioField("Enjoyability of class (1- Not enjoyable at all, jump off a cliff,   5- Very enjoyable)",
                        choices=[('1', '1'), ('2', '2'),
                                 ('3', '3'), ('4', '4'),
                                 ('5', '5')], widget=widgets.TableWidget(with_table_tag=True))
    feedback = TextAreaField('Feedback', [validators.Optional()])

    def render_subject(self):
        if self.level.data == 'P1':
            subject = SelectField('Subject', [validators.DataRequired()], choices=[('EL', 'English'), ('MA', 'Maths')])
        elif self.level.data == 'P2':
            subject = SelectField('Subject', [validators.DataRequired()], choices=[('EL', 'English'), ('MA', 'Maths')])
        else:
            subject = SelectField('Subject', [validators.DataRequired()], choices=[('EL', 'English'), ('MA', 'Maths'), ('Science', 'Science')])
        return subject



class Ticket(Form):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    no = StringField('Phone Number',
                     [validators.DataRequired(), validators.Length(min=8, max=8), Regexp(regex='[0-9]')])
    enquiry = TextAreaField('Enquiry', [validators.DataRequired()])

    submit = SubmitField('Login')
