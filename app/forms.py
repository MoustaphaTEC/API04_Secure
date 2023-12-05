from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,\
    TextAreaField
from wtforms.validators import Email, DataRequired, EqualTo, ValidationError,\
    Length
from app.models import User
import phonenumbers


class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember_me = BooleanField('Souvenez-vous de moi')
    submit = SubmitField('Connexion')


class RegistrationForm(FlaskForm):
    first_name = StringField('Prénom', validators=[DataRequired()])
    last_name = StringField('Nom', validators=[DataRequired()])
    username = StringField("Choisir un nom d'utilisateur", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le mot de passe',
                                     validators=[DataRequired(),
                                                 EqualTo('password')
                                                 ]
                                     )
    submit = SubmitField('Inscription')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Veuillez utiliser un autre nom d'utilisateur")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Veuillez utiliser une autre adresse électronique')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Demande de réinitialisation du mot de passe')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(), EqualTo('password')]
                              )
    token = StringField('Token', validators=[DataRequired()])
    submit = SubmitField('Réinitialiser le mot de passe')


class EditProfileForm(FlaskForm):
    username = StringField("Nom d'utilisateu", validators=[DataRequired()])
    about_me = TextAreaField('A propos de moi', validators=[Length(min=0, max=140)])
    submit = SubmitField('Envoyer')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Utilisez un autre nom d'utilisateur.")


class Enable2faForm(FlaskForm):
    verification_phone = StringField('Tél.', validators=[DataRequired()])
    submit = SubmitField("Activer LITA : Ecole d'été 2023")

    def validate_verification_phone(self, verification_phone):
        try:
            p = phonenumbers.parse(verification_phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Numéro de tél. invalide')


class Confirm2faForm(FlaskForm):
    token = StringField('Token')
    submit = SubmitField()


class Disable2faForm(FlaskForm):
    submit = SubmitField("Désactiver LITA : Ecole d'été 2023")
