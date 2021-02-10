from flask import Flask, request, render_template, redirect, url_for, json
# from datetime import datetime

import json
import requests
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models import DatetimeTickFormatter
from bokeh.resources import CDN 
from bokeh.embed import file_html, components
from bokeh.palettes import Spectral3
import pandas_bokeh


app = Flask(__name__)

class Food:

    def __init__(self, name, nutrientdict):
        self.foodName = name
        self.n = nutrientdict

    def toString(self):
        print(self.foodName)
        print(self.n)

    def get(self, i):
        return self.n.get(i, 0)

    def getName(self):
        return self.foodName

    def getN(self):
        return self.n


@app.route('/')
def index():
    return render_template('index.html')



def getdata():
    HEADERS={"x-app-id":"4e13e5aa","x-app-key":"2371b979c007fdf88758574145c58171"}
    DATA={"query": request.form['favfood'], "timezone": "US/Eastern"}
    
    data = requests.post('https://trackapi.nutritionix.com/v2/natural/nutrients', headers=HEADERS,data=DATA).json()

    # constructing and returning an array of the foods

    foods = data['foods']

    Pantry = []  # getting all the food from the json
    for food in foods:
        foodName = food['food_name']  # getting the food name
        fullNutrients = food['full_nutrients']  # getting information
        n = {}  # dictionary containing all the nutrients and their values
        for nutrient in fullNutrients:
            nutrientid = nutrient['attr_id']
            nutrientValue = nutrient['value']
            n[nutrientid] = nutrientValue  # uploading nutr info to dict
        Pantry.append(Food(foodName, n))  # constructing food object

    data_nut = [Food.getN(i) for i in Pantry]
    data_name = [Food.getName(i) for i in Pantry]
    
    xdf = pd.DataFrame(data_nut, index= data_name )
    xdf.loc["total"] = xdf.sum()
    xdf = xdf.reset_index()
    df = xdf.rename(columns={208: 'Calories (kcal)',
                        203: 'Protein (g)', 
                        204: 'Total Fat(g)',
                        205: 'Total Carbs(g)',
                        606: 'Total saturated Fat(g)',
                        291: 'Fiber, total dietary(g)',
                        401: 'Vitamin C(mg)',
                        323: 'Vitamin E(mg)',
                        415: 'Vitamin B6(mg)',
                        301: 'Calcium, Ca(mg)',
                        303: 'Iron, Fe(mg)',
                        304: 'Magnesium, Mg(mg)',
                        305: 'Phosphorus, P(mg)',
                        309: 'Zinc, Zn(mg)',
                        307: 'Sodium, Na(mg)',
                        306: 'Potassium, K(mg)',
                        'index': 'Food items'})
    s_df = df.loc[:,df.columns.isin([ 'Food items',
            'Calories (kcal)',
            'Protein (g)', 
            'Total Fat(g)',
            'Total saturated Fat(g)',
            'Total Carbs(g)',
            'Fiber, total dietary(g)',
            'Vitamin C(mg)',
            'Vitamin E(mg)',
            'Vitamin B6(mg)',
            'Calcium, Ca(mg)',
            'Iron, Fe(mg)',
            'Magnesium, Mg(mg)',
            'Phosphorus, P(mg)',
            'Zinc, Zn(mg)',
            'Sodium, Na(mg)',
            'Potassium, K(mg)'])]
    
    return s_df



def get_plot():
    nu_df  = getdata()

    mac_df = nu_df[['Food items',
           'Protein (g)',
           'Total Fat(g)',
           'Total Carbs(g)', 
           'Fiber, total dietary(g)']]
    
    min_df = nu_df[['Food items', 'Vitamin C(mg)',
               'Vitamin E(mg)',
               'Vitamin B6(mg)',
              'Calcium, Ca(mg)',
              'Iron, Fe(mg)',
                'Magnesium, Mg(mg)',
               'Phosphorus, P(mg)',
               'Zinc, Zn(mg)',
                'Sodium, Na(mg)',
             'Potassium, K(mg)']]
    
    pw = nu_df.plot_bokeh.scatter(x = 'Food items', y = 'Calories (kcal)', show_figure=False )
    px = nu_df.plot_bokeh.scatter(x = 'Calories (kcal)', y= 'Protein (g)', category='Food items', show_figure=False )
    py = nu_df.plot_bokeh.scatter(x = 'Calories (kcal)', y= 'Total Fat(g)', category='Food items', show_figure=False )
    pz = nu_df.plot_bokeh.scatter(x = 'Calories (kcal)', y= 'Total Carbs(g)', category='Food items',show_figure=False )
    pm = mac_df.plot_bokeh.bar(x = 'Food items', ylabel="grams (g)", show_figure=False)
    pn = min_df.plot_bokeh.bar(x = 'Food items', ylabel="milligrams (mg)", show_figure=False)

    
    a_plot = pandas_bokeh.plot_grid([[pw, px], [py, pz]])
    b_plot = pandas_bokeh.plot_grid([[pm, pn]])
    
    return (a_plot, b_plot )

@app.route('/end', methods=['POST'])
def output():

    nu_df  = getdata()
    
    result_plot1, result_plot2 = get_plot()
    script, div = components(result_plot1)
    script2, div2 = components(result_plot2)

    return render_template('end.html', script=script, div=div, script2=script2, div2=div2,
                           tables=[nu_df.to_html(classes=["table-bordered", "table-striped", "table-hover"], header="true")]) 


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

@app.errorhandler(KeyError)
def not_found(e):
    return render_template("500.html")

@app.route('/about')
def about():
    
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)