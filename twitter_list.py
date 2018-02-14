# imports the OS module, which will give us access to the operating system and to manipulate files external to this program.
import os
# imports the CSV module, which will allow us to read and write Comma Separated Value files, which we will use here to store information on the people we will find.
import csv
# imports the tweepy module, which is a wrapper that makes the Twitter API more easy to use from a Python program.
import tweepy
# Twitter API keys are confidential, like passwords. If someone else gets a hold of them, they can use your API access. I stored my Twitter API keys in a separate file called twitter_keys.py in a Class called "Key". This line imports those variables so I can use them in this file without exposing them to anyone viewing this file. 
from twitter_keys import Key

# Here are some sample Twitter lists that we can parse to find specialized professionals:
# Designers who work at Google: https://twitter.com/addyosmani/lists/google-designers
# Ruby Developers who work in San Diego: https://twitter.com/sdruby/lists/members
# Engineers with degrees from a French Tech School: https://twitter.com/Altimor/lists/while42-ultimate

list_owner = 'addyosmani'
list_name = 'google-designers'

results_file = csv.writer(open('group_members.csv', 'a'))
if os.stat("group_members.csv").st_size == 0:
  results_file.writerow(["Name", "Location"])

auth = tweepy.OAuthHandler(Key.consumerKey, Key.consumerSecret)
auth.set_access_token(Key.accessToken, Key.accessTokenSecret)

api = tweepy.API(auth)

for member in tweepy.Cursor(api.list_members, list_owner, list_name).items():
  memberName = member.name
  memberLocation = member.location
  if ' ' in memberName:
    results_file.writerow([memberName, memberLocation])
    print("Name: " + memberName + "        Location: " + memberLocation)