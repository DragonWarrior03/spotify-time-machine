from Spotify import spotify
import os
from flask import Flask, render_template, redirect, url_for, flash,abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField
from wtforms.validators import DataRequired, URL
from functools import wraps
from sqlalchemy import Table, Column, Integer, ForeignKey




os.environ["SECRET_KEY"]="38493290320383843"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL","sqlite:///spotify.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)





##CONFIGURE TABLES

class User(UserMixin,db.Model):
    __tablename__ ="users"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(200),unique=True)
    password=db.Column(db.String(200))
    name=db.Column(db.String(200))
    playlists=relationship("Playlists",back_populates="author")

class Playlists(db.Model):
    __tablename__="playlists"
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Integer)
    month=db.Column(db.Integer)
    year = db.Column(db.Integer)
    url=db.Column(db.String(2000))
    author_id=db.Column(db.Integer,ForeignKey("users.id"))
    author=relationship("User",back_populates="playlists")

db.create_all()

##WTFORM
class LoginForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Let me in")

class PlaylistForm(FlaskForm):
    date=StringField("Date",validators=[DataRequired()])
    month=StringField("Month",validators=[DataRequired()])
    year=StringField("Year",validators=[DataRequired()])
    submit=SubmitField("Lets go!")

class RegisterForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired()])
    name=StringField("Name",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Sign Me Up!")

class NameForm(FlaskForm):
    new_name=StringField("Name",validators=[DataRequired()])
    submit=SubmitField("Update")

class PasswordForm(FlaskForm):
    old_password=StringField("Enter old password",validators=[DataRequired()])
    new_password=StringField("Enter new password",validators=[DataRequired()])
    confirm_password=StringField("Confirm password",validators=[DataRequired()])
    submit=SubmitField("Update")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/',methods=["POST","GET"])
def home():
    login_form=LoginForm()
    play_form = PlaylistForm()
    if login_form.validate_on_submit():
        email=login_form.email.data
        password=login_form.password.data
        user=db.session.query(User).filter_by(email=email).first()
        if not user:
            flash("This email does not exist, please try again")
            return redirect(url_for("register"))
        elif not check_password_hash(user.password,password):
            flash("Password incorrect, please try again")
            return redirect(url_for("home"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    if play_form.validate_on_submit():
        date=str(play_form.date.data)
        month=str(play_form.month.data)
        year=str(play_form.year.data)
        new_playlist=Playlists()
        new_playlist.date=date
        new_playlist.month=month
        new_playlist.year=year
        new_playlist.author=current_user
        d=year+"-"+month+"-"+date
        s=spotify(date=d,year=year)
        s.create_playlist()
        playlist=s.playlist["external_urls"]["spotify"]
        new_playlist.url=playlist
        db.session.add(new_playlist)
        db.session.commit()
        return redirect(url_for('playlist'))


    return render_template('index.html',login_form=login_form,play_form=play_form,logged_in=current_user.is_authenticated)

@app.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            flash("This email does not exist, please try again")
            return redirect(url_for("register"))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again")
            return redirect(url_for("home"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template('login.html',form=form)

@app.route('/register',methods=["POST","GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        email=form.email.data
        user=db.session.query(User).filter_by(email=email).first()
        if user:
            flash("You've already signed up with that email, login instead.")
            return redirect(url_for('register'))

        new_user=User()
        new_user.email=form.email.data
        new_user.password=generate_password_hash(form.password.data,method='pbkdf2:sha256',salt_length=8)
        new_user.name=form.name.data
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html',form=form)

@app.route('/about')
def about():
    return render_template('about.html',logged_in=current_user.is_authenticated)


@app.route('/settings',methods=["POST","GET"])
@login_required
def settings():
    name_form=NameForm(new_name=current_user.name)
    pass_form=PasswordForm()
    if name_form.validate_on_submit():
        current_user.name=name_form.new_name.data
        db.session.commit()
        return redirect(url_for('home'))
    if pass_form.validate_on_submit():
        if not check_password_hash(pass_form.old_password.data,current_user.password):
            flash("Old password is incorrect")
            return redirect(url_for('settings'))
        elif pass_form.new_password.data != pass_form.confirm_password.data:
            flash("Both passwords do no match")
            return redirect(url_for('settings'))
        else:
            current_user.password=generate_password_hash(pass_form.new_password.data,method='pbkdf2:sha256',salt_length=8)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('settings.html',name_form=name_form,pass_form=pass_form,logged_in=current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home',logged_in=current_user.is_authenticated))


@app.route('/playlists')
@login_required
def playlist():
    return render_template('playlist.html',logged_in=current_user.is_authenticated)




if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
