from flask import Flask,request,render_template,session
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson.objectid import ObjectId

app=Flask(__name__)
app.config['TESTING'] = True
app.secret_key = '5#y2L"F4Q8z'

app.config['MONGO_URI'] = "mongodb://localhost:27017/blog_db"
mongo = PyMongo(app)

connection = MongoClient()
db = connection.blog_db

@app.route('/')
def home():
	return render_template('index.html')

@app.route( '/register/',methods=['GET'])
def loadregister():
	return render_template('register.html')

@app.route('/register/',methods=['POST'])
def signup():
	username = request.form['user']
	password = request.form['pass']
	email  = request.form['email']
	session['username'] = username
	x = db.user.insert_one({'username' : username,'password' : password, 'email' : email})
	session['id'] = str(x.inserted_id)
	return render_template('main1.html')


@app.route('/',methods=['POST'])
def login():
	username = request.form['user']
	password = request.form['pass']
	x=db.user.find_one({'username':username,'password':password})
	if x != None:
		session['username'] = username
		session['id'] = str(x.get('_id'))
		blog_list=[]
		for b in db.blog.find():
			blog_list.append(b)
		return render_template('main1.html',blog_list=blog_list)
	return render_template('index.html',text="Error in username or password")

@app.route('/main/',methods=['GET'])
def main():
	blog_list = []
	blogs = db.blog.find().sort('_id' , -1)
	for b in blogs:
		blog_list.append(b)
	return render_template('main1.html',blog_list=blog_list)

@app.route('/main/',methods=['POST'])
def logout():
	session.clear()
	return render_template('index.html')

@app.route('/create/',methods=['GET'])
def loadcreateblog():
	return render_template('create.html')

@app.route('/create/',methods=['POST'])
def createblog():
	title = request.form['title']
	content = request.form['content']
	db.blog.insert_one({'user_id' : session['id'],'username' : session['username'] , 'title' : title , 'content' : content})
	blog_list = []
	for b in db.blog.find():
		blog_list.append(b)
	return render_template('main1.html',blog_list=blog_list)

@app.route('/myblogs/',methods=['GET'])
def loadmyblogs():
	myblog_list = []
	blogs = db.blog.find({'user_id' : session['id']}).sort('_id',-1)
	for b in blogs:
		myblog_list.append(b)
	return render_template('myblog.html',myblog_list=myblog_list)

@app.route('/myblogs/',methods=['POST'])
def queryblog():
	if request.form['action']=="delete":
		x = request.form['blog_id']
		db.blog.delete_one({'_id' : ObjectId(x)})
		myblog_list=[]
		blogs=db.blog.find({'user_id': session['id']}).sort('_id',-1)
		for b in blogs:
			myblog_list.append(b)
		return render_template('myblog.html',myblog_list=myblog_list)
	elif request.form['action']=="update":
		x = request.form['blog_id']
		blogs = db.blog.find({'_id' : ObjectId(x)})
		title=[]
		content=[]
		for b in blogs:
			title.append(b['title'])
			content.append(b['content'])

		return render_template('update.html',blog_id=x,title=title[0],content=content[0])

	elif request.form['action']=="updated":
		title = request.form['title']
		content = request.form['content']
		x = request.form['blog_id']
		db.blog.update(
            { '_id': ObjectId(x) },
            {
              '$set' : { 'title': title, 'content': content }
                
            }

                              )
		myblog_list=[]
		blogs = db.blog.find({'user_id' : session['id']}).sort('_id',-1)
		for b in blogs:
			myblog_list.append(b)
		return render_template('myblog.html',myblog_list=myblog_list)
	return

