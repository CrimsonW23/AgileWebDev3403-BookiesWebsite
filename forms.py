from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, DecimalField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from flask import session
from datetime import datetime
import re

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

# Create Bet Form
class CreateBetForm(FlaskForm):
    event_name = StringField("Event Name", validators=[DataRequired()])
    bet_type_description = StringField('Bet Description', validators=[DataRequired()])
    bet_type = SelectField('Definitive Bet Outcome', choices=[('win', 'Win'), ('loss', 'Loss')], validators=[DataRequired()])
    max_stake = DecimalField("Max Stake Amount", validators=[DataRequired(), NumberRange(min=1.0)])
    odds = DecimalField("Odds", validators=[DataRequired(), NumberRange(min=1.0)])
    scheduled_time = DateTimeLocalField("Scheduled Time", format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    duration = IntegerField("Duration (Hours)", validators=[DataRequired(), NumberRange(min=1)])  # Accept only hours
    submit = SubmitField("Create Bet")

    def validate_scheduled_time(form, field):
        if field.data <= datetime.now():
            raise ValidationError("Scheduled time must be in the future.") 

# Place Bet Form
class PlaceBetForm(FlaskForm):
    stake_amount = DecimalField("Stake Amount", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Place Bet")


