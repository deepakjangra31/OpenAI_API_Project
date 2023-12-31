from flask import Flask, render_template, request
from openai import OpenAI
import os
import json
import pandas as pd

app = Flask(__name__)

# IMPORT key from module
from secret_key import openai_key

# set an environment variable
os.environ["OPENAI_API_KEY"] = openai_key

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# we obtained this prompt by trial and error, using prompt engineering
def get_prompt_financial():
    return '''Please retrieve company name, revenue, net income and earnings per share (a.k.a. EPS)
    from the following news article. If you can't find the information from this article 
    then return "". Do not make things up.    
    Then retrieve a stock symbol corresponding to that company. For this you can use
    your general knowledge (it doesn't have to be from this article). Always return your
    response as a valid JSON string. The format of that string should be this, 
    {
        "Company Name": "Walmart",
        "Stock Symbol": "WMT",
        "Revenue": "12.34 million",
        "Net Income": "34.78 million",
        "EPS": "2.1 $"
    }
    News Article:
    ============

    '''

# this function takes news article as text parameter, and we will append it with the prompt.
# use openai.ChatCompletion to generate response
def extract_financial_data(text):
    prompt = get_prompt_financial() + text
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        output = response.choices[0].message.content
        data_dict = json.loads(output)
        df = pd.DataFrame([data_dict])
        return df
    except (KeyError, json.JSONDecodeError):
        print("Error parsing OpenAI response.")
        return pd.DataFrame()

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = ""
    dataframe_html = ""
    if request.method == 'POST':
        user_input = request.form['article']
        df = extract_financial_data(user_input)
        if not df.empty:
            # Style the DataFrame for better display
            dataframe_html = df.style.hide_index().set_table_styles([
                {'selector': 'thead tr th', 'props': [('background-color', '#f2f2f2')]}
            ]).render()
    return render_template('index.html', user_input=user_input, dataframe_html=dataframe_html)

if __name__ == '__main__':
    app.run(debug=True)