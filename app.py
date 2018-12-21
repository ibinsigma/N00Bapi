import os
from flask import Flask,render_template,url_for,request,redirect
from flask_bootstrap import Bootstrap
#import pandas as pd
#import numpy as np

#ML PACKAGES

import cv2
from darkflow.net.build import TFNet
#import matplotlib.pyplot as plt

#Login page
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


#----------------------------------

app = Flask(__name__)
# --
app.config['SECRET_KEY'] = 'thisissupposedtobeVsecret'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////home/niloy/N00Bapi/database.db' 
Bootstrap(app)
db = SQLAlchemy(app)

# --
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=2, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=2, max=80)])

# --


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
	return render_template('indexx.html')

# Appending the YOLO code here....


@app.route('/predict',methods=['POST'])
def predict():
	
	options = {
    'model': 'models/yolo.cfg',
    'load': 'models/yolov2.weights',
    'threshold': 0.3,
    #'gpu': 1.0
	}
	tfnet = TFNet(options)
	
	target = os.path.join(APP_ROOT,'static/')
	print(target)

	if not os.path.isdir(target):
		os.mkdir(target)

	for file in request.files.getlist("file"):
		print(file)
		filename = file.filename
		destination = "/".join([target, filename])
		print(destination)
		file.save(destination)

	# YOLOOOOOOOO----

	img = cv2.imread(filename, cv2.IMREAD_COLOR)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

	# use YOLO to predict the image
	result = tfnet.return_predict(img)

	img.shape


	# In[22]:


	# pull out some info from the results

	tl = (result[0]['topleft']['x'], result[0]['topleft']['y'])
	br = (result[0]['bottomright']['x'], result[0]['bottomright']['y'])
	label = result[0]['label']


	# add the box and label and display it
	
	#img = cv2.rectangle(img, tl, br, (0, 255, 0), 7)
	#img = cv2.putText(img, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
	#plt.imshow(img)
	#plt.show()
# In[ ]:


# WOW!


	
	return render_template("results.html", image_name=filename,value=label)


# ----------------------------------------------------- New Code for login page....
@app.route('/login', methods=['GET', 'POST'])
def login():
	#return render_template('login.html')
	form = LoginForm()
	print("1")
	if form.validate_on_submit():
		print("1")
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if user.password == form.password.data:
				#return redirect(url_for('index'))
				return render_template('loginn.html')
		return '<h3>Invalid username or password</h3>'

	return render_template('login.html',form=form)




if __name__ == '__main__':
	app.run(debug=True,host='192.168.2.56',port=5000)
