# This program uses the Twitter API to export all the names and locations of the members 
# of a Twitter List to a file with comma separated values.

# Here are some sample Twitter Lists that we can parse to find specialized professionals:
# https://twitter.com/addyosmani/lists/google-designers <-- Designers who work at Google 
# https://twitter.com/sdruby/lists/members <-- Ruby Developers who work in San Diego 
# https://twitter.com/Altimor/lists/while42-ultimate <-- Engineers with degrees from a French Tech School

# Imports the OS module, which will give us access to the operating system 
# and to manipulate files external to this program.
import os

# imports the CSV module, which will allow us to read and write 
# Comma Separated Value files (which can be opened in spreadsheets like 
# Excel), which we will use here to store information on the people we will find.
import csv

# imports the tweepy module, which is a wrapper that makes the Twitter 
# API more easy to use from a Python program.
# The documentation for Tweepy is at http://tweepy.readthedocs.io/en/v3.5.0/
import tweepy

# Twitter API keys are confidential, like passwords. If someone else 
# gets a hold of them, they can use your API access. I stored my Twitter 
# API keys in a separate file called twitter_keys.py in a Class called "Key". 
# This line imports those variables so I can use them in this file without 
# exposing them to anyone viewing this file. For the first time out, it will 
# probably be easier to just include your keys in this program. I will point 
# out where in comments below.
# You can create your own API keys at https://apps.twitter.com/app/new
from twitter_keys import Key

# This example uses the twitter list at 
# https://twitter.com/addyosmani/lists/google-designers
# We will assign the owner and name of the list to variables to make it 
# easier to change later when we want to use the program on a different list.
list_owner = 'addyosmani'
list_name = 'google-designers'

# Uses the csv module that we imported earlier to open a file named 
# twitter_list_members.csv. The 'w' flag means that we will open the file 
# in write mode. If the file does not already exist, it will 
# create it. If it does exist, it will overwrite it. 
results_file = csv.writer(open('twitter_list_members.csv', 'w'))
# Writes a header row in our CSV file.
results_file.writerow(["Name", "Location"])

# These three lines authenticate our Twitter API keys (think of them like passwords), 
# which we will use in order to enable tweepy to use the API. I stored my Twitter 
# API keys in a separate file called twitter_keys.py in a Class called "Key". 
# The next three lines import those variables so I can use them in this file without 
# exposing them to anyone viewing this file. For the first time out, it will 
# probably be easier to just include your keys in this program in place of the 
# four keys in the next two lines.
auth = tweepy.OAuthHandler(Key.consumer_key, Key.consumer_secret)
auth.set_access_token(Key.access_token, Key.access_token_secret)
api = tweepy.API(auth)

# This line uses tweepy to get the members of the list with the name and owner 
# that we specified in the variables list_owner and list_name earlier.
# http://tweepy.readthedocs.io/en/v3.5.0/api.html#API.list_members
# But Twitter limits API responses to 20 items, and we might have more than that. 
# Tweepy uses cursoring to paginate the responses and get all of the responses, 
# 20 at a time. http://tweepy.readthedocs.io/en/v3.5.0/cursor_tutorial.html
# It then iterates the next five lines for every member of the list that 
# Twitter sends.
for member in tweepy.Cursor(api.list_members, list_owner, list_name).items():

# Uses the Twitter API to get the name of each Twitter user, and then make 
# sure that the characters are in a format that we can use. Note that the 
# "name" here is set by each person themselves. It's often their real 
# name, but does not have to be.
  member_name = member.name.encode('utf-8')

# Uses the Twitter API to get the location of each Twitter user and then make 
# sure that the characters are in a format that we can use. Note that the 
# "location" here is set by each person themselves. It's often their real 
# location, but does not have to be.
  member_location = member.location.encode('utf-8')

# The next line is to help reduce the number of low quality results that we get.
# It checks that the string contains only letters and spaces, and that there is 
# at least one space in the string.
  if all(char.isalpha() or char.isspace() for char in member_name) and (' ' in member_name):

# If the conditions in the last line were met, we write the person's name and 
# location to our CSV file.
    results_file.writerow([member_name, member_location])