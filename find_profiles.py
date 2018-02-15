'''
This program takes the CSV output file from twitter_list.py
and uses Google and Bing to find the LinkedIn profile for 
the Twitter users in the list that we parsed. We use two search 
engines so we can cross-reference the top result and see if they 
match. In our tests, if both results are the same, there is a 
98% chance that it is the person we are looking for! If the two 
results do not match, the program saves both results to a new 
CSV file so we can see at a glance if one of them looks correct.
'''
# Imports the sleep function from Python's time module. This will 
# allow us to pause the program for a specified period of time. 
from time import sleep

# Imports the OS module, which will give us access to the operating system 
# and to manipulate files external to this program.
import os

# Imports the CSV module, which will allow us to read and write 
# Comma Separated Value files (which can be opened in spreadsheets like 
# Excel), which we will use here to store information on the people we will find.
import csv

# Imports the BeautifulSoup library, which parses HTML so that we are able to 
# extract data from it. The documentation is here:
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup

# Imports the MechanicalSoup library, which automates website interactions 
# such as submitting forms and clicking links. For more information:
# https://github.com/MechanicalSoup/MechanicalSoup
import mechanicalsoup

# Imports the Regular Expressions module, which will let us do more complicated 
# pattern matching on our search results.
import re

# Creates a list of additional search strings that we will 
# use to describe the people we are looking for. We are putting them in a 
# list so that we have them in one location that is easy to edit, and we 
# can use as many or as few terms as we wish without having to update the 
# program in multiple places. 
search_terms = ['google', 'designer']
# Turns the list of search terms into a string, separates each term 
# with a space, and stores it in a variable that we can use later.
formatted_search_terms = ' '.join(search_terms)

# Initializes an empty list.
data = []

# Opens the CSV that we created with twitter_list.py in read-only mode, 
# assigns it to variable 'f', and then closes it when we are done.
with open('group_members.csv', 'r') as f:

# Uses the CSV module to import the contents of the file into a 
# dictionary.
    reader = csv.DictReader(f)

# Row by row, adds the dictionary to the list that we initialized earlier.
# The variable data will be a list of key/value pairs wih info on each person.
    for row in reader:
      data.append(row)

# Uses the CSV module to open our output file (or create it if it does 
# not exist already). The 'a' option opens it in append mode, so if the 
# file already exists, we will add new data to it and not overwrite the 
# existing data.
results_file = csv.writer(open('results.csv', 'a'))

# Uses the os module to check if the size of our output file is zero,
# which would mean that it is empty. If it is empty, it will write a 
# header row in the file.
if os.stat('results.csv').st_size == 0:
  results_file.writerow(['Name', 'Location', 'Confirmed Link', 'Google Link', 'Bing Link'])

# Initializes two variables so we can keep track of how many names we have
# checked and how many matches we have found.
counter = 0
match_counter = 0

# Creates two virtual browsers using Mechanical Soup. We will use one for 
# Google, and one for Bing.
google_browser = mechanicalsoup.StatefulBrowser()
bing_browser = mechanicalsoup.StatefulBrowser()

'''
Everything to this point is setup; opening the input file, preparing the 
output file, creating virtual browsers, etc. What comes next is the meat of 
the program - functions that will handle the searching and comparing of 
results.
'''

# This function takes a virtual browser and our data about a person as input, 
# and returns the first matching result for that person on LinkedIn, using 
# Google search.
def get_google_link(browser, person):
# Opens the Google home page in our virtual browser.
  browser.open('https://www.google.com/')
# On the Google home page, the HTML code for the search form looks like this:
# <form class="tsf" action="/search" style="overflow:visible" id="tsf" method="GET" name="f" onsubmit="return q.value!=''" role="search">
# Note that the name of the form is "f" in the code. So we instruct our 
# virtual browser to get the form "f" and assign it to the variable "form".
  form = browser.select_form('form[name="f"]')
# We prepare our search string. It will combine a site-specific search on 
# linkedin, the person's name and location that we got from Twitter, and 
# the additional search terms that we formatted earlier. To make the search 
# cleaner, we are only using the part of the location before any commas, so
# if we have a US location in the format "city, state", we only search using 
# the city.
  search_string = 'site:linkedin.com/in/ ' + person['Name'] + ' ' + person['Location'].split(',')[0] + ' ' + formatted_search_terms
# On the Google home page, the HTML code for the part of the search form that 
# is the input field where you type your query looks like this:
# <input class="lst lst-tbb sbibps" id="lst-ib" maxlength="2048" name="q" autocomplete="off" title="Search" type="text" value="" aria-label="Search">
# We instruct our virtual browser to fill that input field with our search string.
  browser['q'] = search_string
# On the Google home page, the HTML code for the part of the search form that 
# is the submit button looks like this:
# <button class="sbico-c" value="Search" aria-label="Google Search" id="_fZl" name="btnG" type="submit">
# We tell our virtual browser that this button should be used to submit the form.
  form.choose_submit('btnG')
# Now that we have filled in the search field and identified how to submit the
# form, we actually submit it, and store the results page in a variable.
  page = browser.submit_selected()
# We use BeautifulSoup to parse the HTML that we just received.
  soup = BeautifulSoup(page.text, 'html.parser')
# We search the HTML that we just parsed for a link ('a') with a URL ('href') that 
# begins with '/url?q=https://www.linkedin.com/in/'
  link = soup.find('a', attrs={'href': re.compile("^\/url\?q=https:\/\/www.linkedin.com\/in\/")})
# If we find a link that matches...
  if link is not None:
# ...we split the link every time there is an '=' or '&' symbol in it.
    str_parts = re.split(r'[=&]+', link['href'])
# We know that the link starts with '/url?q=', so we want the second 
# part of it, which contains the piece that is important to us.
    final_link = (str_parts[1])
# prints the link to the console so we can see in real time what is happening.
    print ('Google Link:' + final_link)
# if we can't find any matching links...
  else:
# ...we assign a null value to our final_link variable.
    final_link = None
# Regardless of whether we found our link or not, we return the value for 
# final_link at the end of the function.
  return final_link

# This function takes a virtual browser and our data about a person as input, 
# and returns the first matching result for that person on LinkedIn, using 
# Bing search.
def get_bing_link(browser, person):
# Opens the Bing home page in our virtual browser.
  browser.open('https://www.bing.com/')
# There is only one form on the Bing home page, and unlike Google it does 
# not have a name attribute. So we instruct our virtual browser to get the 
# first form on the page and assign it to the variable "form".
  form = browser.select_form(nr=0)
# We prepare our search string. It will combine a site-specific search on 
# linkedin, the person's name and location that we got from Twitter, and 
# the additional search terms that we formatted earlier. To make the search 
# cleaner, we are only using the part of the location before any commas, so
# if we have a US location in the format "city, state", we only search using 
# the city.
  search_string = 'site:linkedin.com/in/ ' + person['Name'] + ' ' + person['Location'].split(',')[0] + ' ' + formatted_search_terms
# On the Bing home page, the HTML code for the part of the search form that 
# is the input field where you type your query looks like this:
# <input autocapitalize="off" autocomplete="off" autocorrect="off" class="b_searchbox" id="sb_form_q" maxlength="1000" name="q" placeholder="Enter your search" spellcheck="false" title="Enter your search term" type="search" value=""/>
# We instruct our virtual browser to fill that input field with our search string.
  browser['q'] = search_string
# On the Bing home page, the HTML code for the part of the search form that 
# is the submit button looks like this:
# <input class="b_searchboxSubmit" id="sb_form_go" name="go" tabindex="0" title="Search" type="submit"/>
# We tell our virtual browser that this button should be used to submit the form.
  form.choose_submit('go')
# Now that we have filled in the search field and identified how to submit the
# form, we actually submit it, and store the results page in a variable.
  page = browser.submit_selected()
# We use BeautifulSoup to parse the HTML that we just received.
  soup = BeautifulSoup(page.text, 'html.parser')
# We search the HTML that we just parsed for a link ('a') with a URL ('href') that 
# includes 'linkedin.com/in/'
  link = soup.find('a', attrs={'href': re.compile('linkedin.com\/in\/')})
# If we find a link that matches...
  if link is not None:
# ...we split the link every time there is an '=' or '&' symbol in it.
    str_parts = re.split(r'[=&]+', link['href'])
# After looking at the structure of the link that we get back, we want the first 
# part of it, which contains the piece that is important to us.
    final_link = (str_parts[0]) 
# prints the link to the console so we can see in real time what is happening.
    print ("Bing Link:" + final_link)
# if we can't find any matching links...
  else:
# ...we assign a null value to our final_link variable.
    final_link = None
# Regardless of whether we found our link or not, we return the value for 
# final_link at the end of the function.
  return final_link

# This function compares the two links and determines if they match.
def compare_links(person, google_link, bing_link, counter, match_counter):  
# Initializes a variable called new_link with an empty string. 
  new_link = ""
# Checks to make sure that we were able to find values for both of our 
# links. If we try the next couple of lines on a null variable, we will 
# get errors, and already know that we know that we don't want to confirm 
# identical links if one of them does not exist.
  if google_link is not None and bing_link is not None:
# We split the Google and Bing links every time there is a forward slash. 
# We want the part that comes after the 'https://www.linkedin.com/in/', 
# so we select the fifth string that is created when we split it. Then we
# split that string again every time there is a question mark, which 
# LinkedIn uses sometimes to add additional information at the end of the 
# URL. We take the first string from that split, which is the unique 
# identifier for the profile.
    google_name = google_link.split("/")[4].split("?")[0]
    bing_name = bing_link.split("/")[4].split("?")[0]
# If we have a match...
    if google_name == bing_name:
# ...we change our new_link variable to be the same as one of the matching 
# links.
      new_link = google_link
# Prints a notification to the console so we can see in real time what is happening.
      print(str(counter) + ": " + person["Name"] + " - Match!")
# Since we have a match, we call the function that increments our match_counter.
      match_counter = increment(match_counter)
# This else condition applies if the two URLs do not match.
    else:
# Prints a notification to the console so we can see in real time what is happening.
      print(str(counter) + ": " + person["Name"] + " - :(")
# This else condition applies if we found one of the URLS to be null.
  else:
# Prints a notification to the console so we can see in real time what is happening.
    print(str(counter) + ": " + person["Name"] + " - :(")
  return new_link, match_counter

# This function writes all of the data for a given person into a new row in our 
# output file.
def add_result(results_file, name, location, final_link, google_link, bing_link):
  results_file.writerow([name, location, final_link, google_link, bing_link])

# This function simply take an integer and adds one to it. It's useful for keeping 
# track of how many times we have looped through the program.
def increment(counter):
  counter += 1
  return counter

# This function prints the stats for the program in our terminal, so we can 
# see the progress in real time.
def print_stats(match_counter, counter):
  print('Total: ' + str(counter) + '     Matches: ' + str(match_counter) + '     Percent Matched: ' + str(int(match_counter/counter*100)) + '%')

'''
Now that we have all of our functions set up, we are going to actually call 
them sequentially, once for every person in our dataset.
'''

for person in data:
# First we increment our counter, to keep track of how many people we have looped through.
  counter = increment(counte.r)
# We get our Google Link
  google_link = get_google_link(google_browser, person)
# We get our Bing Link.
  bing_link = get_bing_link(bing_browser, person)
# We compare the links and get back both a link (if there is a match), and the total 
# number of matches that we have received so far.
  final_link, match_counter = compare_links(person, google_link, bing_link, counter, match_counter)
# We write the name, location, matched link, Google link, and Bing link to the output file.
# Why all three links? Because even if there is no match, one of the search engines is often able 
# to find the right person, and being able to just click the links is a big time saver.
  add_result(results_file, person["Name"], person["Location"], final_link, google_link, bing_link)
# We print our current stats to the console to keep track of our overall progress in real time.
  print_stats(match_counter, counter)
# We pause the program for 46 seconds between each loop. We do this so that we are not hammering 
# the Google and Bing servers over and over, which will get us flagged as a bot and cut off.
  sleep(46)