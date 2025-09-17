import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
import stripe
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from functions.txt_to_pdf import convert_text_to_pdf
from functions.imagem_to_pdf import imagem_para_pdf
from functions.html_to_pdf import html_para_pdf
from modules.pdf_manager import mesclar_pdfs
from modules.pdf_generator import PdfGenerator
from configs.config_manager import carregar_config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    quota = db.Column(db.Integer, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    plan = db.relationship('Plan', backref=db.backref('users', lazy=True))
    quota_left = db.Column(db.Integer, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class Controller(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def not_auth(self):
        return "You are not authorized to view this page."

admin = Admin(app, name='BorgePDF Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(Controller(User, db.session))
admin.add_view(Controller(Plan, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not Plan.query.first():
        free_plan = Plan(name='free', quota=10)
        premium_plan = Plan(name='premium', quota=100)
        db.session.add(free_plan)
        db.session.add(premium_plan)
        db.session.commit()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        free_plan = Plan.query.filter_by(name='free').first()
        user = User(username=form.username.data, email=form.email.data, plan=free_plan, quota_left=free_plan.quota)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/txt-to-pdf-latex', methods=['POST'])
@login_required
def txt_to_pdf_latex_route():
    if current_user.plan.name != 'premium':
        flash('This feature is only available for premium users.')
        return redirect(url_for('index'))

    if current_user.quota_left <= 0:
        flash('You have no quota left. Please upgrade your plan.')
        return redirect(url_for('index'))

    if 'txt_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('txt_files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    config = carregar_config()
    text_blocks = []
    for path in filepaths:
        with open(path, 'r', encoding='utf-8') as f:
            text_blocks.append(f.read())

    if convert_text_to_pdf(text_blocks, output_name, config, process_latex=True):
        current_user.quota_left -= 1
        db.session.commit()
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error converting text to PDF')
        return redirect(url_for('index'))

@app.route('/txt-to-pdf', methods=['POST'])
@login_required
def txt_to_pdf_route():
    if current_user.quota_left <= 0:
        flash('You have no quota left. Please upgrade your plan.')
        return redirect(url_for('index'))

    if 'txt_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('txt_files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    config = carregar_config()
    text_blocks = []
    for path in filepaths:
        with open(path, 'r', encoding='utf-8') as f:
            text_blocks.append(f.read())

    if convert_text_to_pdf(text_blocks, output_name, config):
        current_user.quota_left -= 1
        db.session.commit()
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error converting text to PDF')
        return redirect(url_for('index'))

@app.route('/image-to-pdf', methods=['POST'])
@login_required
def image_to_pdf_route():
    if current_user.quota_left <= 0:
        flash('You have no quota left. Please upgrade your plan.')
        return redirect(url_for('index'))

    if 'image_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('image_files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    if imagem_para_pdf(filepaths, output_name):
        current_user.quota_left -= 1
        db.session.commit()
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error converting images to PDF')
        return redirect(url_for('index'))

@app.route('/html-to-pdf', methods=['POST'])
@login_required
def html_to_pdf_route():
    if current_user.quota_left <= 0:
        flash('You have no quota left. Please upgrade your plan.')
        return redirect(url_for('index'))

    if 'html_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['html_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    if html_para_pdf(filepath, output_name):
        current_user.quota_left -= 1
        db.session.commit()
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error converting HTML to PDF')
        return redirect(url_for('index'))

@app.route('/merge-pdfs', methods=['POST'])
@login_required
def merge_pdfs_route():
    if current_user.quota_left <= 0:
        flash('You have no quota left. Please upgrade your plan.')
        return redirect(url_for('index'))

    if 'pdf_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('pdf_files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    if mesclar_pdfs(filepaths, output_name):
        current_user.quota_left -= 1
        db.session.commit()
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error merging PDFs')
        return redirect(url_for('index'))

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_... '
app.config['STRIPE_SECRET_KEY'] = 'sk_test_... '
app.config['STRIPE_WEBHOOK_SECRET'] = 'whsec_... '
stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/upgrade')
@login_required
def upgrade():
    return render_template('upgrade.html')

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_... ',  # Price ID from your Stripe dashboard
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('index', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('upgrade', _external=True),
            customer=current_user.stripe_customer_id,
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session.get('customer')
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            premium_plan = Plan.query.filter_by(name='premium').first()
            user.plan = premium_plan
            user.quota_left = premium_plan.quota
            db.session.commit()

    return 'Success', 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
