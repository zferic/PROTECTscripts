#! /usr/bin/env python

import sys
import re
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
choice_index = 5
text_type_index = 7

field_dict = collections.OrderedDict()
def ParseDD(dd_filename, form_name):
  data_dict = csv.reader(open(dd_filename, "r"))
  for row in data_dict:
    if row[1] != form_name:
      continue;
    field_name = row[field_index]
    if row[type_index] == "radio" or row[type_index] == 'dropdown':
      field_dict[field_name.upper()] = DataType.RADIO
    elif row[text_type_index] == "number" or row[text_type_index] == "integer":
      field_dict[field_name.upper()] = DataType.NUMBER
    elif row[type_index] == 'checkbox':
      field_choices = row[choice_index]
      sepintlist = field_choices.split('|')
      for item in sepintlist:
        found_int = re.search("\d+", item)
        field_dict[field_name.upper()+"__"+str(found_int.group())] = DataType.RADIO
    else:
      field_dict[field_name.upper()] = DataType.TEXT

colors = []
def GenerateColorMap(raw_data_filename):
  raw_data = csv.reader(open(raw_data_filename, "r"))
  num_skipped_column = 2
  header = next(raw_data)
  num_col = len(header) - num_skipped_column
  num_row = 0
  for row in raw_data:
    num_row += 1
    for i in range(len(row)):
      if header[i] == "STUDY_ID" or header[i] == "PPTERM":
        continue
      if header[i] in field_dict:
        if row[i] == "":
          colors.append(0)
        elif field_dict[header[i]] == DataType.TEXT:
          colors.append(1)
        elif field_dict[header[i]] == DataType.RADIO:
          colors.append(2)
        elif field_dict[header[i]] == DataType.NUMBER:
          colors.append(3)
      else:
        print "Something wrong here" 
        print header[i]
        exit()
  color_array = np.array(colors)
  color_array.resize(num_row, num_col)

  cmap = ListedColormap(['black', 'red', 'blue', 'green'])
  plt.pcolormesh(color_array, cmap=cmap)
  #plt.imshow(color_array, cmap=cmap)
  plt.xlabel('Fields')
  plt.ylabel('Samples/Participants')
  plt.title('Color map of product use data')
  
  plt.grid()
  #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
  #           ncol=3, mode="expand", borderaxespad=0.)
  plt.tight_layout()
  plt.savefig('data_color_map.png', format='png', bbox_inches='tight') 

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
