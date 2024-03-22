
import random

from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo,Email,DataRequired

from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime


app = Flask(__name__)

questions = {
       1: {
            'question': 'Ποιος ήταν ο πρώτος άνθρωπος που περπάτησε στη Σελήνη;',
            'options': ['Α) Neil Armstrong', 'Β) Yuri Gagarin', 'Γ) Buzz Aldrin', 'Δ) Michael Collins'],
            'correct_answer': 'Α'
        },
        2: {
            'question': 'Ποια πόλη είναι η πρωτεύουσα της Ιταλίας;',
            'options': ['Α) Βαρκελώνη', 'Β) Παρίσι', 'Γ) Ρώμη', 'Δ) Βιέννη'],
            'correct_answer': 'Γ'
        },
        3: {
            'question': 'Ποιος ζωγράφος δημιούργησε τον πίνακα "Η Μονάλιζα";',
            'options': ['Α) Vincent van Gogh', 'Β) Pablo Picasso', 'Γ) Leonardo da Vinci', 'Δ) Claude Monet'],
            'correct_answer': 'Γ'
        },
        4: {
            'question': 'Ποιος είναι ο μεγαλύτερος ποταμός στον κόσμο;',
            'options': ['Α) Νείλος', 'Β) Άμαζονας', 'Γ) Γάγγης', 'Δ) Μισισιπής'],
            'correct_answer': 'Β'
        },
        5: {
            'question': 'Ποιος συγγραφέας έγραψε το βιβλίο "Ο Άρχοντας των Δαχτυλιδιών";',
            'options': ['Α) J.K. Rowling', 'Β) George R.R. Martin', 'Γ) J.R.R. Tolkien', 'Δ) C.S. Lewis'],
            'correct_answer': 'Γ'
        }
    }


app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
app.config['SECRET_KEY'] = "my super secret key  no one is supposed to know"

# Initialize The Database
db = SQLAlchemy(app)
app.app_context().push() 
# στο shell python from app import app    from app import db    db.create_all

#---------------------------------------------------------------
# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column (db.String(200), nullable=False, unique=True)
    pw = db.Column (db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now)

	

class UserForm(FlaskForm):
    email= StringField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    pw = PasswordField("Password",validators=[DataRequired()])
    #pw2 = PasswordField("Password",validators=[DataRequired() , EqualTo('pw') ])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email= StringField("Email", validators=[DataRequired()])
    pw = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Submit")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    question_text = db.Column(db.String(255), unique=True, nullable=False)
    option_A = db.Column(db.String(100), nullable=False)
    option_B = db.Column(db.String(100), nullable=False)
    option_C = db.Column(db.String(100), nullable=False)
    option_D = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

    def __repr__(self): #represation 
        return f"{self.question_text}: {self.correct_answer}"
#---------------------------------------------------------------
      
score = 0
@app.route('/', methods=['GET','POST'])
def index():
    global score
    if request.method == 'POST':
        form_data = request.form
        v1 =[key for key in form_data.keys()][0]
        v2 =[value for value in form_data.values()][0][0]
        if (v1 == v2):
            score += 1
        elif (v1 != 0):
            score -=1
    x=random.randint(1,len(questions))
    question = questions[x]
    
    return render_template('index.html', question=question, score=score)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        print('ooooooooooooooooooooo')
   
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            
            user = Users( name=form.name.data, email=form.email.data, phone= form.phone.data , pw = form.pw.data)
            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully!")
        form.phone.data = ''
        form.email.data = ''
        form.name.data = ''
        form.pw.data = ''
        name=form.name.data
    
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form=UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == 'POST':
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		try:
			db.session.commit()
			flash ("User updated successfully")
			return render_template("update.html", 
						  form=form,name_to_update=name_to_update,id=id)
		except:
			flash ("Error, try again")
			return render_template("update.html", 
						  form=form,name_to_update=name_to_update,id=id)
	else:
		return render_template("update.html", 
						  form=form,name_to_update=name_to_update, id=id)
     
@app.route('/delete/<int:id>')
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()

	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User Deleted Successfully!!")

		our_users = Users.query.order_by(Users.date_added)
		return render_template("add_user.html", 
		form=form,
		name=name,
		our_users=our_users)

	except:
		flash("There was a problem deleting user, try again...")
		return render_template("add_user.html", 
		form=form, name=name,our_users=our_users)
@app.errorhandler(404)
def page_not_found(e):    
    return render_template('404.html'), 404

#internal server error
@app.errorhandler(500)
def page_not_found(e):    
    return render_template('500.html'), 404





if __name__ == '__main__':
    app.run(debug=True)
    