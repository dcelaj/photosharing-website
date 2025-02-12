######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from asyncio.windows_events import NULL
from datetime import date
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

#######################################################
# TODO: Add titles to photos and descriptions to albums
# Make tags & tag search use CSV (also tags under pic)
# Add comment box, add like button and list
# "Add Friend" button/search
# album previews    
# profile too, visit other's profiles?
# (how to get unique link tho??? pass as parameter?)
# PFPs? 
# As of now some pages don't properly redir away, ie up
#######################################################

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'YOUR_PASSWORD_HERE'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



##########begin code used for login##########
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('homepage.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('homepage.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
##########end login code##########



##########get user data#########
def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT name, date, albums_id FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumPhotos(alb):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos Albums WHERE albums_id = '{0}'".format(alb))
	return cursor.fetchall() #TODO:get comments with a diff query...maybe a show comm button? ?

def getPhotoComments(alb):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id, first_name, text FROM Comments NATURAL JOIN Albums NATURAL JOIN Photos NATURAL JOIN Users WHERE albums_id='{0}'".format(alb))
	return cursor.fetchall()

def getTaggedPhotos(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption, albums_id FROM Photos NATURAL JOIN Tagged NATURAL JOIN Tags WHERE name LIKE '%{0}%'".format(tag))
	return cursor.fetchall() #TODO: How to get multiple?

def getFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Friends WHERE user_id1='{0}' OR user_id2='{0}'".format(uid))
	frens = cursor.fetchall()
	frenlist = []
	for x in frens:
		if x[0] == uid:
			frenlist.append(x[0])
		else:
			frenlist.append(x[1])
	return frenlist
##########end##########



#########pages#########
# PROFILE
@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('profile.html', albums=getUserAlbums(uid), name=flask_login.current_user.id, friends=getFriends(uid))


##########begin photo uploading code##########
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		#get info
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		alb = request.form.get('album') #TODO: Convert album name into album id, ALSO CONFIRM ALBUM BELONGS TO USER!!!!!!!!!!!! (unless communal album?)
		photo_data =imgfile.read()

		#upload photo
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Photos (imgdata, user_id, caption, albums_id) VALUES (%s, %s, %s, %s)''' ,(photo_data, uid, caption, alb))
		conn.commit()

		#tags code
		tag = request.form.get('tags')
		if cursor.execute("SELECT name FROM Tags WHERE name='{0}'".format(tag)): #checking if tag exists
			cursor.execute("SELECT tag_id FROM Tags WHERE name='{0}'".format(tag)) #if so grab id
			tid = cursor.fetchone()
		else: #if not then make a new tag
			cursor.execute('''INSERT INTO Tags (name) VALUES (%s)''', (tag))
			conn.commit()
			cursor.execute("SELECT MAX(tag_id) FROM Tags")
			tid = cursor.fetchone()
		cursor.execute("SELECT MAX(photo_id) FROM Photos")
		pid = cursor.fetchone()
		cursor.execute('''INSERT INTO Tagged (photo_id, tag_id) VALUES (%s, %s)''', (pid, tid))
		conn.commit()
		
		return render_template('profile.html', name=flask_login.current_user.id, message='Photo uploaded!', albums=getUsersPhotos(uid), base64=base64, friends=getFriends(uid))
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
##########end photo uploading code##########


#CREATE ALBUM
@app.route('/create', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		#getting info
		td = date.today()
		uid = getUserIdFromEmail(flask_login.current_user.id)
		newalb = request.form.get('albname')

		#####uploading album#####
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Albums (name, date, user_id) VALUES (%s, %s, %s)''', (newalb, td, uid))
		conn.commit()

		#####getting id#####
		cursor.execute("SELECT MAX(albums_id) FROM Albums")
		msg = cursor.fetchone()
		msg = "Album ID #" + str(msg) + " created!"
		
		return render_template('profile.html', name=flask_login.current_user.id, message=msg, albums=getUserAlbums(uid), base64=base64, friends=getFriends(uid))
	else:
		return render_template('create.html')


#VIEW ALBUM
@app.route("/album/<alb_id>", methods=['GET'])
def albm(alb_id):
	cursor = conn.cursor()
	cursor.execute("SELECT name, first_name, user_id FROM Albums NATURAL JOIN Users WHERE albums_id='{0}'".format(alb_id))
	cred = cursor.fetchall()
	return render_template('album.html', albumname=cred, album=getAlbumPhotos(alb_id), comments=getPhotoComments(alb_id), base64=base64)


#SEARCH
@app.route("/search", methods=['GET', 'POST'])
def srch():
	#####TODO: maybe convert into address bar input#####
	tname = request.form.get('search')
	return render_template('homepage.html', results=getTaggedPhotos(tname))


##################################################
#LIKES
@app.route("/like/<pid>", methods=['GET', 'POST'])
@flask_login.login_required
def like(pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute('''INSERT INTO Likes (photo_id, user_id) VALUES (%s, %s)''', (pid, uid))
	conn.commit()
	return flask.redirect(flask.url_for('home'))

#COMMENTS
@app.route("/comm/<pid>", methods=['GET', 'POST'])
@flask_login.login_required
def comment(pid):
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		txt = request.form.get('comm')
		cursor=conn.cursor()
		cursor.execute('''INSERT INTO Comments (photo_id, user_id, text) VALUES (%s, %s, %s)''', (pid, uid, txt))
		conn.commit()
		return flask.redirect(flask.url_for('home'))
	else:
		return '''
			   <form action='#' method='POST'>
				<input type='text' name='comm'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		       <a href='/home'>Home</a>
			   '''

#FRIENDS
@app.route("/edit/add/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def friend(id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute('''INSERT INTO Friends (user_id1, user_id2) VALUES (%s, %s)''', (id, uid))
	conn.commit()
	return flask.redirect(flask.url_for('home'))

@app.route("/edit")
@flask_login.login_required
def editfriend():
	return render_template('edit.html')
##################################################


#HOMEPAGE, not to be confused with the welcome below
@app.route("/home", methods=['GET', 'POST'])
def home():
	if flask_login.user_logged_in:
		return render_template('homepage.html', name=flask_login.current_user.id)
	else:
		return render_template('welcome.html')


#DEFAULT WELCOME PAGE
@app.route("/", methods=['GET'])
def welcome():
	return render_template('welcome.html')


#################################################################################

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
