from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send Message')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    summary = TextAreaField('Summary', validators=[Optional(), Length(max=300)], 
                          description='A brief description of the blog post (optional, max 300 characters)')
    content = TextAreaField('Content', validators=[DataRequired()],
                          description='Use HTML formatting for headings, paragraphs, etc.')
    tags = StringField('Tags', description='Comma-separated tags')
    published = BooleanField('Published', default=True,
                           description='Check to publish immediately, uncheck to save as draft')
    submit = SubmitField('Save Blog Post')

class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    meta_description = TextAreaField('Meta Description', validators=[Optional(), Length(max=160)],
                                 description='Brief description for search engines (max 160 characters)')
    content = TextAreaField('Content', validators=[DataRequired()])
    key_features = TextAreaField('Key Features', validators=[Optional()],
                              description='One feature per line')
    technical_specs = TextAreaField('Technical Specifications', validators=[Optional()],
                                description='Format: Label:Value, one per line')
    tags = StringField('Tags', description='Comma-separated tags')
    published = BooleanField('Published', default=True)
    submit = SubmitField('Save Product')