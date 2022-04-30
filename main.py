from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
# create database
app.config['SECRET_KEY']='278723f7b4100e0f40f8dc17'
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///auth.db'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
Session(app)

# create models
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(255), nullable=False)
    email=db.Column(db.String(255), unique=True ,nullable=False)
    password=db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User('{self.id}',,'{self.name}','{self.email}')"

# CREATE tables
db.create_all()

# home routes
@app.route('/')
def index():
    # check user is authenticated or not
    if not session.get('user_id'):
        return redirect('/login')
    # check the user_id is in session or not
    if session.get('user_id'):
        id=session["user_id"]
    users=User.query.get(id)
    return render_template('index.html',title='Home Page',users=users)

# signup routes
@app.route('/signup',methods=['POST','GET'])
def signup():
     # check user is authenticated or not
    if session.get('user_id'):
        return redirect('/')
    if request.method=='POST':
        # get the value from the form
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
        # check the value are fill or not
        if name=='' or email=='' or password=='':
            # return flash message
            flash('Please fill the field','danger')
            return redirect('/signup')
        else:
            # check email avilabilty
            is_email=User.query.filter_by(email=email).first()
            # check email
            if is_email:
                 flash('Email already exist','danger')
                 return redirect('/signup')
            else:
                # make a password hash
                hash_password=bcrypt.generate_password_hash(password)
                # create a instance of User class
                data=User(name=name,email=email,password=hash_password)
                # save data in database
                db.session.add(data)
                # commit database
                db.session.commit()
                # send flash message
                flash('Account Create successfully','success')
                return redirect('/login')
    return render_template('signup.html',title='Signup Page')

# login page
@app.route('/login',methods=['POST','GET'])
def login():
    # now authenticate the user
     if session.get('user_id'):
        return redirect('/')
    # check it is post request or not
     if request.method == 'POST':
        # get the value of form 
        email=request.form.get('email')
        password=request.form.get('password')
        # check the field is not empty
        if email=='' and password=='':
            # send flash message
            flash('Please fill the field','danger')
            return redirect('/login')
        else:
            # get user by Email
            users=User.query.filter_by(email=email).first()
            # check the user is exist and password is verify or not
            if users and bcrypt.check_password_hash(users.password,password):
                # store the name and id in session
                session['user_id']=users.id
                session['name']=users.name
                # redirect to home Page
                flash('Login Successfully','success')
                return redirect('/')
            else:
                flash('Invalid Email and Password','danger')
                return redirect('/login')
     else:
         return render_template('login.html',title='Login Page')

# logout users
@app.route('/logout')
def logout():
    # session.pop('user_id',None)
    # session.pop('name',None)
    session['user_id']=None
    session['name']=None
    return redirect('/login')

if __name__ =='__main__':
    app.run(debug=True)

    # 