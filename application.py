import json
import boto3
import pandas as pd

from flask import Flask
from flask import render_template, request
from flask_restful import Api

application = Flask(__name__)
api = Api(application)

s3 = boto3.client('s3')
s3_bucket = 'co.data.covid19-us-east-2'


def init_menu(route):
    menu_items = {'index': 'menu-item', 'compare': 'menu-item', route: 'menu-item-active'}
    return menu_items


def load_dataframe(file_name):
    obj = s3.get_object(Bucket=s3_bucket, Key=file_name)
    return pd.read_csv(obj['Body'])


@application.route('/')
@application.route('/index')
def index():
    menu_items = init_menu('index')
    country = request.args.get('country', 'Colombia')
    countries_df = load_dataframe('processed_countries.csv')

    confirmed_df = load_dataframe(f'countries/{country}_confirmed.csv')
    confirmed_df.fillna(0, inplace=True)

    deaths_df = load_dataframe(f'countries/{country}_deaths.csv')
    recovered_df = load_dataframe(f'countries/{country}_recovered.csv')

    predicted_confirmed_df = load_dataframe(f'countries/{country}_predicted_confirmed.csv')
    predicted_deaths_df = load_dataframe(f'countries/{country}_predicted_deaths.csv')
    predicted_recovered_df = load_dataframe(f'countries/{country}_predicted_recovered.csv')

    return render_template(
        'index.html',
        menu_items=menu_items,
        url_rule=request.url_rule,
        country=country,
        countries=list(countries_df['country'].values),
        confirmed=confirmed_df,
        deaths=deaths_df,
        recovered=recovered_df,

        predictions_confirmed=predicted_confirmed_df,
        predictions_deaths=predicted_deaths_df,
        predictions_recovered=predicted_recovered_df
    )


@application.route('/compare', methods=['GET', 'POST'])
def compare():
    menu_items = init_menu('compare')
    show_plots = False
    post_countries = []
    countries_df = load_dataframe('processed_countries.csv')
    countries_data = {}
    post_report = 'confirmed'
    if request.method == 'POST':
        show_plots = True
        post_report = request.form['report']
        post_countries = json.loads(request.form['countries'])
        post_countries = [country['value'] for country in post_countries]
        for country in post_countries:
            country_df = load_dataframe(f'countries/{country}_{post_report}.csv')
            countries_data[country] = country_df

    return render_template(
        'compare.html',
        menu_items=menu_items,
        url_rule=request.url_rule,
        show_plots=show_plots,
        countries=countries_df,
        post_countries=post_countries,
        post_report=post_report,
        countries_data=countries_data)


if __name__ == '__main__':
    application.debug = True
    application.run()
