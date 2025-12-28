from flask import Flask, render_template, request, flash, redirect
import pickle
from matplotlib import image
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os
import io
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors


app = Flask(__name__)

app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_auth'

mysql = MySQL(app)

# Load the trained malaria detection model
model_path = "C:/Users/Hp/Desktop/multiple disease/models/malaria_detection_model_vgg19_enhanced.h5"
model = load_model(model_path)

# Function to preprocess the image
def load_and_preprocess_image(image):
    img = image.resize((224, 224))  # Resize the image to the target size
    img_array = np.array(img) / 255.0  # Rescale the image
    img_array = np.expand_dims(img_array, axis=0)  # Expand dims to match model input
    return img_array


# Load the pre-trained pneumonia detection model
modelpneumonia = load_model('C:/Users/Hp/Desktop/multiple disease/models/pneumonia_detection_model_vgg16.h5')

# Function to preprocess the image
def load_and_preprocess_imagepnemuonia(img):
    IMG_HEIGHT = 224
    IMG_WIDTH = 224
    img = img.resize((IMG_HEIGHT, IMG_WIDTH))  # Resize the image to match model input
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize pixel values
    return img_array

def predict(values, dic):
    if len(values) == 8:
        model = pickle.load(open('models/diabetes.pkl','rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 26:
        model = pickle.load(open('models/breast_cancer.pkl','rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 13:
        model = pickle.load(open('models/heart.pkl','rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 18:
        model = pickle.load(open('models/kidney.pkl','rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 10:
        model = pickle.load(open('models/liver.pkl','rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]

# @app.route("/")
# def home():
#     return render_template('home.html')
@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route("/diabetes", methods=['GET', 'POST'])
def diabetesPage():
    return render_template('diabetes.html')

@app.route("/cancer", methods=['GET', 'POST'])
def cancerPage():
    return render_template('breast_cancer.html')

@app.route("/heart", methods=['GET', 'POST'])
def heartPage():
    return render_template('heart.html')

@app.route("/kidney", methods=['GET', 'POST'])
def kidneyPage():
    return render_template('kidney.html')

@app.route("/liver", methods=['GET', 'POST'])
def liverPage():
    return render_template('liver.html')

@app.route("/malaria", methods=['GET', 'POST'])
def malariaPage():
    return render_template('malaria.html')

@app.route("/pneumonia", methods=['GET', 'POST'])
def pneumoniaPage():
    return render_template('pneumonia.html')

@app.route("/predict", methods = ['POST', 'GET'])
def predictPage():
    try:
        if request.method == 'POST':
            to_predict_dict = request.form.to_dict()
            to_predict_list = list(map(float, list(to_predict_dict.values())))
            pred = predict(to_predict_list, to_predict_dict)
    except:
        message = "Please enter valid Data"
        return render_template("home.html", message = message)

    return render_template('predict.html', pred = pred)

# Route for the malaria prediction page
@app.route("/malariapredict", methods=['POST', 'GET'])
def malariapredictPage():
    pred = None  # Initialize pred to None
    message = None  # Initialize message to None

    if request.method == 'POST':
        try:
            if 'image' in request.files:
                img = Image.open(request.files['image'])  # Open the uploaded image
                img_array = load_and_preprocess_image(img)  # Preprocess the image
                prediction = model.predict(img_array)  # Make the prediction
                pred = (prediction > 0.5).astype(int)[0][0]  # Get binary result

                # Determine if the image is infected or not
                if pred == 0:
                    message = "The image is infected with malaria."
                else:
                    message = "The image is not infected with malaria."
        except Exception as e:
            message = f"Error: {str(e)}. Please upload a valid image."

    return render_template('malaria_predict.html', pred=pred, message=message)



# Route for the pneumonia prediction page
@app.route("/pneumoniapredict", methods=['POST', 'GET'])
def pneumoniapredictPage():
    pred = None  # Initialize pred to None
    message = None  # Initialize message to None

    if request.method == 'POST':
        try:
            if 'image' in request.files:
                img = request.files['image'].read()  # Read the uploaded image
                img = Image.open(io.BytesIO(img))  # Open the image using PIL
                img_array = load_and_preprocess_imagepnemuonia(img)  # Preprocess the image
                prediction = modelpneumonia.predict(img_array)  # Make the prediction
                pred = (prediction > 0.5).astype(int)[0][0]  # Get binary result

                # Determine if the image is infected with pneumonia or not
                if pred == 0:
                    message = "The image shows signs of pneumonia."
                else:
                    message = "The image does not show signs of pneumonia."
        except Exception as e:
            message = f"Error: {str(e)}. Please upload a valid image."

    return render_template('pneumonia_predict.html', pred=pred, message=message)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('Incorrect username or password')
    return render_template('login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        phone_number = request.form['phone_number']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            flash('Username already exists!')
        elif password != confirm_password:
            flash('Passwords do not match!')
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, email, password, dob, gender, address, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                           (username, email, hashed_password, dob, gender, address, phone_number))
            mysql.connection.commit()
            flash('You are successfully registered!')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout/')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug = True)