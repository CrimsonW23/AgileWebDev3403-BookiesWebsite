from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    categories = [
            ('General'),
            ('Basketball'),
            ('Rugby League'),
            ('Australian Rules'),
            ('Baseball'),
            ('Golf'),
            ('Other Sport')
    ]

    author = StringField('Name', validators=[DataRequired(), Length(min=1, max=25)])
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=50)])
    category = SelectField('Category', choices=categories, validators=[DataRequired()])
    post = TextAreaField('Say something:', validators=[DataRequired(), Length(min=1, max=150)])
    submit = SubmitField('Submit')

class ReplyForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(min=1, max=25)])
    reply = TextAreaField('Add to the conversation:', validators=[DataRequired(), Length(min=1, max=150)])
    submit = SubmitField('Submit')


    