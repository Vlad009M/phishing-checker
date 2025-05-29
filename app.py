from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from models import db, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import docx
import PyPDF2
from ml_model import predict_phishing
from local_ai_analyzer import analyze_with_local_ai
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# --- Налаштування пошти ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'matovkavlad@gmail.com'  # 🔒 Замінити на справжній
app.config['MAIL_PASSWORD'] = 'pqxp lqbo vrce nsfp'    # 🔒 App password
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

# --- SQLAlchemy ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Flask-Login ---
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Головна сторінка ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Реєстрація ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash('Паролі не співпадають')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Користувач з таким email вже існує')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_pw,
            registered_at=datetime.utcnow(),
            account_type='free',
            checks_today=0,
            is_admin=False,
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Підтвердження пошти
        token = s.dumps(email, salt='email-confirm')
        confirm_url = url_for('confirm_email', token=token, _external=True)

        msg = Message("Підтвердження пошти", recipients=[email], sender=app.config['MAIL_USERNAME'])
        msg.body = f"Привіт! Для завершення реєстрації підтвердіть вашу пошту:\n\n{confirm_url}"
        mail.send(msg)

        flash('На вашу пошту надіслано листа для підтвердження.')
        return redirect(url_for('login'))

    return render_template('register.html')

# --- Підтвердження пошти ---
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except Exception:
        flash('Посилання недійсне або протерміноване.')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()
    if user:
        if user.is_verified:
            flash('Пошта вже підтверджена.')
        else:
            user.is_verified = True
            db.session.commit()
            flash('Пошта успішно підтверджена! Тепер увійдіть.')
    return redirect(url_for('login'))

# --- Вхід ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Підтвердіть email перед входом!')
                return redirect(url_for('login'))

            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Невірний email або пароль')
            return redirect(url_for('login'))

    return render_template('login.html')

# --- Профіль ---
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# --- Вихід ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Адмін панель ---
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash("Доступ заборонено")
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

# --- Перевірка тексту ---
@app.route('/predict-text', methods=['POST'])
@login_required
def predict_text():
    if current_user.account_type == 'free' and current_user.checks_today >= 5:
        return jsonify({'error': 'Ваш ліміт вичерпано. Придбайте Premium для необмеженого доступу.'}), 403

    data = request.get_json()
    text = data.get('text', '')
    result = predict_phishing(text)
    current_user.checks_today += 1
    db.session.commit()
    return jsonify({'probability': result})

@app.route('/check-text', methods=['POST'])
@login_required
def check_text():
    if current_user.account_type == 'free' and current_user.checks_today >= 5:
        return jsonify({'error': 'Ваш ліміт вичерпано. Придбайте Premium для необмеженого доступу.'}), 403

    text = request.form.get('text', '')
    probability = predict_phishing(text)
    current_user.checks_today += 1
    db.session.commit()
    return jsonify({'probability': probability})

# --- AI аналіз ---
@app.route('/ai-analysis', methods=['POST'])
@login_required
def ai_analysis():
    if current_user.account_type == 'free' and current_user.checks_today >= 5:
        return jsonify({'error': 'Ваш ліміт вичерпано. Придбайте Premium для необмеженого доступу.'}), 403

    data = request.get_json()
    text = data.get('text', '')
    result = analyze_with_local_ai(text)
    current_user.checks_today += 1
    db.session.commit()
    return jsonify({'ai_opinion': result})

# --- Перевірка файлів ---
@app.route('/check-file', methods=['POST'])
@login_required
def check_file():
    if current_user.account_type == 'free' and current_user.checks_today >= 5:
        return jsonify({'error': 'Ваш ліміт вичерпано. Придбайте Premium для необмеженого доступу.'}), 403

    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'error': 'Файл не завантажено'}), 400

    filename = secure_filename(uploaded_file.filename)
    ext = filename.lower().split('.')[-1]

    text = ""
    try:
        if ext == 'txt':
            text = uploaded_file.read().decode('utf-8', errors='ignore')
        elif ext == 'pdf':
            reader = PyPDF2.PdfReader(uploaded_file)
            text = "\n".join(page.extract_text() or '' for page in reader.pages)
        elif ext == 'docx':
            doc = docx.Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            return jsonify({'error': 'Непідтримуваний формат файлу'}), 400

        result = analyze_with_local_ai(text)
        current_user.checks_today += 1
        db.session.commit()
        return jsonify({'probability': result})

    except Exception as e:
        return jsonify({'error': f'Помилка читання файлу: {str(e)}'}), 500

# --- Ініціалізація БД ---
with app.app_context():
    db.create_all()

# --- Політика безпеки ---
@app.route('/security-policy')
def security_policy():
    return render_template('security_policy.html')


# --- Запуск ---
if __name__ == '__main__':
    app.run(debug=True)
