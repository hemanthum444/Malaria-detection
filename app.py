from flask import Flask, redirect, url_for, request, render_template, session
from werkzeug.utils import secure_filename
import os
import numpy as np

# Keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Define a flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user authentication function
def is_logged_in():
    return 'username' in session

# Add the is_logged_in function to the template context
@app.context_processor
def inject_is_logged_in():
    return dict(is_logged_in=is_logged_in)

# Load your trained model
MODEL_PATH = "malariagit97_final.h5"
model = load_model(MODEL_PATH)

# Function for model prediction
def model_predict(img_path, model):
    test_image = image.load_img(img_path, target_size=(64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    result = model.predict(test_image)
    if result[0][0] == 0:
        preds = 'The Person is Infected With Malaria'
    else:
        preds = 'The Person is not Infected With Malaria'
    return preds

@app.route('/', methods=['GET'])
def index():
    if not is_logged_in():
        return redirect(url_for('register'))
    # Main page
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Implement your registration logic here
        # Example: store user credentials in a database
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('upload'))
    if request.method == 'POST':
        # Implement your login logic here
        # Example: validate user credentials from a database
        username = request.form['username']
        password = request.form['password']
        
        # Example: check if the username and password are correct
        if username == 'example_user' and password == 'example_password':
            # Set up session
            session['username'] = username
            # Redirect to choose file page
            return redirect(url_for('upload'))
        else:
            # Incorrect username or password, redirect back to login page
            return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        result = preds  # Replace this with your result handling
        return render_template('result.html', result=result)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
