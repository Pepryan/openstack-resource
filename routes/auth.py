from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from routes import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login

    Returns:
        Response: Redirect to index if login successful, otherwise render login page
    """
    if current_user.is_authenticated:
        return redirect(url_for('compute.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form

        user = User.authenticate(username, password)
        if user:
            login_user(user, remember=remember)

            # If remember me is checked, make the session permanent
            if remember:
                # This will use the app's PERMANENT_SESSION_LIFETIME setting
                session.permanent = True

            flash('Successful!')
            return redirect(url_for('compute.index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout

    Returns:
        Response: Redirect to login page
    """
    logout_user()
    return redirect(url_for('auth.login'))
