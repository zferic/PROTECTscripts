#! /usr/bin/env python

import sys
import csv
from enum import Enum
import collections
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import BoundaryNorm

class DataType(Enum):
  TEXT = 0,
  RADIO = 1,
  NUMBER = 2

# According the data dictionary
field_index = 0
form_index = 1
type_index = 3
text_type_index = 7

field_dict = collections.OrderedDict()
def ParseDD(dd_filename, form_name):
  data_dict = csv.reader(open(dd_filename, "r"))
  for row in data_dict:
    if row[1] != form_name:
      continue;
    field_name = row[field_index]
    if row[type_index] == "radio":
      field_dict[field_name.upper()] = DataType.RADIO
    elif row[text_type_index] == "number" or row[text_type_index] == "integer":
      field_dict[field_name.upper()] = DataType.NUMBER
    else:
      field_dict[field_name.upper()] = DataType.TEXT

colors = []
def GenerateColorMap(raw_data_filename):
  raw_data = csv.reader(open(raw_data_filename, "r"))
  num_skipped_column = 2
  num_col = len(next(raw_data)) - num_skipped_column
  header = next(raw_data)
  num_row = 0
  for row in raw_data:
    num_row += 1
    for i in range(len(row)):
      if header[i] == "STUDY_ID" or header[i] == "PPTERM":
        continue

      if row[i] == "":
        colors.append(0)
      elif field_dict[header[i]] == DataType.TEXT:
        colors.append(1)
      elif field_dict[header[i]] == DataType.RADIO:
        colors.append(2)
      elif field_dict[header[i]] == DataType.NUMBER:
        colors.append(3)
        print "I am here"
  color_array = np.array(colors)
  color_array.resize(num_row, num_col)

  cmap = ListedColormap(['black', 'red', 'blue'])
  plt.pcolormesh(color_array, cmap=cmap)
  plt.show()
  

def main():
  print ("Start program.")

  if len(sys.argv) < 4:
    print "Too few arguments"
    print "Please specify the data dictionary file, form name, and raw data file."
    sys.exit()

  dd_filename = sys.argv[1]
  form_name = sys.argv[2]
  raw_data_filename = sys.argv[3]
  
  ParseDD(dd_filename, form_name)

  GenerateColorMap(raw_data_filename)

  print ("End program.")
  return 0

if __name__ == '__main__':
  main() 