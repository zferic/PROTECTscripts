#! /usr/bin/env python

import sys
import csv
import re

extract_all = False

# According the data dictionary
field_index = 0
form_index = 1
type_index = 3
text_type_index = 7

human_subject_form_list = ["first_visit", "med_rec_v1", "product_use"]

def Extract(csv_file):
  readfile = csv.reader(open(csv_file, "r"))
  writefile = csv.writer(open("chosenfields.csv", "w"))

  # write header
  #header = next(readfile)

  # Human subject data
  for row in readfile:
      new_row = []
      if row[type_index] == "radio":
        continue
      elif row[text_type_index] == "number" or row[text_type_index] == "integer":
        new_row.append(row[field_index].upper())
        writefile.writerow(new_row)

  # Biological data
  key_field = "CONC"
  row = [key_field]
  writefile.writerow(row)

  # Postpartum label
  birth_label = "PPTERM"
  row = [birth_label]
  writefile.writerow(row)

def main():
    print ("Start program.")

    filename = "human_subjects_dd.csv"
    Extract(filename)

    print ("End program.")
    return 0

if __name__ == '__main__':
  main()
