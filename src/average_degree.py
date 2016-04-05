#!/usr/bin/env python

import sys
import json
import itertools
import collections
import time

if len(sys.argv) < 2:
  print('Usage: ./average_degree.py <tweet_input_path>')
  sys.exit()
tweet_input_path = sys.argv[1]

data = []
twitter_graph = {}
start_timestamp = {}
max_timestamp = {}

def parseJSON():
  with open(tweet_input_path) as data_file:
    for tweet in data_file:
      full_data = json.loads(tweet)
      parsed_data = {}
      if 'created_at' in full_data.keys():
        parsed_data['created_at'] = full_data['created_at']
        tags = []
        for tag in full_data['entities']['hashtags']:
          tags.append(tag['text']);
        parsed_data['hashtags'] = tags
        data.append(parsed_data)

def addToGraph(hashtags):
  for tag in hashtags:
    if tag not in twitter_graph.keys():
      twitter_graph[tag] = set()
  for pair in list(itertools.combinations(hashtags, 2)):
    twitter_graph[pair[0]].add(pair[1])
    twitter_graph[pair[1]].add(pair[0])

def calculateDegree():
  if len(twitter_graph) == 0: 
    return format(0, '.2f')
  sum_edges = 0
  for node, edges in twitter_graph.iteritems():
    sum_edges += len(edges)
  return format(float(sum_edges) / len(twitter_graph), '.2f')

def deleteToGraph(hashtags):
  for pair in list(itertools.combinations(hashtags, 2)):
    if pair[0] in twitter_graph.keys() and pair[1] in twitter_graph[pair[0]]:
      twitter_graph[pair[0]].remove(pair[1])
    if pair[1] in twitter_graph.keys() and pair[0] in twitter_graph[pair[1]]:
      twitter_graph[pair[1]].remove(pair[0])

def convertToTime(created_at):
  return time.mktime(time.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y"))

def processGraph():
  global data
  start_timestamp['time'] = convertToTime(data[0]['created_at'])
  start_timestamp['index'] = 0
  max_timestamp['time'] = start_timestamp['time']
  max_timestamp['index'] = 0

  # Start Debugging
  # data = data[0:100]
  # End Debugging 

  for parsed_tweet in data:
    if len(parsed_tweet['hashtags']) != 0:
      t = convertToTime(parsed_tweet['created_at'])
      if t >= max_timestamp['time']:
        if t-start_timestamp['time'] <= 60:
          addToGraph(parsed_tweet['hashtags'])
        else:
          deleteToGraph(data[start_timestamp['index']]['hashtags'])
          start_timestamp['index'] += 1
          start_timestamp['time'] = convertToTime(data[start_timestamp['index']]['created_at'])
          while t-start_timestamp['time'] > 60:
            deleteToGraph(data[start_timestamp['index']]['hashtags'])
            start_timestamp['index'] += 1
            start_timestamp['time'] = convertToTime(data[start_timestamp['index']]['created_at'])
          addToGraph(parsed_tweet['hashtags'])
        max_timestamp['time'] = t;
      else:
        if max_timestamp['time']-t <= 60:
          addToGraph(parsed_tweet['hashtags'])
    print calculateDegree()

parseJSON()
processGraph()

