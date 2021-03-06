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
            y = []

            currentPosts = list(mongo.db.SmxPosts.find())
            for post in currentPosts:
                if post['email'] != session['login']:
                    y.append(post)


            # following = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
            # following = following['following']
            #
            # for z in following:
            #
            #     currentPosts = list(mongo.db.SmxPosts.find({'email': z}))
            #     for post in currentPosts:
            #         y.append(post)

                # z = list(mongo.db.SmxPosts.find({'email': z}))


            return render_template('/index.html', y=y)
    if request.method == "POST":
        y = {}
        y['title'] = request.form['title']
        y['post'] = request.form['post']
        y['picture'] = request.form['picture']
        y['email'] = session['login']
        y['time'] = datetime.utcnow()
        mongo.db.SmxPosts.insert_one(y)
        flash('Post Created Successfully || Title: ' + y['title'] + ' || Post: ' + y['post'])
        return redirect('/')



@app.route('/myprofile', methods=['GET', 'POST'])
def myprofile():
    y = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
    if request.method == 'GET':
        myPosts = list(mongo.db.SmxPosts.find({'email': session['login']}))

        return render_template('myprofile.html', postData=myPosts, y=y)
    if request.method == 'POST':
        y = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
        y['fname'] = request.form['fname']
        y['lname'] = request.form['lname']
        y['password'] = request.form['password']
        mongo.db.SMxUserxInfo.save(y)
        return redirect('/myprofile')


@app.route('/follow<id>')
def follow(id):
    y = mongo.db.SMxUserxInfo.find_one({'_id': ObjectId(id)})
    x = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
    x['following'].append(y['email'])
    y['followers'].append(x['email'])
    mongo.db.SMxUserxInfo.save(x)
    mongo.db.SMxUserxInfo.save(y)
    return redirect('/')


@app.route('/unfollow<id>')
def unfollow(id):
    y = mongo.db.SMxUserxInfo.find_one({'_id': ObjectId(id)})
    x = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
    x['following'].remove(y['email'])
    y['followers'].remove(x['email'])
    mongo.db.SMxUserxInfo.save(x)
    mongo.db.SMxUserxInfo.save(y)
    return redirect('/')


@app.route('/deletepost<id>')
def deletepost(id):
    mongo.db.SmxPosts.delete_one({'_id': ObjectId(id)})
    return redirect('/myprofile')


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        inbox = mongo.db.SMxMessages.find({'to': session['login']}).sort('time', -1)

        return render_template('messages.html', inbox=inbox)
    if request.method == 'POST':
        y = {}
        y['to'] = request.form['to']
        y['title'] = request.form['title']
        y['content'] = request.form['content']
        y['from'] = session['login']
        y['time'] = datetime.utcnow()

        mongo.db.SMxMessages.insert_one(y)
        flash('Message Sent')
        return redirect('/messages')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        y = {}
        y['fname'] = request.form['firstname'].title()
        y['lname'] = request.form['lastname'].title()
        y['email'] = request.form['email']
        y['password'] = request.form['password']
        y['following'] = []
        y['followers'] = []
        y['schedule'] = {}

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

            session['login'] = email
            session['loginTime'] = datetime.utcnow()

            flash('Success!')
        return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        conditionalStatements = [{'fname': request.form['search'].title()}, {'lname': request.form['search'].title()},
                                 {'email': request.form['search']}]

        y = list(mongo.db.SMxUserxInfo.find({'$or': conditionalStatements}))
        xy = mongo.db.SMxUserxInfo.find_one({'email': session['login']})

        for z in y:
            if xy['email'] == z['email']:
                y.remove(z)

        return render_template('search.html', y=y, xy=xy)
    else:
        return redirect('/')


@app.route('/mySchedule')
def mySchedule():
    if 'login' in session:
        currentUser = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
        currentSchedule = currentUser['schedule']
        return render_template('mySchedule.html', currentSchedule=currentSchedule)

    else:
        return redirect('/login')


@app.route('/addToSchedule/<day>/<slot>/')
def removeslot(day, slot):
    if 'login' in session:
        current_schedule = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
        if day + slot not in current_schedule['schedule']:
            return redirect('/mySchedule')
        else:
            current_schedule['schedule'].pop(day + slot)
            mongo.db.SMxUserxInfo.update_one({'email': session['login']}, {'$set': current_schedule})
            return redirect('/mySchedule')


@app.route('/addToSchedule/<day>/<slot>/<info>')
def addSchedule(day, slot, info):
    if slot.isnumeric() == False:
        flash('Slot Invalid')
        return redirect('/mySchedule')
    if 'login' in session:
        return_value = day + slot + info
        current_schedule = mongo.db.SMxUserxInfo.find_one({'email': session['login']})
        if 'schedule' not in current_schedule:
            current_schedule['schedule'] = {}
        current_schedule['schedule'][day + slot] = info
        mongo.db.SMxUserxInfo.update_one({'email': session['login']}, {'$set': current_schedule})
        flash(day + ' slot ' + slot + ' updated.')
        return redirect('/mySchedule')
    else:
        return redirect('/login')


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
