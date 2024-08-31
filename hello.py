import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    disciplina = db.Column(db.String(10))

    def __repr__(self):
        return '<Professor %r>' % self.name


class ProfessorForm(FlaskForm):
    name = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    disciplina = SelectField('Disciplina', choices=[
        ('DSWA5', 'DSWA5'),
        ('GPSA5', 'GPSA5'),
        ('IHCA5', 'IHCA5'),
        ('SODA5', 'SODA5'),
        ('PJIA5', 'PJIA5'),
        ('TCOA5', 'TCOA5')
    ])
    submit = SubmitField('Cadastrar')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Professor=Professor)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastro-professores', methods=['GET', 'POST'])
def cadastro_professores():
    print("Entrou na rota /cadastro-professores")
    form = ProfessorForm()
    if form.validate_on_submit():
        print("Formulário validado com sucesso.")
        professor = Professor.query.filter_by(name=form.name.data).first()
        if professor is None:
            try:
                professor = Professor(name=form.name.data, disciplina=form.disciplina.data)
                db.session.add(professor)
                db.session.commit()
                print(f"Professor '{professor.name}' cadastrado com sucesso.")
                flash(f"Professor '{professor.name}' cadastrado com sucesso!", 'success')
                return redirect(url_for('cadastro_professores'))
            except Exception as e:
                print(f"Erro ao cadastrar professor: {e}")
                db.session.rollback()
                flash("Ocorreu um erro ao cadastrar o professor. Por favor, tente novamente.", 'danger')
        else:
            print(f"Professor '{form.name.data}' já existe no banco de dados.")
            flash(f"Professor '{form.name.data}' já está cadastrado.", 'warning')

    try:
        professores = Professor.query.all()
        print(f"Professores cadastrados: {professores}")
    except Exception as e:
        print(f"Erro ao consultar professores: {e}")
        professores = []

    return render_template('cadastro_professores.html', form=form, professores=professores)
   
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5002)
