import pandas as pd
import boto3
from flask import Flask
from flask import render_template, request
from flask_restful import Api

application = Flask(__name__)
api = Api(application)

s3 = boto3.client('s3')
s3_bucket = 'co.data.covid19-us-east-2'


def load_dataframe(file_name):
    obj = s3.get_object(Bucket=s3_bucket, Key=file_name)
    return pd.read_csv(obj['Body'])


@application.route('/')
@application.route('/index')
def index():
    country = request.args.get('country', 'Colombia')
    countries_df = load_dataframe('processed_countries.csv')
    print(f'countries/{country}_confirmed.csv')
    confirmed_df = load_dataframe(f'countries/{country}_confirmed.csv')
    confirmed_df.fillna(0, inplace=True)
    deaths_df = load_dataframe(f'countries/{country}_deaths.csv')
    recovered_df = load_dataframe(f'countries/{country}_recovered.csv')

    predicted_confirmed_df = load_dataframe(f'countries/{country}_predicted_confirmed.csv')
    predicted_deaths_df = load_dataframe(f'countries/{country}_predicted_deaths.csv')
    predicted_recovered_df = load_dataframe(f'countries/{country}_predicted_recovered.csv')

    return render_template(
        'index.html',
        country=country,
        countries=list(countries_df['country'].values),
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
