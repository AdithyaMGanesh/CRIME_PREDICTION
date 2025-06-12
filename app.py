import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error,r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import geopandas as gpd
import folium
from flask import Flask, request, render_template,send_file

matplotlib.use('agg')

app = Flask(__name__)


df = pd.read_csv("01_District_wise_crimes_committed_IPC_2001_2012.csv")

zero_columns = ['CUSTODIAL RAPE','PREPARATION AND ASSEMBLY FOR DACOITY','COUNTERFIETING','DOWRY DEATHS','INSULT TO MODESTY OF WOMEN','IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES']
df = df.drop(zero_columns, axis = 1)    #if axis = 0 drops rows if 1 drops columns
state_ut1 = df['STATE/UT'].unique()
crimes_list1 = df.columns[3:33]

def train_model(target_crime):
    X = df[['STATE/UT', 'DISTRICT', 'YEAR']]    
    y = df[target_crime]

    y = y.apply(pd.to_numeric, errors='coerce')    #convert to numeric

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat_district', OneHotEncoder(handle_unknown='ignore'), ['DISTRICT']),
            ('cat_state', OneHotEncoder(handle_unknown='ignore'), ['STATE/UT'])
        ],
        remainder='passthrough'
    )

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor',LinearRegression())
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    return model

def rf_train_model(target_crime):
    X = df[['STATE/UT', 'DISTRICT', 'YEAR']]    
    y = df[target_crime]

    y = y.apply(pd.to_numeric, errors='coerce')  

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat_district', OneHotEncoder(handle_unknown='ignore'), ['DISTRICT']),
            ('cat_state', OneHotEncoder(handle_unknown='ignore'), ['STATE/UT'])
        ],
        remainder='passthrough'
    )

    random_forest_model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=20,max_depth=None, min_samples_split=2, n_jobs=-1, random_state=42))  
    ])

    random_forest_model.fit(X_train, y_train)

    random_forest_predictions = random_forest_model.predict(X_test)

    random_forest_mse = mean_squared_error(y_test, random_forest_predictions)
    # print("Mean Squared Error:", random_forest_mse)
    r_squared_rf = r2_score(y_test, random_forest_predictions)
    print(r_squared_rf)
    return random_forest_model

def compare(state,district,year,crime_type):
    df2 = pd.read_csv("01_District_wise_crimes_committed_IPC_2019.csv")
    zero_columns1 = ['CUSTODIAL RAPE','PREPARATION AND ASSEMBLY FOR DACOITY','COUNTERFIETING','DOWRY DEATHS','INSULT TO MODESTY OF WOMEN','IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES']
    df2 = df2.drop(zero_columns1,axis=1)
    data_to_compare = df2[(df2['STATE/UT'] == state) & (df2['DISTRICT'] == district) & (df2['YEAR'] == year)]
    actual_crime_rate = data_to_compare[crime_type].values[0]
    return actual_crime_rate


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis', methods=['GET','POST'])
def analysis():
    return render_template('analysis.html')

@app.route('/service', methods=['GET','POST'])
def service():
    return render_template('service.html', state = 'KERALA')

@app.route('/predict_page', methods=['GET','POST'])
def predict_page():
    
    return render_template('predict_main.html',state_ut=state_ut1,crimes_list = crimes_list1,predictions={},comp = "",total_accuracy = "")

@app.route('/accuracy',methods = ['GET','POST'])
def accuracy():
    return render_template('accuracy.html',state_ut=state_ut1,crimes_list = crimes_list1,predictions={},comp = "",total_accuracy = "")

@app.route('/why', methods=['GET','POST'])
def why():
    return render_template('why.html')

@app.route('/predict_crime', methods=['GET','POST'])
def predict_crime():
    model_typo = request.form['model']
    crime_type = request.form['crime_type']
    state_ut = request.form['selected_state_ut']
    district = request.form['districts']
    year = int(request.form['YEAR'])

    input_data = pd.DataFrame({
        "STATE/UT": [state_ut],
        'DISTRICT': [district], 
         'YEAR': [year]
     })

    if model_typo == "A":
        if crime_type == "ALL":
            predictions = {}

            for target_crime in df.columns[3:33]: 

                model = rf_train_model(target_crime)
                prediction = abs(int(model.predict(input_data)[0]))
                predictions[target_crime] = prediction
                
            return render_template('predict_main.html',state_ut=state_ut1,crimes_list = crimes_list1, predictions=predictions,district = district)
        else:
            model = rf_train_model(crime_type)
            prediction = abs(int(model.predict(input_data)[0]))
            return render_template('predict_single.html', prediction=prediction, crime_type=crime_type,state_ut=state_ut1,crimes_list = crimes_list1,district = district)
    else:
        if crime_type == "ALL":
            predictions = {}

            for target_crime in df.columns[3:33]: 

                model = train_model(target_crime)
                prediction = abs(int(model.predict(input_data)[0]))
                predictions[target_crime] = prediction
                
            return render_template('predict_main.html',state_ut=state_ut1,crimes_list = crimes_list1, predictions=predictions,district = district)
        else:
            model = train_model(crime_type)
            prediction = abs(int(model.predict(input_data)[0]))
            return render_template('predict_single.html', prediction=prediction, crime_type=crime_type,state_ut=state_ut1,crimes_list = crimes_list1,district=district)

@app.route('/accuracy_test', methods=['GET','POST'])
def accuracy_test():

    crime_type = request.form['crime_type']
    state_ut = request.form['selected_state_ut']
    district = request.form['districts']
    year = int(request.form['YEAR'])

    input_data = pd.DataFrame({
        "STATE/UT": [state_ut],
        'DISTRICT': [district], 
         'YEAR': [year]
     })

    if crime_type == "ALL":
        predictions = {}
        comp = {}
        total_accuracy = 0
        for target_crime in df.columns[3:33]: 

            model = rf_train_model(target_crime)
            prediction = int(model.predict(input_data)[0])
            predictions[target_crime] = prediction
            com = compare(state_ut,district,2019,target_crime)
            difference = abs(prediction - com)

            if com == 0 and prediction == 0:
                percentage_difference = 100
            elif prediction == 0:
                percentage_difference = int(abs(100 - (difference/com+1)))
            elif com == 0:
                percentage_difference = int(abs(100 - (difference/prediction+1)))
            elif prediction > com:
                percentage_difference = int(abs(100 - (difference/prediction)*100))
            else:
                percentage_difference = int(abs(100 - (difference/com)*100))
            
            total_accuracy = total_accuracy + percentage_difference
            percentage_difference = str(percentage_difference)+'%'
            comp[target_crime] = {'actual_rate': com, 'difference': percentage_difference}
        total_accuracy = str(int(total_accuracy/24))+'%'    
        return render_template('accuracy.html',state_ut=state_ut1,crimes_list = crimes_list1, predictions=predictions,comp = comp,total_accuracy = total_accuracy,dist_name=district)


def crime_choropleth():
    file_path = 'static/modified_india_state.geojson'
    india_states_gdf = gpd.read_file(file_path)

    statewise_crime_rates = df.groupby('STATE/UT')['TOTAL IPC CRIMES'].sum().reset_index()
    statewise_crime_rates['CRIME_RATE'] = statewise_crime_rates['TOTAL IPC CRIMES'] / statewise_crime_rates['TOTAL IPC CRIMES'].max()
    
    merged_data = india_states_gdf.merge(statewise_crime_rates, how='left', left_on='NAME_1', right_on='STATE/UT')
  
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    folium.Choropleth(
        geo_data=india_states_gdf,
        name='choropleth',
        data=merged_data,
        columns=['STATE/UT', 'CRIME_RATE'],
        key_on='feature.properties.NAME_1',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Crime Rate'
    ).add_to(m)

    folium.LayerControl().add_to(m)

    m.save('templates/crime_choropleth.html')

@app.route('/crime_choropleth')
def crime_choropleth():
    return render_template('crime_choropleth.html')

@app.route('/district_wise_total_ipc_crimes', methods = ['GET','POST'])
def district_wise_total_ipc_crimes():
    state = request.args.get('district')
    state_data = df[df['STATE/UT'] == state]

    districtwise_crimes = state_data[state_data['DISTRICT'] != 'TOTAL'].groupby('DISTRICT')['TOTAL IPC CRIMES'].sum().reset_index()

    plt.figure(figsize=(20, 6))
    plt.bar(districtwise_crimes['DISTRICT'], districtwise_crimes['TOTAL IPC CRIMES'], color='skyblue')
    plt.xlabel('District')
    plt.ylabel('Total IPC Crimes')
    plt.title(f'Total IPC Crimes in {state} - District Wise')
    plt.xticks(rotation=90)
    plt.ticklabel_format(axis='y', style='plain')
    plt.tight_layout()
    plt.savefig(f'static/images/{state}_crime_rate.png')
    plt.close()
    return send_file(f'static/images/{state}_crime_rate.png')

@app.route('/total_crimes_in_all_states', methods = ['GET','POST'])
def total_crimes_in_all_states():
    statewise_cirmes = df[~df['STATE/UT'].isin(['D & N HAWELI','DAMAN & DIU','LAKSHADWEEP','SIKKIM'])].groupby('STATE/UT')['TOTAL IPC CRIMES'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.bar(statewise_cirmes['STATE/UT'], statewise_cirmes['TOTAL IPC CRIMES'], color='skyblue')
    plt.xlabel('State/UT')
    plt.ylabel('Total IPC Crimes')
    plt.title('Total IPC Crimes in Each State/UT')
    plt.xticks(rotation=75)
    plt.ticklabel_format(axis='y', style='plain')
    plt.tight_layout()
    plt.savefig('static/images/crime_rates_across_states.png')
    plt.close()
    return send_file('static/images/crime_rates_across_states.png')

@app.route('/all_state_year_wise_crimes', methods = ['GET','POST'])
def all_state_year_wise_crimes():
    all_state_yearwise_crimes = df.groupby(['STATE/UT', 'YEAR'])['TOTAL IPC CRIMES'].sum().reset_index()
    plt.figure(figsize=(12, 8))

    for state in all_state_yearwise_crimes['STATE/UT'].unique():
        state_data = all_state_yearwise_crimes[all_state_yearwise_crimes['STATE/UT'] == state]
        plt.plot(state_data['YEAR'], state_data['TOTAL IPC CRIMES'], label=state)

    plt.xlabel('Year')
    plt.ylabel('Total IPC Crimes')
    plt.title('Total IPC Crimes for Each State Over the Years')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f'static/images/all_state_yearwise_crimes.png')
    return send_file(f'static/images/all_state_yearwise_crimes.png')

@app.route('/state_year_wise_crimes', methods = ['GET','POST'])
def state_year_wise_crimes():
    state = request.args.get('district')
    state_data = df[df['STATE/UT'] == state]

    state_yearwise_crimes = state_data.groupby('YEAR')['TOTAL IPC CRIMES'].sum().reset_index()

    plt.figure(figsize=(12, 8))
    plt.plot(state_yearwise_crimes['YEAR'], state_yearwise_crimes['TOTAL IPC CRIMES'], marker='o', color='skyblue', linestyle='-')
    plt.xlabel('Year')
    plt.ylabel('Total IPC Crimes')
    plt.title(f'Total IPC Crimes for {state} Over the Years')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'static/images/{state}_yearwise_crimes.png')
    return send_file(f'static/images/{state}_yearwise_crimes.png')

@app.route('/year_wise_crime_rates', methods = ['GET','POST'])
def year_wise_crime_rates():
    year_to_compare = int(request.args.get('year'))
    data_for_year = df[df['YEAR'] == year_to_compare]
    state_crime_rates = data_for_year.groupby('STATE/UT')['TOTAL IPC CRIMES'].sum().sort_values()

    plt.figure(figsize=(18, 8))
    state_crime_rates.plot(kind='bar')
    plt.title(f'Crime Rates Across State in {year_to_compare}')
    plt.xlabel('State')
    plt.ylabel('Total Crime Rate')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(f'static/images/{year_to_compare}_crime_rates.png')
    return send_file(f'static/images/{year_to_compare}_crime_rates.png')

@app.route('/correlation_heat_map', methods = ['GET','POST'])
def correlation_heat_map():
    plt.figure(figsize=(14, 14))
    correlation_matrix = df.iloc[:, 3:28].corr()
    sns.heatmap(correlation_matrix, annot=True,fmt='.2f',linewidths=.8, cmap='coolwarm')
    plt.title('Correlation Heatmap of Crime Types')
    plt.tight_layout()
    plt.savefig(f'static/images/correlation_heatmap.png')
    return send_file(f'static/images/correlation_heatmap.png')

if __name__ == '__main__':
    app.run(debug=True)