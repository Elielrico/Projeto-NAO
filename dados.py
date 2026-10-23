# -*- coding: utf-8 -*-
import os
from flask import Blueprint, Flask, render_template, request, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# Cria o Blueprint chamado 'dados_bp'
dados_bp = Blueprint('dados', __name__)

# Extensões de imagem permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy()

# Função responsável por configurar e inicializar o Banco de Dados no app Flask
def init_db(app):
    # Configurações do Banco de Dados mantidas dentro do dados.py
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pacientes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

    # Associa a instância do db com o app
    db.init_app(app)

    # Cria as tabelas se elas ainda não existirem
    with app.app_context():
        db.create_all()

# Função para verificar a extensão do arquivo
def arquivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Modelo do Banco de Dados
class Pessoa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(50), nullable=False)
    ultimo_nome = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    condicao_atendimento = db.Column(db.String(100), nullable=False)
    observacoes = db.Column(db.String(255), nullable=False)
    foto_path = db.Column(db.String(255), nullable=False) # Guarda o nome do arquivo da foto
    tabela_q = db.Column(db.String(255), nullable=True) # Guarda o arquivo da tabela de qualidade

# Rota para exibir o formulário e processar o envio
@dados_bp.route('/formulario', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        primeiro_nome = request.form.get('primeiro_nome')
        ultimo_nome = request.form.get('ultimo_nome')
        idade = request.form.get('idade')
        condicao_atendimento = request.form.get('condicao_atendimento')
        observacoes = request.form.get('observacoes', '')
        
        # Processamento do Upload da Foto
        if 'foto' not in request.files:
            return "Nenhum arquivo enviado", 400
        
        foto = request.files['foto']
        
        if foto and arquivo_permitido(foto.filename):
            # Limpa o nome do arquivo por segurança
            filename = secure_filename(foto.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
             # Garante que a pasta static/uploads existe
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            # Salva o arquivo no disco
            foto.save(os.path.join(upload_folder, filename))
            
            # Cria o registro no banco de dados
            nova_pessoa = Pessoa(
                primeiro_nome=primeiro_nome,
                ultimo_nome=ultimo_nome,
                idade=int(idade),
                condicao_atendimento=condicao_atendimento,
                observacoes=observacoes,
                foto_path=filename,
                tabela_q=None
            )
            
            db.session.add(nova_pessoa)
            db.session.commit()
            
            return redirect('/lista')
            
    return render_template('formulario.html')

# Rota para listar as pessoas cadastradas
@dados_bp.route('/lista')
def listar():
    pessoas = Pessoa.query.all()
    return render_template('lista.html', pessoas=pessoas)