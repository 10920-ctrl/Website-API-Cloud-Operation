from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import cast, String
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    search_query = request.args.get('q', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    query = User.query
    if search_query:
        from sqlalchemy import cast, String, or_
        query = query.filter(
            or_(
                User.email.ilike(f"%{search_query}%"),
                User.username.ilike(f"%{search_query}%"),
                User.id.ilike(f"%{search_query}%")
            )
        )
    if sort == 'username':
        query = query.order_by(User.username.asc() if order == 'asc' else User.username.desc())
    elif sort == 'email':
        query = query.order_by(User.email.asc() if order == 'asc' else User.email.desc())
    else:
        query = query.order_by(User.id.asc() if order == 'asc' else User.id.desc())

    users = query.all()
    return render_template("homepage.html", user=current_user, users=users, sort=sort, order=order)

@views.route('/add-user', methods=['POST'])
@login_required
def add_user():
    email = request.form.get('email')
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    if password1 != password2:
        flash('Passwords do not match.', category='error')
        return redirect(url_for('views.home'))
    if email and username:
        new_user = User(email=email, username=username, password=generate_password_hash(password1))
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully! (Password = temp)', category='success')
    else:
        flash('Email and Username are required!', category='error')
    return redirect(url_for('views.home'))

@views.route('/edit-user/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    user_to_edit = User.query.get_or_404(id)
    user_to_edit.email = request.form.get('email')
    user_to_edit.username = request.form.get('username')
    db.session.commit()
    flash('User updated successfully!', category='success')
    return redirect(url_for('views.home'))

@views.route('/delete-user/<int:id>')
@login_required
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User deleted successfully!', category='success')
    return redirect(url_for('views.home'))
