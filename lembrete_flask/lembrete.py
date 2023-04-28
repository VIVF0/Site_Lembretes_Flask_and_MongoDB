from flask import Flask, render_template, request, redirect, session, flash, url_for
import time
import datetime
from pymongo import MongoClient
from hashlib import sha256
import json

def criptografar(senha):
    hash_senha=sha256(senha.encode())
    return hash_senha.digest()

def banco_usuario(db,email,nome,senha):
    try:
        db.usuario.insert_one(
            {
                'Email':email,
                'Nome':nome,
                'Senha':criptografar(senha)
            }
        )
        return True
    except:
        return False

def banco_lembretes(db,id_usuario,lembrete,hora_criacao,dia_criacao,hora_ativa,dia_ativa):
    try:
        db.lembrete.insert_one(
            {
                'Id':id_usuario,
                'Lembrete':lembrete,
                'Hora_ativa':hora_ativa,
                'Dia_ativa':dia_ativa,
                'Hora_criacao':hora_criacao,
                'Dia_criacao':dia_criacao,
                'Status':'aberto'
            }
        )
        return True
    except:
        return False

def fecha_lembrete(db,id_lembrete):
    banco=db['lembrete']
    try: 
        banco.update_one({'_id':id_lembrete},{'Status':'fechado'})
        return True
    except:
        return False
    
def busca_lembrete(db,id_usuario):
    banco=db['lembrete']
    resultado=banco.find({"Id":id_usuario})
    return resultado

def exite_usuario(db,busca,alvo):
    banco=db['usuario']
    resultado=banco.find_one({busca:alvo})
    if resultado==None:
        return True
    else:
        return False

def dia_mes_ano():
    yy=(datetime.datetime.now()).year
    mm=(datetime.datetime.now()).month
    dd=(datetime.datetime.now()).day
    return f'{yy}/{mm}/{dd}'

def hora_min():
    min=time.strftime("%M")
    hora=time.strftime("%H")
    seg=time.strftime("%S")
    return f'{hora}:{min}:{seg}'

def autentica_senha(EmailEntrada,senhaEntrada,db):
    banco=db['usuario']
    resultado=banco.find_one({'Email':EmailEntrada,'Senha':criptografar(senhaEntrada)})
    if resultado!=None:
        return True
    else:
        return False
    
def busca_usuario(db,email):
    banco=db['usuario']
    resultado=banco.find_one({'Email':email})
    return resultado
    

client=MongoClient('localhost',27017)
db=client.lembrete_mongodb

app = Flask(__name__)
app.secret_key = 'lembrete'

@app.route('/')
def index():
    return render_template('index.html',titulo='teste')

@app.route('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def autenticar():
    if autentica_senha(request.form['email'],request.form['senha'],db):
        usuario=busca_usuario(db,request.form['email'])
        session['usuario'] = str(usuario['_id'])
        flash(request.form['email'] + ' logado com sucesso!')
        return redirect(url_for('lembrete'))
    else:
        flash('Usuário não logado.')
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
    if exite_usuario(db,'email', email):
        if banco_usuario(db, email, nome, senha):
            usuario=busca_usuario(db, email)
            session['usuario'] = usuario['_id']
            flash(usuario['Nome'] + ' criado com sucesso!')
        else:
            flash('Não foi possível cadastrar o usuário')
    else:
        flash('Não foi possível cadastrar o usuário')
    return redirect(url_for('cadastro_usuario'))


@app.route('/cadastro_lembrete') 
def cadastro_lembrete():
    return render_template('cad_lembrete.html',titulo='Cadastro de Lembrete')
    
@app.route('/cadastro_lembrete', methods=['POST',])
def cad_lembrete():
    if 'usuario' not in session or session['usuario'] == None:
        return redirect(url_for('login'))
    else:
        banco_lembretes(db,session['usuario'],request.form['lembrete'],hora_min(),dia_mes_ano(),request.form['hora'],request.form['dia'])
        return redirect(url_for('lembrete'))
    
@app.route('/lembrete')
def lembrete():
    lembrete=busca_lembrete(db,session['usuario'])
    return render_template('lembrete.html',titulo="Lembretes",lembrete=lembrete)

@app.route('/fecha_lembrete', methods=['POST',])
def status_lembrete():
    fecha_lembrete(db,request.form['item_id'])
    return redirect(url_for('lembrete'))

app.run(debug=True)