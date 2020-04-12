import sys
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import requests
import urllib.parse
from urllib.parse import urlparse
import csv
import proxy_ditto
import souper


"""
This script scrapes apartment.com data for apartment prices,
into a csv file.

It does thew following:
1. Searches for the apartment on google
2. Gets the url for the apartment.com entry for the apartment
3. Parses through that page for bedroom, bathroom, rent data
4. Collects all the data, outputs into a csv

The first two steps are done because the URL changes (there is an end-hash)
for each apartment, every day. So hard-coding the apartment.com entry url
would not take into account the time-varying rent values.

User Input:
apartment list: list of apartments for Google search:
"""
region_apt_dict = {'Hardin Valley': ['Enlcave at Hardin Valley',
                                     'Greystone Summit',
                                     'Greystone Vista'],
                   'Turkey Creek': ['Tapestry Turkey Creek',
                                    'Overlook at Farragut'],
                   'Downtown Knoxville': ['One Riverwalk Knoxville Apartment',
                                          'Maplehurst Park Knoxville Apartment',
                                          'Marble Alley Lofts'],
                   'UTK Campus': ['Barclay House Knoxville',
                                  'The Slate at 901',
                                  'TENN Apartments'],
                   'Oak Ridge': ['Centennial Village Apartments',
                                'Tara Hills Apartments',
                                'Bristol Park at Oak Ridge']}

apt_list = []
for key, val in region_apt_dict.items():
    apt_list.extend(val)
print(apt_list)

def google_search(query):
    url = 'https://www.google.com/search?client=ubuntu&channel=fs&q={}&ie=utf-8&oe=utf-8'.format(query)
    try:
        html = requests.get(url)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
    except:
        raise ValueError('Cannot get URL')
    return soup


def extract_url_from_google_html(element):
    i1 = element.index('https')
    i2 = element.index('&amp')
    return element[i1:i2]


def get_url(apt):
    soup = google_search(apt)
    a = soup.find_all('a')
    for i in a:
        if 'www.apartments.com' in i.text:
            return extract_url_from_google_html(str(i))

    # if nothing is found
    raise ValueError('There is no listing for apartments.com for this apartment:\n%s'%apt)


def clean_rent_string(num_string):
    """ Cleans the number string, averages price range if it's a range"""
    if num_string == 'Call for Rent':
        return 0
    num_string = num_string.replace('$', '').replace(',','').strip()
    if '/ Person' in num_string:
        per_person = clean_rent_string(num_string[:num_string.index('/')])
        return str(per_person) + 'pp'
    if '-' in num_string:
        x = num_string.replace('-', '').split()
        x = [float(q) for q in x]
        return sum(x)/2
    return float(num_string)

def clean_bed_bath_string(num_string):
    if 'studio' in num_string.lower():
        return 1
    num_string = num_string.lower()
    for i in ['brs', 'br', 'bas', 'ba', 'beds', 'bed', 'baths', 'bath']:
        num_string = num_string.replace(i, '').strip()
    if '½' in num_string:
        return float(num_string[:num_string.index('½')]) + 0.5
    return int(num_string)


def read_url(url):
    print('Reading url:')
    print(url)
    print('-------------------')
    soup = souper.get_soup(url)
    beds, baths = get_beds_bathrooms(soup)
    rents = get_rents(soup)

    # array of [bed, bath, rent]
    arr = []
    for indx, val in enumerate(beds):
        entry = [beds[indx], baths[indx], rents[indx]]
        if entry not in arr:
            if 'pp' in str(entry[2]):
                entry[2] = float(entry[2].replace('pp', '')) * entry[0]
            arr.append(entry)
    print('Beds\tBaths\tRent')
    for i in arr:
        print('%s\t%s\t%s' %(i[0], i[1], i[2]))
    return arr


def get_beds_bathrooms(soup):
    beds = []
    baths = []
    bed_elements = soup.findAll('td', class_='beds')
    for i in bed_elements:
        beds.append(clean_bed_bath_string(i.findAll('span', class_='shortText')[0].text.strip()))

    bath_elements = soup.findAll('td', class_='baths')
    for i in bath_elements:
        baths.append(clean_bed_bath_string(i.findAll('span', class_='shortText')[0].text.strip()))

    return beds, baths


def get_rents(soup):
    rent = []
    x = soup.findAll('td', class_='rent')
    for i in x:
        rent.append(clean_rent_string(i.text.strip()))
    return rent


def price_dict_to_csv(price_dict, url_dict):
    csv_dict_list = []
    for key, val in price_dict.items():
        reg = [k for k, v in region_apt_dict.items() if key in v]
        url = url_dict[key]
        for i in ['Knoxville', 'Apartments', 'Apartment']:
            key = key.replace(i, '')
        for entry in val:
            csv_dict_list.append({'Region': reg[0], 'Apartment': key, 'Beds': entry[0], 'Baths': entry[1], 'Rent': entry[2], 'URL': url})
    return csv_dict_list


def main():
    today = datetime.date(datetime.now())
    url_dict = {}
    print('Today is: ', today)
    price_dict = {k:{} for k in apt_list}
    for apt in apt_list:
        try:
            url = get_url(apt)
            url_dict[apt] = url
            price_dict[apt] = read_url(url)
        except Exception as e:
            print('Apartment %s is not available or there is something wrong' %apt)
            print('Error:\n', e)
    csv_list = price_dict_to_csv(price_dict, url_dict)
    with open('./data/%s.csv' %today, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_list[0].keys())
        writer.writeheader()
        for data in csv_list:
            writer.writerow(data)

if __name__ == '__main__':
    main()