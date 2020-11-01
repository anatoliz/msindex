import csv
import sys
import urllib.request
import xml.etree.ElementTree as ET
import datetime

dic = {}
i = 0
recentdate = ""
lastnetworth = "" 
now = datetime.date.today()

if sys.argv[1] == "max":
	filename = "<INSERT CSV OUTPUT FILE NAME>"
	inputdate = datetime.date(1940, 1, 1)
	spfrequency = "q"

if sys.argv[1] == "fiveyear":
	filename = "<INSERT CSV OUTPUT FILE NAME>"
	inputdate = datetime.date(now.year - 5, now.month, now.day)
	spfrequency = "m"

if sys.argv[1] == "oneyear":
	filename = "<INSERT CSV OUTPUT FILE NAME>"
	inputdate = datetime.date(now.year - 1, now.month, now.day)
	spfrequency = "w"

contents = urllib.request.urlopen("https://api.stlouisfed.org/fred/series/observations?series_id=NCBCEL&api_key=<INSERT API KEY HERE>").read()
with open('/var/www/msindex.net/chart/data/equity.xml', 'wb') as f:
	f.write(contents)

contents = urllib.request.urlopen("https://api.stlouisfed.org/fred/series/observations?series_id=TNWMVBSNNCB&api_key=<INSERT API KEY HERE>").read()
with open('/var/www/msindex.net/chart/data/networth.xml', 'wb') as f:
	f.write(contents)

contents = urllib.request.urlopen("https://api.stlouisfed.org/fred/series/observations?series_id=SP500&api_key=<INSERT API KEY HERE>&frequency=" + spfrequency).read()
with open('/var/www/msindex.net/chart/data/sp.xml', 'wb') as f:
	f.write(contents)

contents = urllib.request.urlopen("https://api.stlouisfed.org/fred/series/observations?series_id=SP500&api_key=<INSERT API KEY HERE>&frequency=d").read()
with open('/var/www/msindex.net/chart/data/dailysp.xml', 'wb') as f:
	f.write(contents)

tree = ET.parse('/var/www/msindex.net/chart/data/equity.xml')
root = tree.getroot()
for item in root.findall('./observation'):
  date = item.get('date')
  value = item.get('value')
  if value != ".":
    dic[date] = float(value)
    recentdate = date

tree = ET.parse('/var/www/msindex.net/chart/data/networth.xml')
root = tree.getroot()
for item in root.findall('./observation'):
  date = item.get('date')
  value = item.get('value')
  if value !=  ".":
    dic[date] = dic[date] / float(value)
    lastnetworth = float(value)

tree = ET.parse('/var/www/msindex.net/chart/data/dailysp.xml')
root = tree.getroot()
for item in root.findall('./observation'):
  date = item.get('date')
  value = item.get('value')
dic[date] = (10 * float(value)) / lastnetworth
print(dic[date])
splitdate = date.split("-")
lastbusinessdate = datetime.date(int(splitdate[0]), int(splitdate[1]), int(splitdate[2]))

tree = ET.parse('/var/www/msindex.net/chart/data/sp.xml')
root = tree.getroot()
for item in root.findall('./observation'):
  date = item.get('date')
  value = item.get('value')
  splitdate = date.split("-")
  formaldate = datetime.date(int(splitdate[0]), int(splitdate[1]), int(splitdate[2]))

  if value != "." and date > recentdate and lastbusinessdate > formaldate:
    dic[date] = (10 * float(value)) / lastnetworth

with open(filename, 'w', newline='') as csvfile:
    fieldnames = ['year', 'month', 'day', 'value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for date, value in sorted(dic.items(), key=lambda item: item[0]):
        splitdate = date.split("-")
        currentdate = datetime.date(int(splitdate[0]), int(splitdate[1]), int(splitdate[2]))
        if currentdate >= inputdate:
            writer.writerow({'year': splitdate[0], 'month': splitdate[1], 'day':splitdate[2], 'value': value})
