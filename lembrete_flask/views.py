from flask import render_template, request, redirect, session, flash, url_for
import data_base as dt
from app import app,db
from helpers import *

@app.route('/')
def index():
    return render_template('index.html',titulo='teste')

@app.route('/login')
def login():
    if not session.get('usuario'):
        return redirect(url_for('lembrete'))
    return render_template('login.html')

@app.post('/login')
def autenticar():
    email=request.form['email']
    if dt.autentica_senha(email,request.form['senha'],db):
        usuario=dt.busca_usuario(db,email)
        session['usuario'] = str(usuario['_id'])
        flash(usuario['Nome'] + ' logado com sucesso!')
        return redirect(url_for('lembrete'))
    else:
        flash('Não foi possivel efetuar o login!')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['usuario'] = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('index'))

@app.route('/cadastro_usuario')
def cadastro_usuario():
    return render_template('cad_usuario.html',titulo='Cadastro')

@app.route('/cadastro_usuario', methods=['POST',])
def cadastro_novo_usuario():
    email = request.form['email']
    nome = request.form['nome']
    senha = request.form['senha']
    if dt.existe_usuario(db,'email', email):
        if dt.cadastrar_usuario(db, email, nome, senha):
            usuario=dt.busca_usuario(db, email)
            session['usuario'] = usuario['_id']
            flash(usuario['Nome'] + ' criado com sucesso!')
        else:
            flash('Não foi possível cadastrar o usuário')
    else:
        flash('Não foi possível cadastrar o usuário')
    return redirect(url_for('cadastro_usuario'))


@app.route('/cadastro_lembrete') 
def Page_cadastro_lembrete():
    return render_template('cad_lembrete.html',titulo='Cadastro de Lembrete')
    
@app.post('/cadastro_lembrete')
def cadastro_lembrete():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    else:
        dt.cadastrar_lembrete(db,session['usuario'],request.form['lembrete'],hora_min(),dia_mes_ano(),request.form['hora'],request.form['dia'],request.form['descricao'])
        return redirect(url_for('lembrete'))
    
@app.route('/lembrete')
def lembrete():
    lembrete=dt.busca_lembrete(db,session['usuario'])
    return render_template('lembrete.html',titulo="Lembretes",lembrete=lembrete)

@app.post('/fechar/<id>')
def fechar(id):
    if dt.finalza_lembrete(db,id):
        flash("Lembrete fechado com sucesso!")
    else:
        flash(f"Não foi possivel finalizar o lembrete: {id}")
    return redirect(url_for('lembrete'))

@app.post('/deletar/<id>')
def deletar(id):
    if dt.deleta_lembrete(db,id):
        flash("Lembrete deletado com sucesso!")
    else:
        flash(f"Não foi possivel deletar o lembrete: {id}")
    return redirect(url_for('lembrete'))

@app.post('/editar/<id>')
def editar(id):
    lembrete=dt.busca_lembrete_id(db,id)
    return render_template('edita_lembrete.html',titulo=f'Edição {id}',lembrete=lembrete)

@app.post('/edicao/<id>')
def edicao(id):
    if dt.edita_lembrete(db,id,request.form['titulo'],hora_min(),dia_mes_ano(),request.form['hora_ativa'],request.form['dia_ativa'],request.form['descricao']):
        flash("Lembrete editado com sucesso com sucesso!")
    else:
        flash("Não foi possivel editar o lembrete!")
    return redirect(url_for('lembrete'))