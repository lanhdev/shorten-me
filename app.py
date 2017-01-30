#app.py
from flask import Flask, request, render_template, redirect
from flask.ext.heroku import Heroku
from urlparse import urlparse
import random
import string
import psycopg2

#connecting to database
db = psycopg2.connect("dbname=postgres")
#set this mode so every statement is invoked immediately
db.autocommit = True

#cursor to operate database
cursor = db.cursor()

#setup database
# cursor.execute('''
# DROP TABLE IF EXISTS urls;
# CREATE TABLE urls (
#     id SERIAL PRIMARY KEY NOT NULL,
#     url               TEXT NOT NULL,
#     code              TEXT NOT NULL,
#     hits              INTEGER
# );
# ''')

#Building web app
host = 'https://lanhhoang-url-shorterner.herokuapp.com/'
app = Flask(__name__)
heroku = Heroku(app)

@app.route('/', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		original_url = request.form.get('original-url')
		code = code_generator()
		if not valid_url_checker(original_url):
			return render_template('index.html',err_msg = "Please enter a valid URL")
		try:
			cursor.execute("INSERT INTO urls (url,code,hits) VALUES (%s, %s, 0)",(original_url,code))
			print "Insert successfully"
		except:
			print "Cannot insert"
		return render_template('index.html',shorten_url=host+code)
	return render_template('index.html')

@app.route('/<code>')
def original_redirect(code):
	try:
		cursor.execute("SELECT url FROM urls WHERE code = %s",(code,))
		print "Select successfully" 
		original_url = cursor.fetchone()[0]
		cursor.execute("UPDATE urls SET hits = hits + 1 WHERE code = %s",(code,))
		print original_url
		return redirect(original_url)
	except:
		print "Cannot select"
		return redirect('/')

@app.route('/analytics')
def urls_analytics():
	cursor.execute("SELECT * FROM urls ORDER BY id;")
	urls_array = cursor.fetchmany(10)
	print urls_array
	return render_template('analytics.html',host=host,urls_array=urls_array)

def valid_url_checker(original_url):
	protocol_exist = False
	protocols = ["http","https"]
	if "." not in original_url:
		return False
	url = urlparse(original_url)
	for protocol in protocols:
		if url.scheme == protocol:
			print url.scheme
			protocol_exist = True
	return protocol_exist

def code_generator(size=8, letter=string.ascii_letters + string.digits):
	return ''.join(random.choice(letter) for _ in range(size))

if __name__ == '__main__':
	app.run(debug=True)