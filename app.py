import pandas as pd
import joblib
from flask import Flask,url_for,render_template
from forms import InputForm

# this package for login and signup
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import datetime  # Import the datetime module


app = Flask(__name__)

app.config["SECRET_KEY"] = "secret_key"

model = joblib.load("model.joblib")

# @app.route("/")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    form = InputForm()
    if form.validate_on_submit():
        x_new = pd.DataFrame(dict(
            airline=[form.airline.data],
            date_of_journey=[form.date_of_journey.data.strftime("%Y-%m-%d")],
            source=[form.source.data],
            destination=[form.destination.data],
            dep_time=[form.dep_time.data.strftime("%H:%M:%S")],
            arrival_time=[form.arrival_time.data.strftime("%H:%M:%S")],
            duration=[form.duration.data],
            total_stops=[form.total_stops.data],
            additional_info=[form.additional_info.data]
        ))
        prediction = model.predict(x_new)[0]
        message = f"The predicted price is {prediction:,.0f} INR!"
        
    else:
        message = "Please provide valid input details!"
    return render_template("predict.html", title="Predict", form=form, output=message)




app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Replace the connection string with your MongoDB URI
client = MongoClient('mongodb://localhost:27017')
db = client['Human']  # Replace with your database name
signup_collection = db['signup']
login_collection = db['login']

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        if 'signup' in request.form:
            return redirect(url_for('signup'))
        elif 'login' in request.form:
            return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = signup_collection.find_one({'username': username})
        if existing_user:
            return "User already exists! Please log in."

        signup_collection.insert_one({
            'username': username,
            'email': email,
            'password': password  # Storing plain text password (Not recommended for production)
        })
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Corrected condition
        username = request.form['username']
        password = request.form['password']

        user = signup_collection.find_one({'username': username})
        if user and user['password'] == password:
            login_collection.insert_one({
                'username': username,
                'login_time': datetime.datetime.now()  # Log the login time
            })
            session['username'] = username
            return redirect(url_for('predict'))
        return "Invalid credentials! Please try again."
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)