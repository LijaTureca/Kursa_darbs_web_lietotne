# prediction.py
#https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset (izmantota datu kopa)
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import joblib
import os
from itertools import combinations
import logging
import kagglehub
from database import init_db, get_all_predictions, update_actual_result, save_prediction

logging.basicConfig(level=logging.DEBUG)

MODEL_PATH = 'logistic_model.joblib'
init_db()

dataset_path = kagglehub.dataset_download("andrewsundberg/college-basketball-dataset")
target_file = "cbb.csv"
target_path = os.path.join(dataset_path, target_file)

if os.path.exists(target_path):
    data = pd.read_csv(target_path)
    print(f"Loaded data from: {target_file}")
    logging.debug(f"CSV data loaded successfully. Shape: {data.shape}")
else:
    raise FileNotFoundError(f"{target_file} not found in the downloaded dataset.")

filtered_data = data[(data['W'] >= 0) & (data['BARTHAG'] >= 0)]
logging.debug(f"Data filtered Shape: {filtered_data.shape}")
# Komandu un label pāru izveides funkcija
def create_pairs(df):
    pairs = []
    labels = []

    # Grupējam datus pa gadiem
    for year, group in df.groupby('YEAR'):
        teams = group.to_dict('records')
        # Izveidot visas iespējamās komandu pāru kombinācijas noteikta gadā
        for team1, team2 in combinations(teams, 2):
            feature = []
            for stat in ['ADJOE', 'ADJDE', 'BARTHAG','EFG_D','TORD', '3P_O']:
                feature.append(team1[stat])
                feature.append(team2[stat])
            pairs.append(feature)

            # Label: par uzvarētāju tiek uzskatīta komanda, kas izcīnījusi visvairāk uzvaru.
            labels.append(1 if team1['W'] > team2['W'] else 0)

    logging.debug(f"Created {len(pairs)} pairs with features.")
    # logging.debug(f"Sample pair features: {pairs[:2]}")
    # logging.debug(f"Sample pair labels: {labels[:2]}")
    logging.debug(f"Label distribution: {pd.Series(labels).value_counts()}")
    # print("pairs",pairs)
    # print("labels",labels)

    return np.array(pairs), np.array(labels)


# Ja modelis neeksistē, apmācit to
if not os.path.exists(MODEL_PATH) :
    X, y = create_pairs(filtered_data)

    if len(X) == 0:
        raise ValueError("Nepietiekams datu apjoms modeļa apmācībai")

    logging.debug(f"Обучающий набор данных создан. X shape: {X.shape}, y shape: {y.shape}")

    # Apmacam modeli
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Modeļa saglabāšana
    joblib.dump(model, MODEL_PATH)
    # logging.info("Модель обучена и сохранена.")
else:
    model = joblib.load(MODEL_PATH)


def predict_quantity(predictionModel):
    """
    Prognozē  1. komandas uzvaras varbūtību
    """
    logging.debug("Starting prediction...")

    feature_order = ['ADJOE', 'ADJDE', 'BARTHAG','EFG_D','TORD', '3P_O']

    try:
        # Izveido abu komandu pazīmju vektoru
        team1_features = [float(predictionModel.team1_stats[feature]) for feature in feature_order]
        team2_features = [float(predictionModel.team2_stats[feature]) for feature in feature_order]
    except KeyError as e:
        logging.error(f"Missing feature in team stats: {e}")
        raise
    except ValueError as e:
        logging.error(f"Error converting feature to float: {e}")
        raise

    # logging.debug(f"Team 1 features: {team1_features}")
    # logging.debug(f"Team 2 features: {team2_features}")

    # Apvieno pazīmes
    new_game = np.array([team1_features + team2_features])
    logging.debug(f"Feature vector for prediction: {new_game}")

    # Team 1 uzvaras varbūtības prognozēšana
    predicted_probability = model.predict_proba(new_game)[0][1]
    predicted_probability2 = model.predict_proba(new_game)
    logging.debug(f"Predicted probability: {predicted_probability}")
    logging.debug(f"Predicted probability: {predicted_probability2}")

    ave_prediction(user_id = session.get('user_id'),input_data=new_game, prediction=predicted_probability)

    return predicted_probability
