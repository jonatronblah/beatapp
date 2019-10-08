from flask import render_template, redirect, url_for, request, flash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app, db
from app.forms import LoginForm, RegistrationForm, UploadForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Song
import os


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

    
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.upload.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.instance_path, filename))
        s = Song(filename=filename, user_id=int(current_user.id))
        db.session.add(s)
        db.session.commit()
        r = Song.query.filter_by(user_id=current_user.id)
        
        return ', '.join([i.filename for i in r])
    return render_template('upload.html', title='Upload New Track', form=form)
        




    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))