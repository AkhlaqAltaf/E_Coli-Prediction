import pandas as pd

from e_coli_prediction.settings import BASE_DIR
import os
import joblib


class PredictEColi:



    def predict(self,modelname,data):

        try:

            filepath = os.path.join(BASE_DIR, f'src/apps/website/weather_analyser/model/{modelname}.joblib')
            # Load the saved model
            loaded_model = joblib.load(filepath)
            print("Model loaded for prediction")
            data['month_date'] = pd.to_datetime(data['month_date'])

            data['month_date'] = data['month_date'].dt.month + data['month_date'].dt.day

            predictions = loaded_model.predict(data)

            print("Predictions on example data:")
            print(predictions)
            return predictions
        except Exception as e:
            print(e)
            return None









