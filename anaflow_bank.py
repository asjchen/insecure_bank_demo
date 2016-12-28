#!/usr/bin/env python

# Major flaws of this system include:
# - SQL injection (an adversary could display the table of user accounts)
# - SHA-1 hashing instead of slow hashing, such as bcrypt (though for large 
#	user databases, this could require client-side hashing. However, an attacker
#	who stole the table of users and password hashes could then send a hash
#	directly to the server and successfully login.)

import sys; sys.path.insert(0, 'lib') 
import os                             
import web
import random
import hashlib
import binascii

urls = (
	'/register', 'Register'
	#,
	#'/login', 'Login',
	#'/profile', 'Profile'
	)


# in sql, use UNHEX() and HEX() when storing, retrieving from database
# figure out how to store binary?
# USE CSRF!!!!!
web.config.debug = False
db = web.database(dbn='sqlite', db='BankAccount.db')
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

def csrf_token():
	if not session.has_key('csrf_token'):
		from uuid import uuid4
		session.csrf_token = uuid4().hex
	return session.csrf_token

def csrf_protected(f):
	def decorated(*args, **kwargs):
		inp = web.input()
		if not (inp.has_key('csrf_token') and inp.csrf_token == session.pop('csrf_token', None)):
			raise web.HTTPError(
				"400 Bad request",
				{'content-type':'text/html'},
				'Cross-site request forgery (CSRF) attempt (or stale browser form). <a href=\"/register\">Back to the form</a>') 
		return f(*args,**kwargs)
	return decorated

render = web.template.render('templates/', globals={'csrf_token': csrf_token})

def query_database(query_string):
	try:
		users = list(db.query(query_string))
		return users
	except Exception as e:
		return []

def find_account(username):
	query_string = 'SELECT * FROM BankAccount WHERE Username = \'' + username + '\''
	return query_database(query_string)

#def authenticate(username, password):

def make_salt():
	return ''.join([chr(random.randint(33, 127)) for i in range(8)])

def make_account(username, password):
	salt = make_salt()
	password_hash = hashlib.sha1(password + salt).hexdigest()
	db.insert('BankAccount', Username=username, Salt=salt,
		PasswordHash=password_hash, Amount=random.randint(0, 999999999))

class Register:
	def GET(self):
		registration_errors = {}
		return render.register(registration_errors, csrf_token)

	@csrf_protected
	def POST(self):
		params = web.input()
		username = params['username'].strip()
		password1 = params['password1'].strip()
		password2 = params['password2'].strip()
		if password1 != password2:
			registration_errors = {'mismatched_passwords': True}
			return render.register(registration_errors, csrf_token)
		if find_account(username) != []:
			registration_errors = {'username_taken': True, 'username': username}
			return render.register(registration_errors, csrf_token)
		make_account(username, password1)
		
		registration_errors = {}
		return render.register(registration_errors, csrf_token)

if __name__ == '__main__':
	#web.internalerror = web.debugerror  
	app.run()


