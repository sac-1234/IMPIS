from flask import Flask, render_template, request, redirect, session, url_for, flash
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
import base64
import os
import requests
import sqlite3

app = Flask(__name__)

model = load_model('E:/Medicinal-Leaf-Classification-main/Notebooks/plant.h5')
class_dict = np.load("E:/Medicinal-Leaf-Classification-main/artifacts/class_names.npy", allow_pickle=True)


def create_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_db()

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        
        flash('Signup successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[2] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

# Home route (requires login)


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))




def search_word(word, language='en'):
    url = "https://chatgpt-api8.p.rapidapi.com/"
    payload = [
	{
		"content": "Hello! I'm an AI assistant bot based on ChatGPT 3. How may I help you?",
		"role": "system"
	},
	{
		"content": word,
		"role": "user"
	}
]
    headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "cc5c20336amsh1e3e54bce426f0dp18a8bejsn1da808da25bf",
	"X-RapidAPI-Host": "chatgpt-api8.p.rapidapi.com"
}

    response = requests.post(url, json=payload, headers=headers)

    return response.json()['text']

    
def predict(image):
    IMG_SIZE = (1, 224, 224, 3)

    img = image.resize(IMG_SIZE[1:-1])
    img_arr = np.array(img)
    img_arr = img_arr.reshape(IMG_SIZE)

    pred_proba = model.predict(img_arr)
    pred = np.argmax(pred_proba)
    return pred

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode()


'''@app.route('/')
def alpha():
    return render_template('./signup.html')'''

@app.route('/')
def home():
    background_image = add_bg_from_local("./static/z1.jpg")
    return render_template('index.html', background_image=background_image)

@app.route('/predict', methods=['POST'])
def predict_image():
    if request.method == 'POST':
        file = request.files['file']
        img = Image.open(file)
        img = img.resize((300, 300))

        pred = predict(img)
        name = class_dict[pred]
        result = 'The given image is ' + name 
        return render_template('result.html',variable=[result,search_word(f'medicinal leaf {name}')])
    
@app.route('/about')
def about():
    return render_template("./about.html")

if __name__ == '__main__':
    app.run(debug=True)
