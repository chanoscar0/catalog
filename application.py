from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = True
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/gconnect', methods = ['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State Parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        #Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = '')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    h = httplib2.Http()
    req = h.request(url, 'GET')[1]
    req_json = req.decode('utf8').replace("'", '"')
    result = json.loads(req_json)    #if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
    #Verify that the access token is used for the intended user_id
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."
        ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current User is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    #Store the credentials for future use in the session
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    #Get User info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    newUser = User(username = login_session['username'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!<h1>'
    output +='<img src = "'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output

#Disconnect - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s' %access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('You have been logged out.')
        return redirect('/catalog/')
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))

    login_session['state'] = state
    return render_template('login.html', STATE = state)

#JSON API to present the Catalog database_setup
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    jsonList = []
    answerList = []
    for c in categories:
        jsonDict = {}
        itemList = []
        items = session.query(Item).filter_by(category_id = c.id).all()
        jsonDict['Category_ID'] = c.id
        jsonDict['Category_Name'] = c.name
        for i in items:
            itemDict = {}
            itemDict['cat_id'] = i.category_id
            itemDict['description'] = i.description
            itemDict['item_id'] = i.id
            itemDict['title'] = i.name
            itemList.append(itemDict)
        jsonDict['Items'] = itemList
        jsonList.append(jsonDict)
    return jsonify(Catalog = jsonList)

#Broad Catalog for Consumers to see
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    recentItems = session.query(Item).order_by(desc(Item.id)).limit(10).all()
    return render_template('publicCategories.html',
           categories = categories,recentItems = recentItems)

#Items under a specific Category
@app.route('/catalog/<path:category_name>/items/')
@app.route('/catalog/<path:category_name>/')
def showItems(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id).all()

    return render_template('publicitems.html', items = items, category = category)
#Specific Item Information
@app.route('/catalog/<path:category_name>/<item_name>/')
def showItem(category_name,item_name):
    item = session.query(Item).filter_by(category_name = category_name,
    name = item_name).one()
    return render_template('showItem.html', item = item)

@app.route('/catalog/new/', methods = ['GET','POST'])
def createItem():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        category = session.query(Category).filter_by(name = request.form['category_name']).one()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       picture=request.form['picture'],
                       category_id=category.id,
                       category_name = category.name,
                       username=login_session['username'])
        session.add(newItem)
        session.commit()
        flash('New %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showItems',
                        category_name = category.name))
    else:
        return render_template('newitem.html', categories = categories)

@app.route('/catalog/<path:item_name>/edit/', methods = ['GET','POST'])
def editItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(name = item_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    if editedItem.username != login_session['username']:
        flash('You cannot edit an item you did not create. Please create your own item.')
        return redirect(url_for('showItem',category_name =editedItem.category_name, item_name = item_name))
    if request.method == "POST":
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        if request.form['category_name']:
            editedItem.category_name = request.form['category_name']
            session.add(editedItem)
            session.commit()
            flash('Item Successfully Edited')
            return redirect(url_for('showItem',
                   category_name = editedItem.category_name,
                   item_name = editedItem.name))
    else:
        return render_template('edititem.html', item=editedItem,
        item_name=item_name, categories = categories)


@app.route('/catalog/<path:item_name>/delete/', methods = ['GET','POST'])
def deleteItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(name = item_name).one()
    category_name = itemToDelete.category_name
    if itemToDelete.username != login_session['username']:
        flash('You cannot delete an item you did not create. Please create your own item.')
        return redirect(url_for('showItem',category_name =itemToDelete.category_name, item_name = item_name))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showItems', category_name = category_name))
    else:
        return render_template('deleteitem.html',
               item=itemToDelete, item_name = item_name)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
