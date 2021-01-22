from wtforms import Form,FieldList
from wtforms import TextField,FormField
from wtforms.validators import required
from wtforms import PasswordField,StringField,validators,BooleanField,IntegerField, ValidationError, SelectField, FloatField, RadioField


class selectJob(Form):
    job = SelectField('Job',choices=[('Engineer - Mechanical',"Engineer - Mechanical"),('Nurse',"Nurse"),('Welder',"Welder"),('Cook',"Cook"),
                                        ('dress',"Dressmaker / Seamstress")])









