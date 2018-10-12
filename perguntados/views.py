from flask import g, session, request, redirect, url_for, render_template
import psycopg2, psycopg2.extras

from random import randint,shuffle
import datetime

from perguntados import app
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
from base64 import b64encode, b64decode

global partidas
partidas = []


@app.before_request
def before_request():
   g.db = psycopg2.connect(host='localhost', database='publicbase',user='postgres', password='klinsman')

# Disconnect database
@app.teardown_request
def teardown_request(exception):
    g.db.close()

def encrypt(msm, publickey):
	cipher = PKCS1_OAEP.new(publickey)
	return cipher.encrypt(msm)

def decrypt(msm, privatekey):
	cipher = PKCS1_OAEP.new(privatekey)
	return cipher.decrypt(msm)

def read_database(term, table):
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	sql = "select %s from %s;" % (term, table)
	cur.execute(sql)
	data = cur.fetchall()
	cur.close()
	return data

def read_user():
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	sql = "SELECT * from Users where username = '%s';"  %str(session['username'])
	cur.execute(sql)
	data = cur.fetchall()
	cur.close()
	return data
def message():
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	sql = "SELECT texto from menssege where destino = '%s';"  %str(session['username'])
	cur.execute(sql)
	data = cur.fetchall()
	cur.close()
	return data

def read_public():
	if(session['username'] == 'Haddad'):
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		sql = "SELECT keypb from users where username = '%s';"  %'Bolsonaro'
		cur.execute(sql)
		data = cur.fetchall()
		cur.close()
		key = data[0][0]
		new = b64decode(key)
		return RSA.importKey(new)
	else:
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		sql = "SELECT keypb from users where username = '%s';"  %'Haddad'
		cur.execute(sql)
		data = cur.fetchall()
		cur.close()
		key = data[0][0]
		new = b64decode(key)
		return RSA.importKey(new)

def read_private(user):
	con2 = psycopg2.connect(host='localhost', database='privatebase',user='postgres', password='klinsman')
	cur2 = con2.cursor(cursor_factory=psycopg2.extras.DictCursor)
	sql = "SELECT keypv from key where users = '%s';"  %user
	cur2.execute(sql)
	data = cur2.fetchall()
	cur2.close()
	key = data[0][0]
	new = b64decode(key)
	return RSA.importKey(new)
	


@app.route('/', methods=['POST','GET'])
def index():		
		#verifica se o usuario está logado no sistema se sim ele redireciona para o painel
	if not session.get('logged_in'):
		return render_template('index.html')
	else:
		return redirect(url_for('painel'))
		

@app.route('/login', methods=['POST','GET'])
def login():

	if request.method == 'POST':
		#faz login no sistema
		if (request.form['submit'] == "b1"):
			login = False
			for x in read_database("username", "Users"):
				for y in x:
					if(request.form['UserName'] == y):
						login = True

			if(login == True):
				session['username'] = request.form['UserName']
				session['logged_in'] = True
				print('logado')

	return redirect(url_for('index'))

@app.route('/painel', methods=['POST','GET'])
def painel():
	#print(read_private('Haddad'))
	#print(encrypt(b'tdc projetos', read_public('Haddad')))
	if not session.get('logged_in'):
		return redirect(url_for('index'))
	else:
		data = read_user()
		if(data[0][2]):
			if(session['username'] == 'Haddad'):
				return render_template('painel.html', msm= True, remetente='Bolsonaro')
			else:
				return render_template('painel.html', msm= True, remetente='Haddad')
		return render_template('painel.html', user=session['username'])


@app.route('/ler', methods=['POST','GET'])
def ler():
	#print(read_private('Haddad'))
	#print(encrypt(b'tdc projetos', read_public('Haddad')))
	if not session.get('logged_in'):
		return redirect(url_for('index'))
	else:
		if(session['username'] == 'Bolsonaro'):
			cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
			sql = "SELECT texto from Menssege where destino = '%s';"  %'Bolsonaro'
			cur.execute(sql)
			data = cur.fetchall()[0][0]

			sql1 = "delete from menssege where destino = 'Bolsonaro';"
			cur.execute(sql1)
			g.db.commit()
			sql2 = "UPDATE Users SET msm = False WHERE username = '%s';" %'Bolsonaro'
			cur.execute(sql2)
			g.db.commit()
			cur.close()

			descryptoText = decrypt(b64decode(data), read_private('Bolsonaro'))
			return render_template('ler.html',texto=descryptoText.decode())
		else:
			cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
			sql = "SELECT texto from Menssege where destino = '%s';"  %'Haddad'
			cur.execute(sql)
			data = cur.fetchall()[0][0]
			sql1 = "delete from menssege where destino = 'Haddad';"
			cur.execute(sql1)
			g.db.commit()
			sql2 = "UPDATE Users SET msm = False WHERE username = '%s';" %'Haddad'
			cur.execute(sql2)
			g.db.commit()
			cur.close()

			descryptoText = decrypt(b64decode(data), read_private('Haddad'))
			return render_template('ler.html',texto=descryptoText.decode())

@app.route('/send', methods=['POST','GET'])
def send():
	#print(read_private('Haddad'))
	#print(encrypt(b'tdc projetos', read_public('Haddad')))
	if not session.get('logged_in'):
		return redirect(url_for('index'))
	else:
		if(session['username'] == 'Haddad'):
			textoRec = ''
			if request.method == 'POST':
				textoRec = request.form['message']
			print(textoRec)
			textoCrypto = encrypt(textoRec.encode(),read_public())
			textoFinal = b64encode(textoCrypto).decode()
			print(textoCrypto)
			cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
			sql1 = "insert into Menssege(destino, texto) values ('%s', '%s')" %('Bolsonaro',textoFinal)
			cur.execute(sql1)
			g.db.commit()

			sql2 = "UPDATE Users SET msm = True WHERE username = '%s';" %'Bolsonaro'
			cur.execute(sql2)
			g.db.commit()
			cur.close()
			return redirect(url_for('painel'))
		else:
			textoRec = ''
			if request.method == 'POST':
				textoRec = request.form['message']
			print(textoRec)
			textoCrypto = encrypt(textoRec.encode(),read_public())
			textoFinal = b64encode(textoCrypto).decode()
			print(textoCrypto)
			cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
			sql1 = "insert into Menssege(destino, texto) values ('%s', '%s')" %('Haddad',textoFinal)
			cur.execute(sql1)
			g.db.commit()
			sql2 = "UPDATE Users SET msm = True WHERE username = '%s';" %'Haddad'
			cur.execute(sql2)
			g.db.commit()
			cur.close()
			return redirect(url_for('painel'))

	