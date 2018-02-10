from time import sleep
import os
import csv
from bs4 import BeautifulSoup
import mechanicalsoup
import re

data = []
with open('attendees.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      data.append(row)

results_file = csv.writer(open("results.csv", "a"))
if os.stat("results.csv").st_size == 0:
  results_file.writerow(["Name", "Company", "Country", "Confirmed Link", "Google Link", "Bing Link"])

counter = 0
match_counter = 0

google_browser = mechanicalsoup.StatefulBrowser()
bing_browser = mechanicalsoup.StatefulBrowser()

def calculate_percentage(match_counter, counter):
  print("Total: " + str(counter) + "     Matches: " + str(match_counter) + "     Percent Matched: " + str(int(match_counter/counter*100)) + "%")

def compare_links(person, google_link, bing_link, counter, match_counter):  
  new_link = ""
  if google_link is not None and bing_link is not None:
    google_name = google_link.split("/")[4].split("?")[0]
    bing_name = bing_link.split("/")[4].split("?")[0]
    if google_name == bing_name:
      new_link = google_link
      print(str(counter) + ": " + person["Name"] + " - Match!")
      match_counter = increment(match_counter)
    else:
      print(str(counter) + ": " + person["Name"] + " - :(")
  else:
    print(str(counter) + ": " + person["Name"] + " - :(")
  return new_link, match_counter

def add_result(results_file, name, title, company, country, final_link, google_link, bing_link):
  results_file.writerow([name, title, company, country, final_link, google_link, bing_link])

def increment(counter):
  counter += 1
  return counter

def get_google_link(browser, person):
  browser.open('https://www.google.com/')
  form = browser.select_form('form[name="f"]')
  search_string = "site:uk.linkedin.com/in/ " + person["Name"] + " " + person["Company"]
  browser["q"] = search_string
  form.choose_submit('btnG')
  page = browser.submit_selected()
  soup = BeautifulSoup(page.text, 'html.parser')
  link = soup.find('a', attrs={'href': re.compile("^\/url\?q=https:\/\/uk.linkedin.com\/in\/")})
  if link is not None:
    str_parts = re.split(r'[=&]+', link["href"])
    final_link = (str_parts[1])
  else:
    final_link = None
    print(final_link)
  return final_link

def get_bing_link(browser, person):
  browser.open('https://www.bing.com/')
  form = browser.select_form('form[action="/search"]')
  search_string = "site:linkedin.com/in/ " + person["Name"] + " " + person["Company"]
  browser["q"]   = search_string
  form.choose_submit('go')
  page = browser.submit_selected()
  soup = BeautifulSoup(page.text, 'html.parser')
  link = soup.find('a', attrs={'href': re.compile("linkedin.com\/in\/")})
  if link is not None:
    str_parts = re.split(r'[=&]+', link["href"])
    final_link = (str_parts[0]) 
  else:
    final_link = None
    print(final_link)
  return final_link

for person in data:
  counter = increment(counter)
  google_link = get_google_link(google_browser, person)
  bing_link = get_bing_link(bing_browser, person)
  final_link, match_counter = compare_links(person, google_link, bing_link, counter, match_counter)
  add_result(results_file, person["Name"], person["Title"], person["Company"], person["Country"], final_link, google_link, bing_link)
  calculate_percentage(match_counter, counter)
  sleep(46)