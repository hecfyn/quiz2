
import random

from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo,Email,DataRequired
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'





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
    score = db.Column (db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)

	
class QuestionForm(FlaskForm):
    question_text= StringField("Email")
    ans1 = StringField("Name")
    ans2 = StringField("Phone")
    ans3 = PasswordField("Password")
    ans4 = PasswordField("Password")
    submit = SubmitField("Submit")



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

  
#---------------------------------------------------------------

@app.route('/play/<int:id>', methods=['GET','POST'])
def play(id):
    user = Users.query.get_or_404(id)
    
    form = QuestionForm()
    questions = Question.query.all()

    while(True):
        
        if request.method == 'POST': 
            question = questions[random.randint(0, len(questions)-1)]
            print(request.form)
            print(request.form.getlist('answer')[0])


            if request.form.getlist('answer')[1] == request.form.getlist('answer')[0]:
                user.score += 1
            elif user.score- 1 >=0 :
                user.score -= 1
        else:
            
            question = questions[random.randint(0, len(questions)-1)]
            
        return render_template('index.html', question=question, score=user.score, correct = question.correct_answer)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            
            user = Users( name=form.name.data, phone= form.phone.data ,email=form.email.data,score=0,  pw = form.pw.data)
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
     
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.method == 'POST':
        user = Users.query.filter_by(email=form.email.data).first()
        print(user)
        email = request.form['email']
        pw = request.form['pw']
        if email ==  user.email and pw == user.pw:
            return redirect(url_for('play', id=user.id))        
        else:
            flash("Loggin unsuccessful, try again")

   
    return render_template('login.html', form=form)
        

@app.errorhandler(404)
def page_not_found(e):    
    return render_template('404.html'), 404

#internal server error
@app.errorhandler(500)
def page_not_found(e):    
    return render_template('500.html'), 404





if __name__ == '__main__':
    app.run(debug=True)
    