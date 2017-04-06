#! /usr/bin/env python

import numpy as np
import pandas as pd
import sys
import csv

def Filter(raw_data_file):
  # Get chosen fields
  readfile = csv.reader(open("chosenfields.csv", "r"))
  chosen_fields = []
  for row in readfile:
    chosen_fields.append(row[0])
  
  data = pd.read_csv(raw_data_file)
  print "The column number of raw data BEFORE filtered is: " + str(len(data.columns))
  for column in data.columns:
    if column == "STUDY_ID" or column == "PPTERM":
      continue

    # Remove unchosen fields
    if column not in chosen_fields:
      data.drop(column, axis=1, inplace=True)
      continue
    
    null_flags = data[column].isnull()
    remove = True
    null_count = 0
    for flag in null_flags:
      if flag == False:
        remove = False
      if flag == True:
        null_count += 1

    proportion = float(null_count) / float(len(null_flags))
    if remove == True or proportion > 0.5:
      data.drop(column, axis=1, inplace=True)

  print "The column number of raw data AFTER filtered is: " + str(len(data.columns))

  #data.fillna(0, inplace=True)
  data.to_csv("filtered_" + raw_data_file)


def main():
  print ("Start program.")

  if len(sys.argv) < 2:
    print "Too few arguments"
    print "Please specify the csv file."
    sys.exit()

  filename = sys.argv[1]
  Filter(filename)

  print ("End program.")
  return 0

if __name__ == '__main__':
  main()
