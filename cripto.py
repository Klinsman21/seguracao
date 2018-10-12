from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
import psycopg2

con1 = psycopg2.connect(host='localhost', database='publicbase',user='postgres', password='klinsman')
cur1 = con1.cursor()
con2 = psycopg2.connect(host='localhost', database='privatebase',user='postgres', password='klinsman')
cur2 = con2.cursor()

from Crypto import Random
from base64 import b64encode, b64decode

def geradorChaves(tamanho):
	#2048
	random_generator = Random.new().read
	key = RSA.generate(tamanho, random_generator)
	private = key
	Public = key.publickey()
	return Public, private

Public, Private = geradorChaves(2048)


teste1 = Public.exportKey('DER')

final1 = b64encode(teste1).decode()

teste2 = Private.exportKey('DER')

final2 = b64encode(teste2).decode()
'''
cur.execute("SELECT key FROM cripto;")
key = cur.fetchone()
new = b64decode(key[0])
print(new)
'''


sql1 = "insert into Users(username, keypb) values ('%s', '%s')" %('Bolsonaro',final1)
cur1.execute(sql1)
con1.commit()

sql2 = "insert into key(users, keypv) values ('%s', '%s')" %('Bolsonaro',final2)
cur2.execute(sql2)
con2.commit()

'''
msm = b"tdc projetos"
encrypt = encrypt(msm, Public)
print(decrypt(encrypt, Private))
'''