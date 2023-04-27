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
                'Dia_criacao':dia_criacao
            }
        )
        return True
    except:
        return False
    
def busca_lembrete(db,id_usuario):
    banco=db['lembrete']
    lembrete={}
    resultado=banco.find({"Id":id_usuario})
    i=0
    for item in resultado:
        lembrete[i][item.key]=item.value
        i+=1
    return lembrete

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
    resultado=banco.find_one({EmailEntrada:criptografar(senhaEntrada)})
    if resultado!=None:
        return True
    else:
        return False

client=MongoClient('localhost',27017)
db=client.lembrete_mongodb
#busca_lembrete(db,'6414cc87c1cae14e563f0401')


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
        email=request.form['email']
        session['usuario'] = email
        flash(email + ' logado com sucesso!')
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
    try:
        if exite_usuario(db,'email',request.form['email']):
            cadastro=banco_usuario(db,request.form['email'],request.form['nome'],request.form['senha'])
            if cadastro:
                session['usuario'] = request.form['email']
                flash(request.form['email'] + ' criado com suesso!')
                return redirect((url_for('cadastro_usuario')))
            else:
                flash('Não foi possivel cadastrar o usuario')
                return redirect((url_for('cadastro_usuario')))
        else:
            flash('Não foi possivel cadastrar o usuario')
            return redirect((url_for('cadastro_usuario')))
    except:
        flash('Não foi possivel cadastrar o usuario')
        return redirect((url_for('cadastro_usuario')))

@app.route('/cadastro_lembrete') 
def cadastro_lembrete():
    return render_template('cad_lembrete.html',titulo='Cadastro de Lembrete')
    
@app.route('/cadastro_lembrete', methods=['POST',])
def cad_lembrete():
    if 'usuario' not in session or session['usuario'] == None:
        return redirect(url_for('login'))
    else:
        banco_lembretes(db,session['usuario'],request.form['lembrete'],hora_min(),dia_mes_ano(),request.form['hora'],request.form['dia'])
        return redirect((url_for('lembrete')))
    
@app.route('/lembrete')
def lembrete():
    #if 'usuario' not in session or session['usuario'] == None:
    #    return redirect(url_for('login', proxima=url_for('lembrete')))
    usuario=busca_usuario(db,'usuario','Email','vitor')
    #return render_template('lembrete.html',lembrete=busca_lembrete(db,usuario[]), titulo='Lembretes',id_usuario=session['usuario'])
    
app.run(debug=True)