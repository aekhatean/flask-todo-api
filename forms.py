# Unnecessary since it is now an API without front-end

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired, Length


class CreateTaskFrom(FlaskForm):
    task_title = StringField('Task title', validators=[DataRequired(), Length(min=5)])
    task_desc = StringField('Task desc', validators=[DataRequired(), Length(min=10)])
    task_time = DateField('Task time', validators=[DataRequired()])
    task_status = BooleanField('Task status', default=False , validators=[DataRequired()])

    submit = SubmitField('Create')

