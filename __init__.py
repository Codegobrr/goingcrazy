import shelve
from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from wtforms import Form, StringField, PasswordField, SubmitField, EmailField, SelectField, RadioField, validators, \
    IntegerField, \
    widgets
from wtforms.validators import InputRequired, Length, ValidationError, Email, equal_to
from classes import Create_Student_Feedback, Ticket
from general_feedback import Public, Private

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_name.db'
app.config['SECRET_KEY'] = 'yeet'

basedata = SQLAlchemy(app)
basedata.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(basedata.Model, UserMixin):
    id = basedata.Column(basedata.Integer, primary_key=True)
    email = basedata.Column(basedata.String(20), nullable=False, unique=True)
    password = basedata.Column(basedata.String(80), nullable=False)
    type = basedata.Column(basedata.String(1), nullable=False)

    def get_type(self):
        return self.type


class ClassInfo(basedata.Model):
    id = basedata.Column(basedata.Integer, primary_key=True)
    level = basedata.Column(basedata.String(2))
    subject = basedata.Column(basedata.String(150))
    weekday_price = basedata.Column(basedata.Integer)
    weekend_price = basedata.Column(basedata.Integer)
    duration = basedata.Column(basedata.Integer)
    description = basedata.Column(basedata.String(10000))


class StudentInfo(basedata.Model):
    id = basedata.Column(basedata.Integer, primary_key=True)
    user_id = basedata.Column(basedata.Integer, basedata.ForeignKey('user.id'))
    name = basedata.Column(basedata.String(150))
    parent_name = basedata.Column(basedata.String(150))
    gender = basedata.Column(basedata.String(1))
    parent_relationship = basedata.Column(basedata.String(8))
    level = basedata.Column(basedata.String(3))


class RegisterStudent(Form):
    name = StringField("Student's Name", [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', [validators.DataRequired()],
                        choices=[('M', 'Male'), ('F', 'Female'), ('bruh', 'Rather not say')],
                        widget=widgets.TableWidget(with_table_tag=True))
    level = SelectField('Education Level', choices=[('P1', 'Primary 1'), ('P2', 'Primary 2'), ('P3', 'Primary 3'),
                                                    ('P4', 'Primary 4'), ('P5', 'Primary 5'), ('P6', 'Primary 6')])
    parent_name = StringField("Parent's Name", [validators.Length(min=1, max=150), validators.DataRequired()])
    parent_relationship = SelectField('Relationship to Child', [validators.DataRequired()],
                                      choices=[('M', 'Father'), ('F', 'Mother'), ('Guardian', 'Guardian'),
                                               ('Others', 'Others')])
    email = EmailField(validators=[InputRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    retype = PasswordField(validators=[InputRequired(), Length(min=8, max=20),
                                       equal_to('password', 'Both password fields must be equal!')],
                           render_kw={"placeholder": "Retype Password"})

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError('That email already exists. Please choose a different one.')


class UpdateClass(Form):
    weekday_price = IntegerField("Weekday Price", [validators.Length(min=1, max=150), validators.DataRequired()])
    weekend_price = IntegerField("Weekend Price", [validators.Length(min=1, max=150), validators.DataRequired()])

    description = StringField("Class Description", [validators.Length(min=1, max=150), validators.DataRequired()])
    duration = IntegerField("Duration(mins)", [validators.Length(min=1, max=150), validators.DataRequired()])


class TeacherInfo(basedata.Model):
    id = basedata.Column(basedata.Integer, primary_key=True)
    user_id = basedata.Column(basedata.Integer, basedata.ForeignKey('user.id'))
    first_name = basedata.Column(basedata.String(100))
    last_name = basedata.Column(basedata.String(100))
    gender = basedata.Column(basedata.String(1))
    phone_number = basedata.Column(basedata.String(8))
    educational_level_taught = basedata.Column(basedata.String(3))
    subjects = basedata.Column(basedata.String(1))


class RegisterTeacher(Form):
    first_name = StringField("First Name", [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField("Last Name", [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = RadioField('Gender', [validators.DataRequired()],
                        choices=[('M', 'Male'), ('F', 'Female')],
                        widget=widgets.TableWidget(with_table_tag=True))
    phone_number = StringField("Phone Number", [validators.Length(min=8, max=8), validators.DataRequired()])
    educational_level_taught = SelectField('Educational level taught',
                                           choices=[('P1', 'Primary 1'), ('P2', 'Primary 2'), ('P3', 'Primary 3'),
                                                    ('P4', 'Primary 4'), ('P5', 'Primary 5'), ('P6', 'Primary 6')])
    subjects = RadioField('Subjects taught', [validators.DataRequired()],
                          choices=[('English', 'English'), ('Mathematics', 'Math'), ('Science', 'Science')])

    email = EmailField(validators=[InputRequired(), Email()], render_kw={"placeholder": "Email address"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(validators=[InputRequired(), Length(min=8, max=16),
                                                 equal_to('password', 'Both password fields must be equal!')],
                                     render_kw={"placeholder": "Re-type Password"})

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError('That email already exists. Please choose a different one.')


class LoginForm(Form):
    email = StringField(validators=[InputRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


@app.before_first_request
def create_tables():
    basedata.create_all()

    admin = User.query.filter_by(type='A').first()
    if admin is None:
        teet = bcrypt.generate_password_hash("Thisisapassword2")
        admin = User(email="Admin@gmail.com", password=teet, type="A")
        basedata.session.add(admin)
        basedata.session.commit()

    P1_Eng = ClassInfo.query.filter(and_(ClassInfo.level == 'P1', ClassInfo.subject == 'English')).all()
    if not P1_Eng:
        description = "AftaSkool's Primary 1 English programme is a perfect way to lay down the groundwork to" \
                      " nurture students into appreciating the langauge and become good speakers."
        duration = 90
        weekday = 90
        weekend = 100
        pain = ClassInfo(level='P1', subject='English', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P1_Math = ClassInfo.query.filter(and_(ClassInfo.level == 'P1', ClassInfo.subject == 'Math')).all()
    if not P1_Math:
        description = "Our Primary 1 Math programme aims to teach basic core mathematical " \
                      "concepts to students through fun hands-on experiences."
        duration = 90
        weekday = 115
        weekend = 125
        pain = ClassInfo(level='P1', subject='Math', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P2_Eng = ClassInfo.query.filter(and_(ClassInfo.level == 'P2', ClassInfo.subject == 'English')).all()
    if not P2_Eng:
        description = "Continue to build solid foundations in the English language in areas such as Grammar, Vocabulary and Reading. "
        duration = 90
        weekday = 115
        weekend = 125
        pain = ClassInfo(level='P2', subject='English', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P2_Math = ClassInfo.query.filter(and_(ClassInfo.level == 'P2', ClassInfo.subject == 'Math')).all()
    if not P2_Math:
        description = "AftaSkool's Primary 2 Math programme helps to introduce difficult concepts to students with our tutors' guidance. "
        duration = 90
        weekday = 115
        weekend = 125
        pain = ClassInfo(level='P2', subject='Math', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P3_Eng = ClassInfo.query.filter(and_(ClassInfo.level == 'P3', ClassInfo.subject == 'English')).all()
    if not P3_Eng:
        description = "Students will learn effective oral techniques and vocabulary to " \
                      "express themselves through speaking and writing eloquently."
        duration = 90
        weekday = 125
        weekend = 135
        pain = ClassInfo(level='P3', subject='English', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P3_Math = ClassInfo.query.filter(and_(ClassInfo.level == 'P3', ClassInfo.subject == 'Math')).all()
    if not P3_Math:
        description = "Explore new topics such as angles, graphs, real world problems and reinforce previously learnt mathematical topics."
        duration = 90
        weekday = 125
        weekend = 135
        pain = ClassInfo(level='P3', subject='Math', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P3_Sci = ClassInfo.query.filter(and_(ClassInfo.level == 'P3', ClassInfo.subject == 'Science')).all()
    if not P3_Sci:
        description = "AftaSkool's Primary 3 Science programme introduces students to the wonders of " \
                      "Science, and helps to garner their interest through exciting lessons and topics."
        duration = 90
        weekday = 125
        weekend = 135
        pain = ClassInfo(level='P3', subject='Science', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P4_Eng = ClassInfo.query.filter(and_(ClassInfo.level == 'P4', ClassInfo.subject == 'English')).all()
    if not P4_Eng:
        description = "AftaSkool's Primary 4 English programme helps to ease students into the " \
                      "transition of Upper Primary, with solidifying previous concepts learnt in their lower primary years."
        duration = 90
        weekday = 125
        weekend = 135
        pain = ClassInfo(level='P4', subject='English', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P4_Math = ClassInfo.query.filter(and_(ClassInfo.level == 'P4', ClassInfo.subject == 'Math')).all()
    if not P4_Math:
        description = "Learn exciting new topics and concepts while strengthening students' foundations from lower primary.  "
        duration = 90
        weekday = 125
        weekend = 135
        pain = ClassInfo(level='P4', subject='Math', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P4_Sci = ClassInfo.query.filter(and_(ClassInfo.level == 'P4', ClassInfo.subject == 'Science')).all()
    if not P4_Sci:
        description = "AftaSkool's Primary 4 Science programme continues to develop students' " \
                      "interest in Science, while tackling new concepts and topics.  "
        duration = 90
        weekday = 125
        weekend = 135
        pain = ClassInfo(level='P4', subject='Science', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P5_Eng = ClassInfo.query.filter(and_(ClassInfo.level == 'P5', ClassInfo.subject == 'English')).all()
    if not P5_Eng:
        description = "Start the preparation for PSLE by mastering basic grammar rules and concepts, " \
                      "expanding students' vocabulary and express critical thinking through speaking and writing."
        duration = 90
        weekday = 135
        weekend = 145
        pain = ClassInfo(level='P5', subject='English', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P5_Math = ClassInfo.query.filter(and_(ClassInfo.level == 'P5', ClassInfo.subject == 'Math')).all()
    if not P5_Math:
        description = "Get a headstart for PSLE with AftaSkool's Primary 5 Math programme," \
                      " learning new mathematical concepts such as percentages and ratios. "
        duration = 90
        weekday = 135
        weekend = 145
        pain = ClassInfo(level='P5', subject='Math', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P5_Sci = ClassInfo.query.filter(and_(ClassInfo.level == 'P5', ClassInfo.subject == 'Science')).all()
    if not P5_Sci:
        description = "AftaSkool's Primary 5 Science programme introduces students to PSLE-type questions in tackling both multiple-choice questions (MCQ) and open-ended questions. "
        duration = 90
        weekday = 135
        weekend = 145
        pain = ClassInfo(level='P5', subject='Science', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P6_Eng = ClassInfo.query.filter(and_(ClassInfo.level == 'P6', ClassInfo.subject == 'English')).all()
    if not P6_Eng:
        description = "AftaSkool's Primary 6 English programme helps to prepare students for PSLE with past year exam papers, " \
                      "going through past concepts while strengthening and improving their language skills."
        duration = 90
        weekday = 135
        weekend = 145
        pain = ClassInfo(level='P6', subject='English', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P6_Math = ClassInfo.query.filter(and_(ClassInfo.level == 'P6', ClassInfo.subject == 'Math')).all()
    if not P6_Math:
        description = "AftaSkool's Primary 6 Math tuition class provides students with the necessary resources needed to ace PSLE, " \
                      "with examination revision notes, diligent math practices and exercises."
        duration = 90
        weekday = 135
        weekend = 145
        pain = ClassInfo(level='P6', subject='Math', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()

    P6_Sci = ClassInfo.query.filter(and_(ClassInfo.level == 'P6', ClassInfo.subject == 'Science')).all()
    if not P6_Sci:
        description = "AftaSkool's Primary 6 Science programme prepares students with exam-like assessments" \
                      " and practices to solidify what the concepts and topics they have learnt since Primary 3. "
        duration = 90
        weekday = 135
        weekend = 145
        pain = ClassInfo(level='P6', subject='Science', weekday_price=weekday, weekend_price=weekend, duration=duration,
                         description=description)
        basedata.session.add(pain)
        basedata.session.commit()






@app.route('/')
def test():
    return render_template('test.html')


@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/search_class_info')
def search():




@app.route('/update_class/<id>', methods=['GET', 'POST'])
def update_class_info(id):
    bruh = UpdateClass(request.form)

    if request.method == 'POST' and bruh.validate():
        class_yes = ClassInfo(level=bruh.level.data, subject=bruh.subject.data, weekday_price=bruh.weekday_price.data,
                            weekend_price=bruh.weekend_price.data,
                            description=bruh.description.data, duration=bruh.duration.data)
        basedata.session.add(class_yes)
        basedata.session.commit()
        return redirect(url_for('login'))

    else:
        class_info = ClassInfo.query.filter_by(id=id).first()
        bruh.level.data = class_info.level()
        bruh.subject.data = class_info.subject()
        bruh.weekday_price.data = class_info.weekday_price()
        bruh.weekend_price.data = class_info.weekend_price()



    return render_template('homa_i_want.html', form=bruh)


@app.route('/register_student', methods=['GET', 'POST'])
def register():
    register_student = RegisterStudent(request.form)

    if request.method == 'POST' and register_student.validate():
        hashed_password = bcrypt.generate_password_hash(register_student.password.data)
        new_user = User(email=register_student.email.data, password=hashed_password, type="S")
        basedata.session.add(new_user)
        basedata.session.commit()
        new_student_info = StudentInfo(user_id=new_user.id, name=register_student.name.data,
                                       gender=register_student.gender.data, level=register_student.level.data,
                                       parent_name=register_student.parent_name.data,
                                       parent_relationship=register_student.parent_relationship.data)
        basedata.session.add(new_student_info)
        basedata.session.commit()
        return redirect(url_for('login'))

    return render_template('sign_up_student.html', form=register_student)


@app.route('/register_teacher', methods=['GET', 'POST'])
def registering_teacher():
    register_teacher = RegisterTeacher(request.form)

    if request.method == 'POST' and register_teacher.validate():
        hashed_password = bcrypt.generate_password_hash(register_teacher.password.data)
        new_user = User(email=register_teacher.email.data, password=hashed_password, type="T")
        basedata.session.add(new_user)
        basedata.session.commit()
        new_teacher_info = TeacherInfo(user_id=new_user.id, first_name=register_teacher.first_name.data,
                                       last_name=register_teacher.last_name.data,
                                       gender=register_teacher.gender.data,
                                       educational_level_taught=register_teacher.educational_level_taught.data,
                                       subjects=register_teacher.subjects.data,
                                       phone_number=register_teacher.phone_number.data)
        basedata.session.add(new_teacher_info)
        basedata.session.commit()
        return redirect(url_for('login'))

    return render_template('sign_up_teacher.html', form=register_teacher)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            if user.type == "S":
                return redirect(url_for('dashboard'))
            elif user.type == "T":
                return redirect(url_for('teacher_dashboard'))
            elif user.type == "A":
                return redirect(url_for('admin_dashboard'))

    return render_template('login.html', form=login_form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    lmao = StudentInfo.query.filter_by(user_id=current_user.id).first()
    name = lmao.name

    return render_template('dashboard.html', name=name)


@app.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    teacherinfo = TeacherInfo.query.filter_by(user_id=current_user.id).first()
    first_name = teacherinfo.first_name
    last_name = teacherinfo.last_name

    return render_template('teacher_dashboard.html', first_name=first_name, last_name=last_name)


@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    admin = User.query.filter_by(id=current_user.id).first()
    if admin.type != "A":
        return redirect(url_for('home'))

    return render_template('adminHomepage.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('test'))


@app.route('/ticket', methods=['GET', 'POST'])
def general_feedback():
    ticket = Ticket(request.form)
    if request.method == 'POST' and ticket.validate():
        ticket_dict = {}
        db = shelve.open('ticket.db', 'c')

        try:
            ticket_dict = db['ticket']

        except:
            print("Error in retrieving the ticket from ticket.db.")

        user = Public(ticket.name.data, ticket.email.data, ticket.no.data, ticket.enquiry.data)
        ticket_dict[user.get_id()] = user
        db['ticket'] = ticket_dict

        db.close()

        return redirect(url_for('lmao'))
    return render_template('ticket.html', form=ticket)


@app.route('/student_feedback', methods=['GET', 'POST'])
def student_feedback():
    student = User.query.filter_by(id=current_user.id).first()
    if student.type == "T":
        redirect(url_for("teacher_dashboard"))
    else:
        create_student_feedback = Create_Student_Feedback(request.form)
        if request.method == 'POST' and create_student_feedback.validate():
            student_feedback_dict = {}
            db = shelve.open('student_feedback.db', 'c')

            try:
                student_feedback_dict = db['student_feedback']

            except:
                print("Error in retrieving feedback from student_feedback.db.")

            user = Private(create_student_feedback.name.data, create_student_feedback.gender.data,
                           create_student_feedback.level.data,
                           create_student_feedback.day.data, create_student_feedback.timing.data,
                           create_student_feedback.subject.data, create_student_feedback.tutor.data,
                           create_student_feedback.topic.data,
                           create_student_feedback.rating.data, create_student_feedback.feedback.data)

            student_feedback_dict[user.get_id()] = user
            db['student_feedback'] = student_feedback_dict

            db.close()

            return redirect(url_for('test'))

        else:
            info = StudentInfo.query.filter_by(user_id=current_user.id).first()
            create_student_feedback.name.data = info.name
            create_student_feedback.gender.data = info.gender
            create_student_feedback.level.data = info.level

    return render_template('student_feedback.html', form=create_student_feedback)


@app.route('/retrieve_student_feedback')
def retrieve_students_feedback():
    student_feedback_dict = {}
    db = shelve.open('student_feedback.db', 'r')
    student_feedback_dict = db['student_feedback']
    db.close()

    sfeedback_list = []
    for key in student_feedback_dict:
        user = student_feedback_dict.get(key)
        sfeedback_list.append(user)
    return render_template('retrieve_student_feedback.html', count=len(sfeedback_list), sfeedback_list=sfeedback_list)


@app.route('/delete_student_feedback /<int:id>', methods=['POST'])
def delete_student_feedback(id):
    users_dict = {}
    db = shelve.open('student_feedback.db', 'w')
    users_dict = db['student_feedback']

    users_dict.pop(id)

    db['student_feedback'] = users_dict

    db.close()

    return redirect(url_for('retrieve_student_feedback'))


@app.route('/update_student_feedback/<int:id>/', methods=['GET', 'POST'])
def update_student_feedback(id):
    update_student_feedback = Create_Student_Feedback(request.form)
    if request.method == 'POST' and update_student_feedback.validate():
        student_feedback_dict = {}
        db = shelve.open('student_feedback.db', 'w')
        student_feedback_dict = db['student_feedback']
        user = student_feedback_dict.get(id)
        user.set_name(update_student_feedback.name.data)
        user.set_date(update_student_feedback.date.data)
        user.set_gender(update_student_feedback.gender.data)
        user.set_level(update_student_feedback.level.data)
        user.set_tutor(update_student_feedback.tutor.data)
        user.set_topic(update_student_feedback.topic.data)
        user.set_rating(update_student_feedback.rating.data)
        user.set_feedback(update_student_feedback.feedback.data)
        db['student_feedback'] = student_feedback_dict
        return redirect(url_for('retrieve_students_feedback'))

    else:
        student_feedback_dict = {}
        db = shelve.open('student_feedback.db', 'r')
        student_feedback_dict = db['student_feedback']
        db.close()
        user = student_feedback_dict.get(id)
        update_student_feedback.name.data = user.get_name()
        update_student_feedback.date.data = user.get_date()
        update_student_feedback.gender.data = user.get_gender()
        update_student_feedback.level.data = user.get_level()
        update_student_feedback.tutor.data = user.get_tutor()
        update_student_feedback.topic.data = user.get_topic()
        update_student_feedback.rating.data = user.get_rating()
        update_student_feedback.feedback.data = user.get_feedback()

        return render_template('update_student_feedback.html', form=update_student_feedback)


@app.route('/lmao')
def lmao():
    length = {}
    db = shelve.open('ticket.db', 'r')
    try:
        length = db['ticket']

    except:
        print("Error in retrieving the ticket from ticket.db.")

    hello = len(length)
    db.close()

    return render_template('successthatisnotme.html', value=hello)


if __name__ == '__main__':
    app.run(debug=True)
