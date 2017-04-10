#! /usr/bin/env python

import sys
import csv
import collections
import numpy as np

def GenerateFieldDescription(raw_data_filename):
  raw_data = csv.reader(open(raw_data_filename, "r"))
  english_description = next(raw_data)
  header = next(raw_data)
  field_description_file = csv.writer(open("field_desc_"+raw_data_filename, "w"))
  for i in range(len(english_description)):
    if english_description[i] != "":
      row = []
      row.append(header[i].lower())
      row.append(english_description[i])
      field_description_file.writerow(row)

def main():
  print ("Start program.")

  if len(sys.argv) < 2:
    print "Too few arguments"
    print "Please specify the raw data file with english descrption."
    sys.exit()

  raw_data_filename = sys.argv[1]

  GenerateFieldDescription(raw_data_filename)

  print ("End program.")
  return 0

if __name__ == '__main__':
  main() 
