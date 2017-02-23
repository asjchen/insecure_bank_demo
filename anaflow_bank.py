#!/usr/bin/env python

"""
Major flaws of this system include:
- SQL injection (an adversary could display the table of user accounts)
- As a corollary, certain usernames will cause the SQL queries to not 
  function correctly
- SHA-1 hashing instead of slow hashing, such as bcrypt (though for large 
  user databases, this could require client-side hashing. However, an attacker
  who stole the table of users and password hashes could then send a hash
  directly to the server and successfully login.)
- Lack of security checks, mainly in the Python web.py backend
"""

import web
import random
from itertools import chain
import hashlib

url_dict = { 
	'Home': '/', \
	'Login': '/login', \
	'Register': '/register', \
	'RegistrationSuccess': '/registration_success', \
	'Profile': '/profile',
	'Logout': '/logout'
	}
urls = tuple(chain.from_iterable([(url_dict[x], x) for x in url_dict]))

web.config.debug = False
db = web.database(dbn='sqlite', db='BankAccount.db')
app = web.application(urls, globals())
store = web.session.DiskStore('sessions')
session = web.session.Session(app, store, initializer={'user': None})

def csrf_token():
	if not session.has_key('csrf_token'):
		from uuid import uuid4
		session.csrf_token = uuid4().hex
	return session.csrf_token

def csrf_protected(f):
	def decorated(*args, **kwargs):
		inp = web.input()
		if not (inp.has_key('csrf_token') and \
			inp.csrf_token == session.pop('csrf_token', None)):
			raise web.HTTPError(
				"400 Bad request",
				{'content-type':'text/html'},
				'Cross-site request forgery (CSRF) attempt (or stale browser '\
				'form). <a href=\"{0}\">Back to the form'\
				'</a>'.format(url_dict['Register'])) 
		return f(*args,**kwargs)
	return decorated

render = web.template.render('templates/', base='base', \
	globals={'csrf_token': csrf_token})

def query_database(query_string):
	try:
		users = list(db.query(query_string))
		return users
	except Exception as e:
		return []

def find_salt(username):
	salt_query_string = 'SELECT Salt FROM BankAccount ' \
		'WHERE Username = \'{0}\''.format(username)
	return query_database(salt_query_string)

# Normally, we would want to check to make sure only one user is returned!
def authenticate(username, password):
	salt_query_results = find_salt(username)
	if salt_query_results == []:
		return False
	salt = salt_query_results[-1].Salt
	candidate_hash = hashlib.sha1(salt + password).hexdigest()
	auth_query_string = 'SELECT Salt FROM BankAccount '\
		'WHERE Username = \'{0}\' ' \
		'AND PasswordHash = \'{1}\''.format(username, candidate_hash)
	auth_query_results = query_database(auth_query_string)
	return (auth_query_results != [])

def make_salt():
	return ''.join([chr(random.randint(37, 127)) for i in range(8)])

def make_account(username, password):
	salt = make_salt()
	password_hash = hashlib.sha1(salt + password).hexdigest()
	db.insert('BankAccount', Username=username, Salt=salt,
		PasswordHash=password_hash, Amount=random.randint(0, 999999999))

def get_profile(username):
	amount_query_string = 'SELECT Amount FROM BankAccount ' \
		'WHERE Username = \'{0}\''.format(username)
	amount_query = query_database(amount_query_string)
	if amount_query == []:
		return None
	return amount_query[-1].Amount

def get_links():
	links = [('Home', url_dict['Home'])]
	if session.user == None:
		nonhome_links = ['Login', 'Register']
	else:
		nonhome_links = ['Profile', 'Logout']
	links += [(name, url_dict[name]) for name in nonhome_links]
	return links

class Home:
	def GET(self):
		links = get_links()
		return render.index(links)

class Register:
	def GET(self):
		if session.user == None:
			links = get_links()
			registration_errors = {}
			return render.register(links, registration_errors, csrf_token)
		else:
			raise web.seeother(url_dict['Profile'])

	@csrf_protected
	def POST(self):
		links = get_links()
		params = web.input()
		username = params['username'].strip()
		password1 = params['password1'].strip()
		password2 = params['password2'].strip()
		if password1 != password2:
			registration_errors = {'mismatched_passwords': True}
			return render.register(links, registration_errors, csrf_token)
		if find_salt(username) != []:
			registration_errors = {'username_taken': True, 'username': username}
			return render.register(links, registration_errors, csrf_token)
		make_account(username, password1)
		raise web.seeother(url_dict['RegistrationSuccess'])

class RegistrationSuccess:
	def GET(self):
		links = get_links()
		login_link = url_dict['Login']
		return render.registration_success(links, login_link)

class Login:
	def GET(self):
		if session.user == None:
			links = get_links()
			login_errors = {}
			register_link = url_dict['Register']
			return render.login(links, login_errors, register_link, csrf_token)
		else:
			raise web.seeother(url_dict['Profile'])

	@csrf_protected
	def POST(self):
		params = web.input()
		username = params['username'].strip()
		password = params['password'].strip()
		if authenticate(username, password):
			session.user = username
			raise web.seeother(url_dict['Profile'])
		else:
			links = get_links()
			login_errors = {'wrong_combination'}
			register_link = url_dict['Register']
			return render.login(links, login_errors, register_link, csrf_token)

class Profile:
	def GET(self):
		if session.user == None:
			raise web.seeother(url_dict['Login'])
		else:
			links = get_links()
			amount = get_profile(session.user)
			return render.profile(links, session.user, amount)

class Logout:
	def GET(self):
		if session.user != None:
			session.user = None
		raise web.seeother(url_dict['Login'])

if __name__ == '__main__':
	app.run()


