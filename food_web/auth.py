from flask import Blueprint, render_template, request, redirect, flash, url_for
from .models import db, Admin
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        admin_name = request.form.get('adminName')
        password = request.form.get('adminPassword')

        if Admin.query.filter_by(admin_name=admin_name).first():
            flash('Admin already exists. Try logging in.', category='error')
            return redirect('/signup')

        new_admin = Admin(admin_name=admin_name)
        new_admin.set_password(password)

        db.session.add(new_admin)
        db.session.commit()
        admins = Admin.query.all()
        print("Admins in DB now:", admins)

        flash('Admin account created successfully!', category='success')
        return redirect('/login')

    return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_name = request.form.get('adminName')
        password = request.form.get('adminPassword')

        admin = Admin.query.filter_by(admin_name=admin_name).first()

        if admin:
            print("Admin found:", admin.admin_name)
            if admin.check_password(password):
                print("Password correct")
                flash('Login successful!', category='success')
                return redirect(url_for('views.dashboard'))
            else:
                print("Password incorrect")
        else:
            print("Admin not found")

        flash('Invalid credentials. Please try again.', category='error')
        return redirect('/login')

    return render_template('login.html')




@auth.route('/logout')
def logout():
    flash('Logged out successfully.', category='info')
    return redirect('/login')
