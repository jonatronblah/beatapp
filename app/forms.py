from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Email, EqualTo
from app.models import User, Song

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')



class UploadForm(FlaskForm):
    upload = FileField('audiosource', validators=[FileRequired(), FileAllowed(['wav', 'mp3'], 'WAV or MP3 files only')])

    submit = SubmitField('Upload')




class RemixForm(FlaskForm):

    song_source = SelectField(u'Song Source')
    remix_template = SelectField(u'Remix Template')
    dist_value = DecimalField(u'Beat Chance', validators=[InputRequired()], places=4)
    posi = IntegerField(u'Beat Length', validators=[InputRequired()])
    var = DecimalField(u'Smoothing', validators=[InputRequired()], places=1)
    allnote = BooleanField(u'Experimental (Template Ignored)')

    def validate_posi(self, posi):
        if posi.data > 16 or posi.data < 1:
            raise ValidationError('Please choose a value between 1 and 16.')

    def validate_dist_value(self, dist_value):
        if dist_value.data > 1000 or dist_value.data < .0001:
            raise ValidationError('Please choose a value between .0001 and 1000.')

    def validate_var(self, var):
        if var.data > 1 or var.data < 0:
            raise ValidationError('Please choose a value between 0 and 1.')

    submit = SubmitField('Remix!')

    def __init__(self):
        super(RemixForm, self).__init__()
        self.song_source.choices = [(str(s.id), s.filename) for s in Song.query.all()]
        self.remix_template.choices = [(str(s.id), s.filename) for s in Song.query.all()]




