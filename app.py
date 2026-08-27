from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    after_this_request,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from functions.html_to_pdf import html_para_pdf
from functions.imagem_to_pdf import imagem_para_pdf
from functions.txt_to_pdf import convert_text_to_pdf
from modules.pdf_operations import (
    PdfOperationError,
    compress_pdf,
    delete_pages,
    merge_pdfs,
    pdf_info,
    reorder_pages,
    rotate_pdf,
    split_pdf,
)
from configs.config_manager import carregar_config


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
GENERATED_DIR = BASE_DIR / "generated"
UPLOAD_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite'}"
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=50 * 1024 * 1024,
    WTF_CSRF_ENABLED=False,
)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    quota = db.Column(db.Integer, nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"), nullable=False)
    plan = db.relationship("Plan", backref=db.backref("users", lazy=True))
    quota_left = db.Column(db.Integer, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(120))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return bool(self.password_hash and check_password_hash(self.password_hash, password))


class RegistrationForm(FlaskForm):
    username = StringField("Nome", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    password2 = PasswordField(
        "Confirme a senha", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Criar conta")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first() is not None:
            raise ValidationError("Escolha outro nome de usuário.")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first() is not None:
            raise ValidationError("Este email já está cadastrado.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


class ProtectedAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class ProtectedAdminIndex(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))


admin = Admin(app, name="BorgePDF Admin", index_view=ProtectedAdminIndex())
admin.add_view(ProtectedAdminView(User, db))
admin.add_view(ProtectedAdminView(Plan, db))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.context_processor
def inject_product_context():
    return {"product_name": "BorgePDF", "max_upload_mb": 50}


def init_db() -> None:
    with app.app_context():
        db.create_all()
        if not Plan.query.first():
            db.session.add_all([Plan(name="free", quota=10), Plan(name="premium", quota=100)])
            db.session.commit()


def _new_output(filename: str = "borgepdf-result.pdf") -> Path:
    name = secure_filename(filename) or "borgepdf-result.pdf"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return GENERATED_DIR / f"{uuid4().hex[:10]}-{name}"


def _save_upload(file_storage, allowed_extensions: set[str] | None = None) -> Path:
    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise PdfOperationError("Escolha um arquivo válido.")
    extension = Path(filename).suffix.lower().lstrip(".")
    if allowed_extensions and extension not in allowed_extensions:
        raise PdfOperationError("O formato deste arquivo não é aceito para essa operação.")
    destination = UPLOAD_DIR / f"{uuid4().hex[:12]}-{filename}"
    file_storage.save(destination)

    @after_this_request
    def cleanup_upload(response):
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass
        return response

    return destination


def _consume_quota() -> None:
    if not current_user.is_authenticated:
        return
    if current_user.quota_left <= 0:
        raise PdfOperationError("Sua cota terminou. Crie um plano premium para continuar.")
    current_user.quota_left -= 1
    db.session.commit()


def _deliver(path: Path, download_name: str):
    @after_this_request
    def cleanup(response):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return response

    return send_file(path, as_attachment=True, download_name=download_name, max_age=0)


def _handle_error(message: str):
    flash(message, "error")
    return redirect(url_for("index"))


@app.errorhandler(413)
def request_entity_too_large(error):
    flash("O arquivo ultrapassa o limite de 50 MB.", "error")
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        free_plan = Plan.query.filter_by(name="free").first()
        if free_plan is None:
            init_db()
            free_plan = Plan.query.filter_by(name="free").first()
        user = User(
            username=form.username.data,
            email=form.email.data,
            plan=free_plan,
            quota_left=free_plan.quota,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Conta criada. Agora você já pode começar.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Criar conta", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Email ou senha inválidos.", "error")
        else:
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html", title="Entrar", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/txt-to-pdf", methods=["POST"])
def txt_to_pdf_route():
    files = request.files.getlist("txt_files")
    try:
        if not files or not files[0].filename:
            raise PdfOperationError("Adicione ao menos um arquivo TXT.")
        paths = [_save_upload(file, {"txt", "md", "markdown"}) for file in files]
        output = _new_output(request.form.get("output_name", "texto-formatado.pdf"))
        config = carregar_config()
        text_blocks = [path.read_text(encoding="utf-8") for path in paths]
        if not convert_text_to_pdf(text_blocks, str(output), config):
            raise PdfOperationError("Não foi possível converter os arquivos de texto.")
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError, UnicodeDecodeError) as exc:
        return _handle_error(str(exc))


@app.route("/txt-to-pdf-latex", methods=["POST"])
def txt_to_pdf_latex_route():
    files = request.files.getlist("txt_files")
    try:
        if not current_user.is_authenticated or current_user.plan.name != "premium":
            raise PdfOperationError("A conversão com LaTeX está disponível no plano premium.")
        if not files or not files[0].filename:
            raise PdfOperationError("Adicione ao menos um arquivo TXT.")
        paths = [_save_upload(file, {"txt", "md", "markdown"}) for file in files]
        output = _new_output(request.form.get("output_name", "texto-latex.pdf"))
        text_blocks = [path.read_text(encoding="utf-8") for path in paths]
        if not convert_text_to_pdf(text_blocks, str(output), carregar_config(), process_latex=True):
            raise PdfOperationError("Não foi possível converter o arquivo com LaTeX.")
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError, UnicodeDecodeError) as exc:
        return _handle_error(str(exc))


@app.route("/image-to-pdf", methods=["POST"])
def image_to_pdf_route():
    files = request.files.getlist("image_files")
    try:
        if not files or not files[0].filename:
            raise PdfOperationError("Adicione ao menos uma imagem.")
        paths = [_save_upload(file, {"png", "jpg", "jpeg", "webp"}) for file in files]
        output = _new_output(request.form.get("output_name", "imagens.pdf"))
        if not imagem_para_pdf([str(path) for path in paths], str(output)):
            raise PdfOperationError("Não foi possível converter as imagens.")
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError) as exc:
        return _handle_error(str(exc))


@app.route("/html-to-pdf", methods=["POST"])
def html_to_pdf_route():
    try:
        file = request.files.get("html_file")
        if file is None or not file.filename:
            raise PdfOperationError("Adicione um arquivo HTML.")
        source = _save_upload(file, {"html", "htm"})
        output = _new_output(request.form.get("output_name", "pagina.pdf"))
        if not html_para_pdf(str(source), str(output)):
            raise PdfOperationError("Não foi possível converter o HTML.")
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError) as exc:
        return _handle_error(str(exc))


@app.route("/merge-pdfs", methods=["POST"])
def merge_pdfs_route():
    files = request.files.getlist("pdf_files")
    try:
        if not files or not files[0].filename:
            raise PdfOperationError("Adicione ao menos dois PDFs para mesclar.")
        paths = [_save_upload(file, {"pdf"}) for file in files]
        if len(paths) < 2:
            raise PdfOperationError("Adicione ao menos dois PDFs para mesclar.")
        output = _new_output(request.form.get("output_name", "documento-mesclado.pdf"))
        merge_pdfs(paths, output)
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError) as exc:
        return _handle_error(str(exc))


@app.route("/compress-pdf", methods=["POST"])
def compress_pdf_route():
    try:
        file = request.files.get("pdf_file")
        if file is None or not file.filename:
            raise PdfOperationError("Adicione um PDF para comprimir.")
        source = _save_upload(file, {"pdf"})
        output = _new_output(request.form.get("output_name", "pdf-comprimido.pdf"))
        compress_pdf(source, output)
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError) as exc:
        return _handle_error(str(exc))


@app.route("/split-pdf", methods=["POST"])
def split_pdf_route():
    try:
        file = request.files.get("pdf_file")
        if file is None or not file.filename:
            raise PdfOperationError("Adicione um PDF para dividir.")
        source = _save_upload(file, {"pdf"})
        output = _new_output(request.form.get("output_name", "paginas-selecionadas.pdf"))
        split_pdf(source, output, request.form.get("page_spec", "all"))
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError) as exc:
        return _handle_error(str(exc))


@app.route("/rotate-pdf", methods=["POST"])
def rotate_pdf_route():
    try:
        file = request.files.get("pdf_file")
        if file is None or not file.filename:
            raise PdfOperationError("Adicione um PDF para girar.")
        source = _save_upload(file, {"pdf"})
        output = _new_output(request.form.get("output_name", "pdf-rotacionado.pdf"))
        angle = int(request.form.get("angle", "90"))
        rotate_pdf(source, output, angle, request.form.get("page_spec", "all"))
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError, ValueError) as exc:
        return _handle_error(str(exc))


@app.route("/delete-pages", methods=["POST"])
def delete_pages_route():
    try:
        file = request.files.get("pdf_file")
        if file is None or not file.filename:
            raise PdfOperationError("Adicione um PDF para remover páginas.")
        source = _save_upload(file, {"pdf"})
        output = _new_output(request.form.get("output_name", "pdf-sem-paginas.pdf"))
        delete_pages(source, output, request.form.get("page_spec", ""))
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError) as exc:
        return _handle_error(str(exc))


@app.route("/reorder-pages", methods=["POST"])
def reorder_pages_route():
    try:
        file = request.files.get("pdf_file")
        if file is None or not file.filename:
            raise PdfOperationError("Adicione um PDF para reorganizar.")
        source = _save_upload(file, {"pdf"})
        output = _new_output(request.form.get("output_name", "pdf-reorganizado.pdf"))
        reorder_pages(source, output, request.form.get("page_order", ""))
        _consume_quota()
        return _deliver(output, output.name.split("-", 1)[-1])
    except (PdfOperationError, OSError) as exc:
        return _handle_error(str(exc))


@app.route("/pdf-info", methods=["POST"])
def pdf_info_route():
    try:
        file = request.files.get("pdf_file")
        if file is None or not file.filename:
            raise PdfOperationError("Adicione um PDF para consultar as informações.")
        source = _save_upload(file, {"pdf"})
        info = pdf_info(source)
        flash(f"PDF analisado: {info['pages']} página(s), {int(info['size']) / 1024:.1f} KB.", "success")
    except (PdfOperationError, OSError) as exc:
        flash(str(exc), "error")
    return redirect(url_for("index"))


@app.route("/upgrade")
@login_required
def upgrade():
    return render_template("upgrade.html")


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", use_reloader=False)
