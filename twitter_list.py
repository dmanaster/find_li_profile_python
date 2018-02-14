import os
import csv
import re
import tweepy
from twitter_keys import Key


# Here are some good sample Twitter lists:
# Designers who work at Google: https://twitter.com/addyosmani/lists/google-designers
# Ruby Developers who work in Sa Diego: https://twitter.com/sdruby/lists/members

results_file = csv.writer(open("group_members.csv", "a"))
if os.stat("group_members.csv").st_size == 0:
  results_file.writerow(["Name", "Location"])

auth = tweepy.OAuthHandler(Key.consumerKey, Key.consumerSecret)
auth.set_access_token(Key.accessToken, Key.accessTokenSecret)

api = tweepy.API(auth)

for member in tweepy.Cursor(api.list_members, 'addyosmani', 'google-designers').items():
  memberName = member.name
  memberLocation = member.location
  # if (' ' in memberName and (re.search('san diego', memberLocation, re.IGNORECASE) or re.search(', CA', memberLocation, re.IGNORECASE))):
  if ' ' in memberName:
    results_file.writerow([memberName, memberLocation])
    print("Name: " + memberName + "        Location: " + memberLocation)