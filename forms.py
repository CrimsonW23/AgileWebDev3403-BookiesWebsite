from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from flask import session

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
    
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=50)])
    category = SelectField('Category', choices=categories, validators=[DataRequired()])
    post = TextAreaField('Say something:', validators=[DataRequired(), Length(min=1, max=150)])
    submit = SubmitField('Submit')

class ReplyForm(FlaskForm):
    reply = TextAreaField('Add to the conversation:', validators=[DataRequired(), Length(min=1, max=150)])
    submit = SubmitField('Submit')


    