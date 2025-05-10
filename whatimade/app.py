# app.py

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Review, Comment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    reviews = Review.query.order_by(Review.id.desc()).all()
    return render_template('home.html', reviews=reviews)

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    reviews = Review.query.order_by(Review.id.desc()).all()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please log in to post.', 'warning')
            return redirect(url_for('login'))

        if 'new_review' in request.form:
            content = request.form['review_content']
            if content.strip():
                review = Review(content=content, author=current_user)
                db.session.add(review)
                db.session.commit()
                flash('Review posted!', 'success')
            else:
                flash('Review cannot be empty.', 'danger')

        elif 'new_comment' in request.form:
            content = request.form['comment_content']
            review_id = request.form['review_id']
            if content.strip():
                comment = Comment(content=content, user_id=current_user.id, review_id=review_id)
                db.session.add(comment)
                db.session.commit()
                flash('Comment posted!', 'success')
            else:
                flash('Comment cannot be empty.', 'danger')

        return redirect(url_for('demo'))

    return render_template('rome.html', reviews=reviews)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/books')
def books():
    # Logic for books page
    return render_template('book.html')

@app.route('/categories')
def categories():
    # Logic for categories page
    return render_template('cat.html')

@app.route('/contact')
def contact():
    # Logic for contact page
    return render_template('contact.html')

@app.route('/about')
def about():
    # Logic for about page
    return render_template('about.html')

@app.route('/review/<int:review_id>')
def review_detail(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template('review_detail.html', review=review)

@app.route('/new_review', methods=['GET', 'POST'])
@login_required
def ():
    if request.method == 'POST':
        content = request.form['content']
        if content.strip():
            review = Review(content=content, author=current_user)
            db.session.add(review)
            db.session.commit()
            flash('Review posted!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Review cannot be empty.', 'danger')
    return render_template('new_review.html')


if __name__ == "__main__":
    app.run(debug=True)
