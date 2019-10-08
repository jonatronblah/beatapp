from flask import render_template, redirect, url_for, request, flash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app, db
from app.forms import LoginForm, RegistrationForm, UploadForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Song, Beat
import os
import librosa
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from itertools import tee



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

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

nclusters= 8
  
def getbeats(audio):
    y, sr = librosa.load(audio, sr=44100)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, units='samples')
    beatpairs = [i for i in pairwise(beats)]
    flatness_list = []
    rms_list = []
    specbw_list = []
    mfcc_list = []
    start = []
    end = []
    note_list = []
    idx = []
    for e, i in enumerate(beatpairs):
        flatness = librosa.feature.spectral_flatness(y=y[i[0]:i[1]])
        flatness = np.mean(flatness)
        rms = librosa.feature.rms(y=y[i[0]:i[1]])
        rms = np.mean(rms)
        specbw = librosa.feature.spectral_bandwidth(y=y[i[0]:i[1]], sr=sr)
        specbw = np.mean(specbw)
        mfcc = librosa.feature.mfcc(y[i[0]:i[1]], sr=sr)
        mfcc = np.mean(mfcc.flatten())
        chroma = librosa.feature.chroma_stft(y[i[0]:i[1]], sr=sr)
        note = np.max([np.mean(i) for i in chroma])
        flatness_list.append(flatness)
        rms_list.append(rms)
        specbw_list.append(specbw)
        mfcc_list.append(mfcc)
        note_list.append(note)
        start.append(i[0])
        end.append(i[1])
        idx.append(e)
    df = pd.DataFrame()
    df['flatness'] = flatness_list
    df['rms'] = rms_list
    df['specbw'] = specbw_list
    df['mfcc'] = mfcc_list
    df['note'] = note_list
    df['start'] = start
    df['end'] = end
    df['idx'] = idx
    X_scaled = StandardScaler().fit_transform(df.iloc[:,:4])
    ky = KMeans(n_clusters=nclusters).fit_predict(X_scaled)
    df['labels'] = ky
    return df

  
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
        df = getbeats(os.path.join(app.instance_path, filename))
        for row in df.itertuples():
            b = Beat(start=row[5], end=row[6], flatness=row[0], rms=row[1], specbw=row[2], mfcc=row[3], note=row[4], n_group=row[8], idx=row[7], song_id=Song.query.filter_by(user_id=int(current_user.id)).all()[-1].id) 
            db.session.add(b)
        
        
        db.session.commit()
        r = Song.query.filter_by(user_id=current_user.id)
        return ', '.join([i.filename for i in r])
    return render_template('upload.html', title='Upload New Track', form=form)
        


    


    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))