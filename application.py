import pandas as pd
import boto3
from flask import Flask
from flask import render_template
from flask_restful import Api

application = Flask(__name__)
api = Api(application)

s3 = boto3.client('s3')


def load_dataframe(file_name):
    obj = s3.get_object(Bucket='co.data.covid19-us-east-2', Key=f'countries/{file_name}')
    return pd.read_csv(obj['Body'])


@application.route('/')
@application.route('/index')
def index():
    confirmed_df = load_dataframe('Colombia_confirmed.csv')
    confirmed_df.fillna(0, inplace=True)
    deaths_df = load_dataframe('Colombia_deaths.csv')
    recovered_df = load_dataframe('Colombia_recovered.csv')

    predicted_confirmed_df = load_dataframe('Colombia_predicted_confirmed.csv')
    predicted_deaths_df = load_dataframe('Colombia_predicted_deaths.csv')
    predicted_recovered_df = load_dataframe('Colombia_predicted_recovered.csv')

    return render_template(
        'index.html',
        labels=list(confirmed_df['date'].values),
        predicted_labels=list(predicted_confirmed_df['date'].values),
        confirmed=list(confirmed_df['daily_cases'].values),
        deaths=list(deaths_df['daily_cases'].values),
        recovered=list(recovered_df['daily_cases'].values),
        acumulated_confirmed=list(confirmed_df['y'].astype(float).values),
        acumulated_deaths=list(deaths_df['y'].astype(float).values),
        acumulated_recovered=list(recovered_df['y'].astype(float).values),
        predictions_confirmed=list(predicted_confirmed_df['y'].astype(float).values),
        predictions_deaths=list(predicted_deaths_df['y'].astype(float).values),
        predictions_recovered=list(predicted_recovered_df['y'].astype(float).values),
    )


if __name__ == '__main__':
    application.debug = True
    application.run()
