# Saahiti Jasti
# Lab 3
# lab3back.py produces a JSON file and an SQL database file for Covid19 data
 
import requests
from bs4 import BeautifulSoup
import re
import pickle
import json
import sqlite3

page = requests.get('https://www.worldometers.info/coronavirus/')
soup = BeautifulSoup(page.content, "lxml")
table = soup.find(id='main_table_countries_today')
    
tableRows = table.find_all('tr')
tableData = []

for tr in tableRows:
    td = tr.find_all('td')
    row = []
    for field in td:
        if field.text.strip() == '':
            row.append(None) #Equivalent to no data
        else:
            try:
                row.append(int(field.text.strip().replace(',', '')))
            except ValueError:
                row.append(field.text.strip())
    tableData.append(row)
    
tableData = tableData[1:] # Remove the empty list at first index and continent data

#Remove any rows where the country field does not have data
covidData = [country for country in tableData if country[1] != 'Total:' and country[14] != None]

with open('covidData.json', 'w') as fh:
    json.dump(covidData, fh, indent=3)

with open('covidData.json', 'r') as fh:
    covidData = json.load(fh)

COLUMNS = ["TotalCases", "NewCases", "TotalDeaths", "NewDeaths", "TotalRecovered", "ActiveCases", "SeriousCritical",
           "CasesPer1M", "DeathsPer1M", "TotalTests", "TestsPer1M", "Population"]

conn = sqlite3.connect('covid19.db')
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS Covid19")

cur.execute('''CREATE TABLE Covid19 (CountryNumber   INTEGER)''')
cur.execute('''ALTER TABLE Covid19 ADD COLUMN '{}' TEXT'''.format('Country'))

for col in COLUMNS:
    cur.execute('''ALTER TABLE Covid19 ADD COLUMN '{}' INTEGER'''.format(col))

cur.execute('''ALTER TABLE Covid19 ADD COLUMN '{}' TEXT'''.format('Continent'))
    
for row in covidData:
    cur.execute('''INSERT INTO Covid19 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (row))

conn.commit()
conn.close()