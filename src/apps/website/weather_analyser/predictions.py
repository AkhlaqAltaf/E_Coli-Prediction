import pandas as pd
from sklearn.preprocessing import LabelEncoder

from e_coli_prediction.settings import BASE_DIR
import os
import joblib




def load_model_and_scaler(creek):
    model_filename = os.path.join(BASE_DIR, f'src/apps/website/weather_analyser/model/models/best_model_{creek}.pkl')
    scaler_filename = os.path.join(BASE_DIR, f'src/apps/website/weather_analyser/model/models/scaler_{creek}.pkl')
    model = joblib.load(model_filename)
    scaler = joblib.load(scaler_filename)
    return model, scaler

# Function to make predictions
def make_predictions(creek, new_data):
    model, scaler = load_model_and_scaler(creek)

    # Preprocess the new data in the same way as the training data
    new_data['month_date'] = pd.to_datetime(new_data['date']).dt.month + pd.to_datetime(new_data['date']).dt.day
    new_data.drop(columns=['date'], inplace=True)

    # Fill missing values with the mean or mode as appropriate
    numeric_columns = new_data.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns:
        new_data[col].fillna(new_data[col].mean(), inplace=True)

    categorical_columns = new_data.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        new_data[col].fillna(new_data[col].mode()[0], inplace=True)

    # Label encoding for the categorical columns
    le = LabelEncoder()
    for col in categorical_columns:
        new_data[col] = le.fit_transform(new_data[col])

    # Define features
    X_new = new_data[['Precipitation', 'Temp', 'MaxTemp', 'MinTemp', 'month_date', 'Season']]

    # Standardize the features
    X_new_scaled = scaler.transform(X_new)

    # Make predictions
    predictions = model.predict(X_new_scaled)
    return predictions









