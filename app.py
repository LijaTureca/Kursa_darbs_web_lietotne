#app.py
import pandas as pd
from models import PredictionModel
import prediction
import logging
import kagglehub
import os
from database import save_prediction, register_user, authenticate_user, \
    get_user_predictions, SessionLocal, Prediction
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import check_password_hash

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    return response
    
target_file = "cbb.csv"
target_path = os.path.join(dataset_path, target_file)

if os.path.exists(target_path):
    data = pd.read_csv(target_path)
    print(f"Loaded data from: {target_file}")
    logging.debug(f"CSV data loaded successfully. Shape: {data.shape}")
else:
    raise FileNotFoundError(f"{target_file} not found in the downloaded dataset.")



def get_team_stats(team, season):
    """
    Iegūst un apkopo komandas statistiku par norādīto sezonu.
    Atgriež sēriju ar statistiku.
    """
    # Datu filtrēšana pēc komandas un gada
    team_stats = data[(data['TEAM'] == team) & (data['YEAR'] == season)]

    if team_stats.empty:
        raise ValueError(f"No stats found for team {team} in season {season}.")

    # Katrai komandai un sezonai jābūt unikālai
    stats = team_stats.iloc[0]
    logging.debug(f"Stats for {team} in {season}: {stats}")

    # print("stats!!!", stats)
    return stats

def prepare_data(stats):
    features = ['ADJOE', 'ADJDE', 'BARTHAG', 'EFG_O', 'EFG_D',
               'TOR', 'TORD', 'ORB', 'DRB', 'FTR', 'FTRD',
               '2P_O', '2P_D', '3P_O', '3P_D']
    try:
        prepared_stats = stats[features].astype(float)
        logging.debug(f"Prepared stats: {prepared_stats}")
        return prepared_stats
    except KeyError as e:
        logging.error(f"Missing column in data: {e}")
        raise
    except ValueError as e:
        logging.error(f"Error converting data types: {e}")
        raise

@app.route('/')
def index():
    # Unikālu komandu iegūšana no CSV
    try:
        teams = data[['TEAM', 'CONF']].drop_duplicates().sort_values('TEAM').to_dict('records')
        logging.debug(f"Fetched {len(teams)} teams from CSV.")
    except Exception as e:
        logging.error(f"Error processing teams data: {e}")
        teams = []
    return render_template('index.html', teams=teams)

@app.route('/predict', methods=['GET'])
def predict_quantity_route():
    user_id = session.get('user_id')
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))
    
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    season = request.args.get('season')

    if not team1 or not team2 or not season:
        return "Please provide both teams and the season.", 400
    if team1 == team2:
        return "Please provide different teams", 400
    try:
        season = int(season)
    except ValueError:
        return "Season must be a valid year (e.g., 2023).", 400

    try:
        # Komandu datu iegūšana
        team1_stats = get_team_stats(team1, season)
        team2_stats = get_team_stats(team2, season)

        team1_prepared = prepare_data(team1_stats)
        team2_prepared = prepare_data(team2_stats)

        team1_stats_dict = team1_prepared.to_dict()
        team2_stats_dict = team2_prepared.to_dict()
        # print("team1_stats_dict",team1_stats_dict)

        # Prediction
        predictionModel = PredictionModel(team1_stats_dict, team2_stats_dict)
        predicted_outcome = prediction.predict_quantity(predictionModel)

        prediction_id = save_prediction(
            user_id=user_id,
            input_data={'team1': team1, 'team2': team2, 'season': season},
            prediction=predicted_outcome
        )
        outcome = f"Komanda {team1}, visticamāk uzvarēs." if predicted_outcome >= 0.5 else f"Komanda {team2} visticamāk uzvarēs."
        return render_template('result.html', outcome=outcome, predicted_outcome=predicted_outcome, prediction_id=prediction_id,team1=team1, team2=team2)

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return str(ve), 400
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return str(e), 500
        
@app.route("/predictions")
def predictions():
    predictions = get_all_predictions()
    display_predictions = []
    for prediction in predictions:
        try:
            input_data = eval(prediction.input_data)
            if isinstance(input_data, list):
                display_predictions.append({
                    "date": prediction.date,
                    "team1": input_data[0][0], 
                    "team2": input_data[0][1],
                    "season": input_data[0][2],
                    "prediction": prediction.prediction
                })
            elif isinstance(input_data, dict):
                display_predictions.append({
                    "date": prediction.date,
                    "team1": input_data.get('team1'),
                    "team2": input_data.get('team2'),
                    "season": input_data.get('season'),
                    "prediction": prediction.prediction
                })
        except Exception as e:
            app.logger.error(f"Error parsing input data: {e}")

    return render_template("predictions.html", predictions=display_predictions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return render_template('already_logged_in.html',
                               username=session.get('username')) 

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            register_user(username, email, password)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('register.html')


app.secret_key = os.urandom(24)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: 
        print(f"User is already logged in: {session['user_id']}")
        return redirect(url_for('already_logged_in'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for('login'))

        user = authenticate_user(username, password)

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('index')) 
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()  
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('session') 
    flash("You have been logged out.", "info")
    return resp


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/clear_predictions', methods=['POST'])
def clear_predictions():
    try:
        db = SessionLocal()
        db.query(Prediction).delete()
        db.commit()
        db.close()
    except Exception as e:
        flash(f"Ошибка при очистке прогнозов: {e}", "danger")
    return redirect(url_for('predictions'))


@app.route('/already_logged_in')
def already_logged_in():
    if 'user_id' not in session:  
        return redirect(url_for('login'))
    return render_template('already_logged_in.html', username=session.get('username'))


if __name__ == '__main__':
    app.run()
