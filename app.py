from flask import Flask, request, render_template, redirect, url_for, json
from bokeh.embed import file_html, components
from Food import getdata, get_plot

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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