from flask import Flask, render_template, request, redirect, session, flash, url_for
import time
import datetime
from pymongo import MongoClient
from hashlib import sha256
#import json
from bson import ObjectId

def criptografar(senha):
    hash_senha=sha256(senha.encode())
    return hash_senha.digest()

def cadastrar_usuario(db,email,nome,senha):
    try:
        db.usuario.insert_one(
            {
                'Email':email,
                'Nome':nome,
                'Senha':criptografar(senha)
            }
        )
        return True
    except Exception as e:
        print("**ERRO::", e)
        return False

def cadastrar_lembrete(db,id_usuario,lembrete,hora_criacao,dia_criacao,hora_ativa,dia_ativa,descricao):
    try:
        db.lembrete.insert_one(
            {
                'Id':id_usuario,
                'Lembrete':lembrete,
                'Descricao':descricao,
                'Hora_ativa':hora_ativa,
                'Dia_ativa':dia_ativa,
                'Hora_criacao':hora_criacao,
                'Dia_criacao':dia_criacao,
                'Status':'aberto'
            }
        )
        return True
    except Exception as e:
        print("**ERRO::", e)
        return False

def edita_lembrete(db,id_lembrete,lembrete,hora_edicao,dia_edicao,hora_ativa,dia_ativa,descricao):
    try:
        banco=db['lembrete']
        banco.update_one({'_id':ObjectId(id_lembrete)},
            {'$set':{
                'Lembrete':lembrete,
                'Descricao':descricao,
                'Hora_ativa':hora_ativa,
                'Dia_ativa':dia_ativa,
                'Hora_edicao':hora_edicao,
                'Dia_edicao':dia_edicao,
                }
            }
        )
        return True
    except Exception as e:
        print("**ERRO::", e)
        return False
    
def finalza_lembrete(db,id_lembrete):
    banco=db['lembrete']
    try: 
        banco.update_one({'_id':ObjectId(id_lembrete)}, {'$set':{'Status':'fechado'}})
        return True
    except Exception as e:
        print("**ERRO::", e)
        return False
    
def deleta_lembrete(db,id_lembrete):
    banco=db['lembrete']
    try: 
        banco.delete_one({'_id':ObjectId(id_lembrete)})
        return True
    except Exception as e:
        print("**ERRO::", e)
        return False
    
def busca_lembrete(db,id_usuario):
    banco=db['lembrete']
    resultado=banco.find({"Id":id_usuario})
    return list(resultado)

def busca_lembrete_id(db,id_lembrete):
    banco=db['lembrete']
    resultado=banco.find_one({"_id":ObjectId(id_lembrete)})
    return resultado

def existe_usuario(db,busca,alvo):
    banco=db['usuario']
    resultado=banco.find_one({busca:alvo})
    if resultado:
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
    if resultado:
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
    if not session.get('usuario'):
        return redirect(url_for('lembrete'))
    return render_template('login.html')

@app.post('/login')
def autenticar():
    email=request.form['email']
    if autentica_senha(email,request.form['senha'],db):
        usuario=busca_usuario(db,email)
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
    if existe_usuario(db,'email', email):
        if cadastrar_usuario(db, email, nome, senha):
            usuario=busca_usuario(db, email)
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
        cadastrar_lembrete(db,session['usuario'],request.form['lembrete'],hora_min(),dia_mes_ano(),request.form['hora'],request.form['dia'],request.form['descricao'])
        return redirect(url_for('lembrete'))
    
@app.route('/lembrete')
def lembrete():
    lembrete=busca_lembrete(db,session['usuario'])
    return render_template('lembrete.html',titulo="Lembretes",lembrete=lembrete)

@app.post('/fechar/<id>')
def fechar(id):
    if finalza_lembrete(db,id):
        flash("Lembrete fechado com sucesso!")
    else:
        flash(f"Não foi possivel finalizar o lembrete: {id}")
    return redirect(url_for('lembrete'))

@app.post('/deletar/<id>')
def deletar(id):
    if deleta_lembrete(db,id):
        flash("Lembrete deletado com sucesso!")
    else:
        flash(f"Não foi possivel deletar o lembrete: {id}")
    return redirect(url_for('lembrete'))

@app.post('/editar/<id>')
def editar(id):
    lembrete=busca_lembrete_id(db,id)
    return render_template('edita_lembrete.html',titulo=f'Edição {id}',lembrete=lembrete)

@app.post('/edicao/<id>')
def edicao(id):
    if edita_lembrete(db,id,request.form['titulo'],hora_min(),dia_mes_ano(),request.form['hora_ativa'],request.form['dia_ativa'],request.form['descricao']):
        flash("Lembrete editado com sucesso com sucesso!")
    else:
        flash("Não foi possivel editar o lembrete!")
    return redirect(url_for('lembrete'))

app.run(debug=True)