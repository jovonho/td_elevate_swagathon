from flask import Flask, redirect, send_from_directory, jsonify, request, url_for, render_template
from flask_cors import CORS
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from math import sin, cos, sqrt, atan2, radians
import pandas as pd
import copy
import random
import requests
import geocoder
import numpy as np
import json

davinciAPIkey = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJDQlAiLCJ0ZWFtX2lkIjoiZGExMmEwZmUtNDkzNy0zNzQ3LWI3ZTctZTgzMDQwMTJmNmFiIiwiZXhwIjo5MjIzMzcyMDM2ODU0Nzc1LCJhcHBfaWQiOiJkNzI3OGJmYS1kZmM5LTRlODQtODdhMi01NDZlY2E5YThiOTcifQ.bhEkLXi8LHS6iLJCGGjhmnOfXkkT8LZs1-LaNb3c4j4"

app = Flask(__name__, static_folder='static')
app.debug = True

CORS(app)

current_user = None
form_data = {}

class User(object):
    name = ""
    age = 0
    gender = ""
    income = 0.0
    lat = 0.0
    lng = 0.0
    address = ""
    postCode = ""
    relationStatus = ""
    workAddress = ""
    workLatLng = [0.0, 0.0]
    dailyCost = 0.0
    numInfant = 0
    numTodd = 0
    numPre = 0
    numKinder = 0
    numSchool = 0

    # The class "constructor" - It's actually an initializer
    def __init__(self, name, age, gender, income, lat, lng, address, postCode, relationStatus, workAddress, workLatLng, dailyCost, numInfant, numTodd, numPre, numKinder, numSchool):
        self.name = name
        self.age = age
        self.gender = gender
        self.income = income
        self.lat = lat
        self.lng = lng
        self.address = address
        self.postCode = postCode
        self.relationStatus = relationStatus
        self.workAddress = workAddress
        self.workLatLng = workLatLng
        self.dailyCost = dailyCost
        self.numInfant = numInfant
        self.numTodd = numTodd
        self.numPre = numPre
        self.numKinder = numKinder
        self.numSchool = numSchool

#Here we only consider the user's income. In reality, if the user is in a couple, we should consider the income of both parents.
def calculateFee(numInfant, numToddler, numPreschool, numKinder, numSchool, income):
    ret = 0
    gap1 = 20000
    gap2 = 40000
    feeInf = numInfant*79
    feeTod = numToddler*61
    feePre = numPreschool*46
    feeKin = numKinder*31
    feeSch = numSchool*21.70
    feeSum = feeInf + feeTod + feePre + feeKin + feeSch
    feeSumOver = feeSum + (feeSum*0.15)
    famFee = 0
    famInc = income


    if famInc <= gap1:
        ret = 1

    elif (famInc > gap1 and famInc <= gap2):
        famFee = ((famInc - gap1)*0.10)/(12*21.75)
        famFee = round(famFee, 2)
        if famFee <= 0:
            ret = 1
        elif (famFee > 0 and famFee < feeSum):
            ret = 2
        elif (famFee >= feeSum and famFee < feeSumOver):
            ret =3
        elif (famFee >= feeSumOver):
            ret = 4

    elif (famInc > gap2):
        famFee = ((gap1*0.10) + ((famInc - gap2)*0.30))/(12*21.75)
        famFee = round(famFee,2)

        if famFee <= 0:
            ret = 1
        elif (famFee > 0 and famFee < feeSum):
            ret = 2
        elif (famFee >= feeSum and famFee < feeSumOver):
            ret = 3
        elif (famFee >= feeSumOver):
            ret  =4
    
    ret2={'code': str(ret), 'fee': str(famFee)}

    return ret2


@app.route('/')
def reroute():
	return redirect(url_for('login'))

@app.route('/login')
def login():
	if current_user != None:
		return redirect(url_for('home'))
	return render_template('login.html')

@app.route('/handle_data', methods=['POST'])
def handle_data():
    error=None
    if len(request.form['custId'])==0:
        error="Invalid customer ID"
        return render_template('login.html', error=error)

    for key,val in request.form.items():
        if val=='':
            form_data[key] = 0 if key != "workAddress" else ""
        else:
            if key=='custId' or key == 'workAddress':
                form_data[key] = val
            else:
                form_data[key] = int(val)
    #return render_template('success.html', form_data=form_data)
    response = requests.get('https://api.td-davinci.com/api/customers/' + form_data['custId'],
                                headers = { 'Authorization': davinciAPIkey })
    print(response)

    geocode_r = geocoder.arcgis(form_data["workAddress"])

    global current_user
    if str(response.json()['result']) == 'None':
        error="Invalid customer ID"
        return render_template('login.html', error=error)
    else:
        current_user = User(
            str(response.json()['result']['givenName'] + " " + response.json()['result']['surname']), 
            int(response.json()['result']['age']), 
            str(response.json()['result']['gender']), 
            float(response.json()['result']['totalIncome']),
            float(response.json()['result']['addresses']['principalResidence']['latitude']),
            float(response.json()['result']['addresses']['principalResidence']['longitude']),
            str(response.json()['result']['addresses']['principalResidence']['streetNumber'] + " " + response.json()['result']['addresses']['principalResidence']['streetName']),
            str(response.json()['result']['addresses']['principalResidence']['postalCode']),
            str(response.json()['result']['relationshipStatus']),
            str(form_data["workAddress"]),
            [geocode_r.lat, geocode_r.lng],
            float(form_data["dailyCost"]),
            int(form_data["numInfant"]),
            int(form_data["numToddler"]),
            int(form_data["numPreSchool"]),
            int(form_data["numKinder"]),
            int(form_data["numSchool"]))

    for attr, value in current_user.__dict__.items():
        print(attr, value)

    global subsidyVars
    subsidyVars = calculateFee(form_data['numInfant'], form_data['numToddler'], form_data['numPreSchool'], form_data['numKinder'], form_data['numSchool'], current_user.income)

    return render_template('index.html', current_user=current_user, subsidyVars = subsidyVars)



@app.route('/home')
def home():
    return send_from_directory(app.static_folder, "index.html")

#Read CSV
child_care = pd.read_csv("child-care.csv", encoding="latin1")

def availability_generator(df,listofcolumns):
    new_col = []
    for column in listofcolumns:
        x = []
        for i in range(len(df)):
            x.append(random.randint(0,int((df.iloc[i][column])/2)))
        df[column+'_AVAIL'] = x
        new_col.append(str(column+'_AVAIL'))
    return df, new_col

def calc_distance(lata,lona,latb,lonb):
   # approximate radius of earth in km
    R = 6373.0
    lat1 = radians(lata)
    lon1 = radians(lona)
    lat2 = radians(latb)
    lon2 = radians(lonb)
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def rand_cost_arr(low, high):
    test = []
    for i in range(count_cc_rows):
        rand = random.randrange(low, high)
        test.append(rand)
    return test

def triangle_coef(tip, base0, base1):
    """tip, base0, base1 are [x, y]"""
    base = calc_distance(base0[0], base0[1], base1[0], base1[1])
    side0 = calc_distance(base0[0], base0[1], tip[0], tip[1])
    side1 = calc_distance(base1[0], base1[1], tip[0], tip[1])
    return base / (side0 + side1)

def distance_coef(latlng):
    return triangle_coef(latlng, [current_user.lat, current_user.lng], current_user.workLatLng)

#Preprocessing:
#(1) AUSPICE: (Non Profit = 1 and Commercial = 0)
child_care['AUSPICE'] = (child_care['AUSPICE'] == 'Non Profit Agency').astype(int)

#(2) SUBSIDY: (Subsidized = 1 and Not Subsidized = 0)
child_care['SUBSIDY'] = (child_care['SUBSIDY'] == 'Y').astype(int)

#(3) AVAILABLE SPACE:
avail_space, col = availability_generator(copy.deepcopy(child_care),['IGSPACE','TGSPACE','KGSPACE','PGSPACE','SGSPACE'])
for column in col:
    child_care[column] = avail_space[column]
child_care['TOT_AVAIL'] = child_care[list(col)].sum(axis=1)

#(4) COST OF CHILD CARE (per day)
count_cc_rows = child_care.shape[0]
child_care['cost_IG'] = rand_cost_arr(45,65)
child_care['cost_TG'] = rand_cost_arr(45,65)
child_care['cost_PG'] = rand_cost_arr(35,55)
child_care['cost_KG'] = rand_cost_arr(30,45)
child_care['cost_SG'] = rand_cost_arr(20,35)


#Example ID: d7278bfa-dfc9-4e84-87a2-546eca9a8b97_c418b5e6-ef7a-4774-88bc-762f2e9adc53
@app.route("/getPreprocessedData", methods=['GET'])
def preprocessedData():
    if request.method == 'GET':
        return child_care[['LOC_NAME', 'LONGITUDE', 'LATITUDE', 'PHONE', 'AUSPICE', 'SUBSIDY', #'DIST_FROM_HOME',
                 'IGSPACE', 'TGSPACE', 'PGSPACE', 'KGSPACE', 'SGSPACE', 'TOTSPACE',
                 'IGSPACE_AVAIL', 'TGSPACE_AVAIL', 'KGSPACE_AVAIL', 'PGSPACE_AVAIL', 'SGSPACE_AVAIL', 'TOT_AVAIL',
                 'cost_IG', 'cost_TG', 'cost_PG', 'cost_KG', 'cost_SG']
                ].to_json(orient='index')

@app.route("/getChildCareData")
def childcare():
    #Getting Parameters
    in_loc_lat = current_user.lat
    in_loc_lon = current_user.lng
    # radius = request.values.get('radius', type=int, default=5000)
    max_cost = current_user.dailyCost #Max cost willing to spend per child (per day)
    num_infants = current_user.numInfant #Infants (0-18 months) IGSPACE
    num_toddlers = current_user.numTodd #Toddlers (18-30 months) TGSPACE
    num_preschoolers = current_user.numPre #Preschoolers (30-48 months) PGSPACE
    num_kindergarden = current_user.numKinder #Kindergarden (48-72 months, Full Day Kindergarden) KGSPACE
    num_school = current_user.numSchool #School (72+ months) SGSPACE

    temp = copy.deepcopy(child_care)
    #(1) Distance from home and score based on school location relative to work+home coordinates
    distance_col, dist_score = [], []
    for K, row in child_care.iterrows():
        distance_col.append(calc_distance(float(in_loc_lat),float(in_loc_lon),row['LATITUDE'],row['LONGITUDE']))
        dist_score.append(distance_coef([row['LATITUDE'],row['LONGITUDE']]))

    temp['DIST_FROM_HOME'] = distance_col
    temp['DIST_SCORE'] = dist_score
    temp['RATING'] = np.random.randint(1, 5, child_care.shape[0]) + np.random.rand((child_care.shape[0]))

    filtered1 = temp[temp['DIST_FROM_HOME'] < 5]

    child_mapping = {'num_infants': 'cost_IG', 'num_toddlers':'cost_TG',
                 'num_preschoolers':'cost_PG', 'num_kindergarden':'cost_KG',
                 'num_school':'cost_SG'}

    filtered2 = filtered1[(filtered1['IGSPACE_AVAIL'] >= num_infants) &
                        (filtered1['TGSPACE_AVAIL'] >= num_toddlers) &
                        (filtered1['PGSPACE_AVAIL'] >= num_preschoolers) &
                        (filtered1['KGSPACE_AVAIL'] >= num_kindergarden) &
                        (filtered1['SGSPACE_AVAIL'] >= num_school)]

    avg_cost = []
    num = 0
    for child_class in [('num_infants', num_infants), ('num_toddlers', num_toddlers), ('num_preschoolers', num_preschoolers), ('num_kindergarden', num_kindergarden), ('num_school', num_school)]:
        if child_class[1] > 0:
            num += 1
            if avg_cost == []:
                avg_cost = filtered2[child_mapping[child_class[0]]].values
            else:
                avg_cost += filtered2[child_mapping[child_class[0]]].values

    filtered2['AVG_COST'] = (avg_cost/num)
    X = filtered2[['LATITUDE', 'LONGITUDE', 'RATING', 'AVG_COST', 'DIST_SCORE']]

    recommend_size = 5

    if filtered2.shape[0] > recommend_size:
        k = int(X.shape[0]/recommend_size)

    scaler = MinMaxScaler(feature_range = (0,1))
    trainX = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=k, random_state=0).fit(trainX)

    pred_x = [[float(in_loc_lat), float(in_loc_lon), 5, float(max_cost), 0.9]]

    group_predicted = kmeans.predict(scaler.transform(pred_x))
    where_labels = np.array(kmeans.labels_)
    raw_arr = X.values

    output = pd.DataFrame()
    for idx in np.where(where_labels == group_predicted)[0]:
        if output.empty:
            output = filtered2[(filtered2['LATITUDE']==raw_arr[idx][0]) & (filtered2['LONGITUDE']==raw_arr[idx][1])]
        else:
            output = pd.concat([output, filtered2[(filtered2['LATITUDE']==raw_arr[idx][0]) & (filtered2['LONGITUDE']==raw_arr[idx][1])]])

    output_json = output[['LOC_NAME', 'LONGITUDE', 'LATITUDE', 'PHONE', 'STR_NO', 'STREET', 'UNIT',
             'RATING', 'DIST_FROM_HOME',
             'IGSPACE', 'TGSPACE', 'PGSPACE', 'KGSPACE', 'SGSPACE', 'TOTSPACE',
             'IGSPACE_AVAIL', 'TGSPACE_AVAIL', 'KGSPACE_AVAIL', 'PGSPACE_AVAIL', 'SGSPACE_AVAIL', 'TOT_AVAIL',
             'cost_IG', 'cost_TG', 'cost_PG', 'cost_KG', 'cost_SG']
            ].to_json(orient='records')

    other_json = filtered2[['LOC_NAME', 'LONGITUDE', 'LATITUDE', 'PHONE', 'STR_NO', 'STREET', 'UNIT',
             'RATING', 'DIST_FROM_HOME',
             'IGSPACE', 'TGSPACE', 'PGSPACE', 'KGSPACE', 'SGSPACE', 'TOTSPACE',
             'IGSPACE_AVAIL', 'TGSPACE_AVAIL', 'KGSPACE_AVAIL', 'PGSPACE_AVAIL', 'SGSPACE_AVAIL', 'TOT_AVAIL',
             'cost_IG', 'cost_TG', 'cost_PG', 'cost_KG', 'cost_SG']
            ].to_json(orient='records')
    
    return json.dumps([output_json, other_json])

@app.route("/getAddreses")
def getAddresses():
	if not current_user:
		print("USER NOT FOUND");
	print(current_user)
	output = pd.DataFrame({"lat":[current_user.lat, current_user.workLatLng[0]], "lng":[current_user.lng, current_user.workLatLng[1]]})

	return output.to_json(orient='records')
if __name__ == '__main__':
    app.run()
