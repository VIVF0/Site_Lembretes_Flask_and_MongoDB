from hashlib import sha256
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