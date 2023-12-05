from flask import render_template, redirect, url_for, flash, request, session, Flask, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app import db, app
from app.models import User
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, \
    ResetPasswordForm, EditProfileForm, Enable2faForm, Confirm2faForm, \
    Disable2faForm
from app.email import send_password_reset_email
from datetime import datetime
from app.twilio_verify_api import request_verification_token, \
    check_verification_token, sms, check_verification_code, request_verification_code, CODE
from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect(app)

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Nom d'utilisateur ou mot de passe incorrect")
            return redirect(url_for('login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        if user.two_factor_enabled():
            #request_verification_code(user.verification_phone)
            session['username'] = user.username
            session['phone'] = user.verification_phone
            sms(session['phone'])
            return redirect(url_for(
                'verify_2fa',
                next=next_page,
                remember='1' if form.remember_me.data else '0'
            ))
        login_user(user, remember=form.remember_me.data)
        return redirect(next_page)
    return render_template('login.html',
                           title='Connexion',
                           form=form
                           )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(last_name=form.last_name.data,
                    username=form.username.data,
                    email=form.email.data
                    )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Vous vous êtes inscrit avec succès. Connectez-vous pour continuer.')
        return redirect(url_for('login'))
    return render_template('register.html',
                           title="S'inscrire",
                           form=form
                           )


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            'Consultez votre e-mail pour obtenir les instructions nécessaires à la réinitialisation de votre mot de passe.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Réinitialiser le mot de passe',
                           form=form
                           )

@app.route('/reset_password_request_2/<email>', methods=['POST'])
def reset_password_request_2(email):
    user = User.query.filter_by(email=email).first()

    if user:
        send_password_reset_email(user)
        response = {
            'status': 'success',
            'message': 'Password reset email sent. Please check your email.'
        }
        status_code = 200
    else:
        response = {
            'status': 'error',
            'message': 'User not found for the provided email address.'
        }
        status_code = 404

    return jsonify(response), status_code

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Votre mot de passe a été réinitialisé.')
        return redirect(url_for('connexion'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Vos modifications ont été enregistrées.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                           title='Editer le profil',
                           form=form
                           )


@app.route('/enable_2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    form = Enable2faForm()
    if form.validate_on_submit():
        session['phone'] = form.verification_phone.data
        #request_verification_token(session['phone'])
        sms(session['phone'])
        return redirect(url_for('verify_2fa'))
    return render_template('enable_2fa.html',
                           title="Activer LITA : Ecole d'été 2023",
                           form=form
                           )


@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    form = Confirm2faForm()
    if form.validate_on_submit():
        phone = session['phone']
        if check_verification_code(form.token.data):
            del session['phone']
            if current_user.is_authenticated:
                current_user.verification_phone = phone
                db.session.commit()
                flash("L'authentification à double facteur est maintenant activée")
                return redirect(
                    url_for('user', username=current_user.username)
                )
            else:
                username = session['username']
                del session['username']
                user = User.query.filter_by(username=username).first()
                next_page = request.args.get('next')
                remember = request.args.get('remember', '0') == '1'
                login_user(user, remember=remember)
                return redirect(next_page)
        form.token.errors.append('Token invalide')
    return render_template('verify_2fa.html',
                           form=form,
                           title="Vérifier LITA : Ecole d'été 2023"
                           )


@app.route('/disable_2fa', methods=['GET', 'POST'])
def disable_2fa():
    form = Disable2faForm()
    if form.validate_on_submit():
        current_user.verification_phone = None
        db.session.commit()
        flash("L'authentification à double facteur est maintenant désactivée")
        return redirect(
            url_for('user', username=current_user.username)
        )
    return render_template('disable_2fa.html',
                           form=form,
                           title="Désactiver LITA : Ecole d'été 2023"
                           )
