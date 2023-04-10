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
    resultado=banco.find()
    i=0
    for item in resultado:
        lembrete[i]=item
        i+=1
    #print(lembrete)
    i=0
    retorno={}
    for elemento in lembrete.items():
        retorno[i]=elemento
        i+=1
    for y in range(0,2):
        print(retorno[y]['Id'])
        
    #print(retorno[0]['Lembrete'])   

def busca_usuario(db,tabela,busca,alvo):
    banco=db[tabela]
    resultado=banco.find_one({busca:alvo})
    for item in resultado:
        return loads(item)

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
    senha=busca_usuario(db,'usuario','Email',EmailEntrada)
    if senha:
        return senha['Senha']==criptografar(senhaEntrada)
    else:
        return False

client=MongoClient('localhost',27017)
db=client.lembrete_mongodb
#busca_lembrete(db,'6414cc87c1cae14e563f0401')


app = Flask(__name__)
app.secret_key = 'lembrete'

@app.route('/')
def index():
    return render_template('index.html',titulo='teste',imagem=imagem)

@app.route('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def autenticar():
    if autentica_senha(request.form['email'],request.form['senha'],db):
        usuario=busca_usuario(db,'usuario','Email',request.form['email'])
        session['usuario'] = usuario['_id']
        flash(usuario['Nome'] + ' logado com sucesso!')
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

@app.route('/cad_lembrete', methods=['POST',])
def cadastro_novo_usuario():
    try:
        banco_usuario(db,request.form['email'],request.form['nome'],request.form['senha'])
        usuario=busca_usuario(db,'usuario','Email',request.form['email'])
        session['usuario'] = usuario['_id']
        flash(usuario['Nome'] + ' criado com suesso!')
        return redirect((url_for('lembrete')))
    except:
        flash('Não foi possivel cadastrar o usuario')
        return redirect((url_for('cadastro_usuario')))

@app.route('/cadastro_usuario') 
def novo_cadastro():
    return render_template('cad_lembrete.html')
    
@app.route('/cad_lembrete', methods=['POST',])
def cad_lembrete():
    if 'usuario' not in session or session['usuario'] == None:
        return redirect(url_for('login', proxima=url_for('lembrete')))
    else:
        cadastro=banco_lembretes(db,session['usuario'],request.form['lembrete'],hora_min(),dia_mes_ano(),request.form['hora'],request.form['dia'])
    
@app.route('/lembrete')
def lembrete():
    #if 'usuario' not in session or session['usuario'] == None:
    #    return redirect(url_for('login', proxima=url_for('lembrete')))
    usuario=busca_usuario(db,'usuario','Email','vitor')
    #return render_template('lembrete.html',lembrete=busca_lembrete(db,usuario[]), titulo='Lembretes',id_usuario=session['usuario'])
    
app.run(debug=True)