# app.py
import pandas as pd
from flask import Flask, render_template, request
from models import PredictionModel
import prediction
import logging
import kagglehub
import os

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

dataset_path = kagglehub.dataset_download("andrewsundberg/college-basketball-dataset")
csv_files = [file for file in os.listdir(dataset_path) if file.endswith(".csv")]
if csv_files:
    data = pd.read_csv(os.path.join(dataset_path, csv_files[0]))
    print(f"Loaded data from: {csv_files[0]}")
else:
    raise FileNotFoundError("No CSV file found in the downloaded dataset.")


logging.debug(f"CSV data loaded successfully. Shape: {data.shape}")

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



if __name__ == '__main__':
    app.run(debug=True)
