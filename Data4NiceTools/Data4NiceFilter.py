#! /usr/bin/env python

import numpy as np
import pandas as pd
import csv

def Filter(raw_data_file):
  # Get chosen fields
  readfile = csv.reader(open("chosenfields.csv", "r"))
  chosen_fields = []
  for row in readfile:
    chosen_fields.append(row[0])
  
  data = pd.read_csv(raw_data_file)
  for column in data.columns:
    if column == "STUDY_ID":
      continue

    if column not in chosen_fields:
      data.drop(column, axis=1, inplace=True)
      continue
    
    null_flags = data[column].isnull()
    remove = True
    for flag in null_flags:
      if flag == False:
        remove = False
        break
    if remove == True:
      data.drop(column, axis=1, inplace=True)

  data.fillna(0, inplace=True)
  data.to_csv("final_protect_data_for_clustering.csv")


def main():
  print ("Start program.")

  filename = "v1data4nice.csv"
  Filter(filename)

  print ("End program.")
  return 0

if __name__ == '__main__':
  main()
