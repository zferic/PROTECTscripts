#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  csv_manipulation.py
#  5/30/2016
#  Copyright 2016 shidong <shidong@ece.neu.edu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


## Warnings: If the input structure changes, e.g. the redcap template, the
##          following code needs to be changed too. For more info, please
##          contact the author.

## current layout of the template
# info[0]       :   field name
# info[1]       :   form name
# info[2]       :   section header
# info[3]       :   field type
# info[4]       :   field label
# info[5]       :   choices, calculations, labels
# info[6]       :   field note
# info[7]       :   Text Validation Type OR Show Slider Number
# info[8]       :   Text Validation Min
# info[9]       :   Text Validation Max
# info[10]      :   Identifier?
# info[11]      :   Branching Logic (Show field only if...)
# info[12]      :   Required Field?
# there are other fields, but not important


import sys
import csv
import re

def Extract(csv_file, target_table):
  readfile = csv.reader(open(csv_file, "rb"))
  writefile = csv.writer(open(target_table+".csv", "wb"))

  # Write extracted row to new csv file
  for row in readfile:
    if row[1] == target_table:
      writefile.writerow(row)

def Update(original_csv_file, ref_csv_file):
  # Assumption here: No header in the original file
  originalfile = csv.reader(open(original_csv_file, "rb"))
  reffile = csv.reader(open(ref_csv_file, "rb"))
  updatedfile = csv.writer(open("updated_dd.csv", "wb"))

  print "WARNING: The program should change as reference csv file format" \
        "changes"

  list_ref = []
  for row in reffile:
    list_ref.append(row)
  # Populate new updated csv file
  for row in originalfile:
    rowstr = row
    for row_ref in list_ref:
      if row_ref[0] == row[0]:
        for idx in range(1, len(row_ref)):
          rowstr[idx+1] = row_ref[idx]
        break
    updatedfile.writerow(rowstr)


usage_str = "./[path to scripts] extract [path to csv file] [targe table]\n" \
            "./[path to scripts] update [path to original csv file] " \
            "[path to reference csv file]\n"

def main():
  if len(sys.argv) < 4:
    print "Too few arguments"
    print "Please specify the csv file and target."
    print usage_str
    sys.exit()

  if len(sys.argv) > 4:
    print "Too many. Read one csv file at at time."
    print usage_str
    sys.exit()

  # check the arguments
  command = sys.argv[1]
  print "Command : ", command

  if command == "extract":
    print "csv file : ", sys.argv[2]
    print "target table : ", sys.argv[3], "This has to be correct"
    print "Start program."

    filename = sys.argv[2]
    target_table = sys.argv[3]
    Extract(filename, target_table)
  elif command == "update":
    print "original csv file : ", sys.argv[2]
    print "reference csv file : ", sys.argv[3]
    print "Start program."

    originalfilename = sys.argv[2]
    referencefilename = sys.argv[3]
    Update(originalfilename, referencefilename)
  else:
    print "Unsupported command"
    exit()

  print "End program."
  return 0

if __name__ == '__main__':
  main()

 
