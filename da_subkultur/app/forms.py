from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    keyword = StringField('keyword', validators=[DataRequired()])
    submit = SubmitField('Search')