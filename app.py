from flask import *
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from flask_moment import Moment
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://neil1:neil1234@ds113853.mlab.com:13853/neilantony2710login?retryWrites=false"
app.config['SECRET_KEY'] = 'secret'
Bootstrap(app)
mongo = PyMongo(app)
moment = Moment(app)


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        if 'login' not in session:

            return redirect('/login')
        else:
            y = mongo.db.SmxPosts.find().sort('time',-1).limit(5)

            print(datetime.utcnow())
            return render_template('/index.html', y=y)
    if request.method == "POST":
        y = {}
        y['title'] = request.form['title']
        y['post'] = request.form['post']
        y['picture'] = request.form['picture']
        y['time'] = datetime.utcnow()
        mongo.db.SmxPosts.insert_one(y)
        flash('Post Created Successfully || Title: ' + y['title'] + ' || Post: ' + y['post'] + str(y['time']))
        return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        y = {}
        y['fname'] = request.form['firstname']
        y['lname'] = request.form['lastname']
        y['email'] = request.form['email']
        y['password'] = request.form['password']
        print(y)
        x = mongo.db.SMxUserxInfo.find_one({'email': y['email']})
        if x is not None:
            flash('Account with E-Mail already created.')
            return redirect('/login')
        mongo.db.SMxUserxInfo.insert_one(y)
        flash('Account created, Now login')
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            flash('You are already logged in.')
            return redirect('/')
        else:
            return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        y = mongo.db.SMxUserxInfo.find_one({'email': email, 'password': password})
        if y is None:

            flash('incorrect information')
            return redirect('/login')
        else:

            session['login'] = 'Success'
            session['loginTime'] = datetime.utcnow()

            flash('Success!')
        return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.errorhandler(404)
def bad_request(e):
    return render_template('error404.html', e=e)
@app.errorhandler(500)
def internal_error(e):
    return render_template('error500.html', e=e)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


#HW: Social Network