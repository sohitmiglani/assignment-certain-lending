from flask import session
import random
import os
import http.client
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import os
import matplotlib

def random_id(length): # This function has two doctests inside it to give an example on how to make doctests
    """
    Creates a random configuration key for the session - for safety of session variables.

    >>> len(random_id(50)) == 50
    True

    >>> random_id('hello')
    Traceback (most recent call last):
        ...
    TypeError: The input must be a positive integer.

    """
    if type(length) != int or length < 1:
        raise TypeError('The input must be a positive integer.')

    choices = '0123456789abcdefghijklmnopqrstuvwxyz'

    id = ''
    for _ in range(length):
        id += random.choice(choices)
    return id

def search_property(api_key, add1, add2):

    link = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/expandedprofile?address1={}&address2={}'
    conn = http.client.HTTPSConnection("api.gateway.attomdata.com")
    headers = { 'accept': "application/json", 'apikey': api_key, }
    add1 = add1.replace(' ', '%20')
    add1 = add1.replace(',', '%2C')
    add2 = add2.replace(' ', '%20')
    add2 = add2.replace(',', '%2C')
    conn.request("GET", link.format(add1,add2) , headers=headers)

    res = conn.getresponse()
    data = res.read()

    results = json.loads(data)

    if results['status']['msg'] != 'SuccessWithResult':
        session['status'] = False
    else:
        session['zip_code'] = int(results['property'][0]['address']['postal1'])
        session['address'] = results['property'][0]['address']['oneLine']
        session['owner'] = results['property'][0]['assessment']['owner']['owner1']['lastName']
        session['type'] = results['property'][0]['summary']['propClass']
        session['age'] = datetime.now().year - results['property'][0]['summary']['yearBuilt']

        session['building_size'] = results['property'][0]['building']['size']['bldgSize']
        session['num_rooms'] = results['property'][0]['building']['rooms']['roomsTotal']
        session['num_baths'] = results['property'][0]['building']['rooms']['bathsTotal']
        session['parking'] = results['property'][0]['building']['parking']['prkgSize']

        session['last_sale'] = results['property'][0]['sale']['saleTransDate'] + ' , $' + \
                    str(results['property'][0]['sale']['amount']['saleAmt'])
        session['total_market'] = results['property'][0]['assessment']['market']['mktTtlValue']
        session['land_market'] = results['property'][0]['assessment']['market']['mktLandValue']
        session['delinquincy'] = results['property'][0]['assessment']['delinquentyear']

        session['status'] = True

def search_zip(api_key, zip_code):

    conn2 = http.client.HTTPSConnection("api.gateway.attomdata.com")
    headers = {
    'accept': "application/json",
    'apikey': api_key, }

    if 'zip_code' in session:
        zip_code = int(session['zip_code'])

    link_zip = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/assessment/detail?postalcode={}'.format(zip_code)
    conn2.request("GET", link_zip, headers=headers)

    data2 = conn2.getresponse().read()
    results_zip = json.loads(data2)

    properties = results_zip['property']

    assessed_values_all = []
    value_per_unit_all = []
    age_all = []
    total_rooms_all = []

    if properties != []:

        for i in range(len(properties)):
            assessed_value = properties[i]['assessment']['assessed']['assdttlvalue']
            assessed_value_per_unit = properties[i]['assessment']['assessed']['assdttlpersizeunit']
            age = datetime.now().year - properties[i]['summary']['yearbuilt']
            total_rooms = properties[i]['building']['rooms']['roomsTotal']

            if total_rooms == 0 or age == 2020 or assessed_value == 0 or assessed_value_per_unit == 0:
                continue

            assessed_values_all.append(assessed_value)
            value_per_unit_all.append(assessed_value_per_unit)
            age_all.append(age)
            total_rooms_all.append(total_rooms)

        if len(assessed_values_all) > 1:
            session['zip_status'] = True
            session['average_assessed_value'] = round(np.mean(assessed_values_all),2)
            session['average_assessed_per_unit'] = round(np.mean(value_per_unit_all),2)
            session['average_age'] = round(np.mean(age_all),2)
            session['average_total_rooms'] = round(np.mean(total_rooms_all),2)
        else:
            session['zip_status'] = False
    else:
        session['zip_status'] = False

    cwd = os.getcwd()

    plt.figure()
    plt.scatter(age_all, assessed_values_all, color='blue')
    plt.title('Variation of Assessed Value with property age in the neighborhood')
    plt.xlabel('Age')
    plt.ylabel('Assessed Value')
    plt.savefig(cwd + '/static/images/age.png')

    plt.figure()
    plt.scatter(total_rooms_all, assessed_values_all, color='blue')
    plt.title('Variation of the Assessed Value with number of rooms')
    plt.xlabel('Number of rooms')
    plt.ylabel('Assessed Value')
    plt.savefig(cwd + '/static/images/rooms.png')
