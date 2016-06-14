#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  checkMissFieldAndOrder.py
#  6/14/2016
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

import sys
import csv

usage_str = "Usage: ./[script name] [path to data dictionary csv] " \
            "[path to export data csv] [target table]\n"\
            "This script is used to check the inconsistency between data "\
            "dictionary and export data"

def main():

  if len(sys.argv) < 4:
    print "Too few arguments"
    print "Please specify the data dictionary, export data csv file and"\
          " target table."
    print usage_str
    sys.exit()

  if len(sys.argv) > 4:
    print "Too many arguments."
    print usage_str
    sys.exit()

  # check the arguments
  print "program name : ", sys.argv[0]
  print "data dictionary csv file : ", sys.argv[1]
  print "export data csv file : ", sys.argv[2]
  print "target table : ", sys.argv[3], "This has to be correct"
  print "Program starts.\n"

  ddfilename = sys.argv[1]
  edfilename = sys.argv[2]
  target_table = sys.argv[3]

  # read csv file
  ddfile = csv.reader(open(ddfilename, "rb"))
  edfile = csv.reader(open(edfilename, "rb"))

  ed_field_list = next(edfile)
  dd_field_list = []

  # look at the second column, find the right table to work on
  # You can specify which table to work on !!!
  for row in ddfile:
    tablename = row[1].strip()
    if tablename == target_table:
      dd_field_list.append(row[0])

  # Check if there is miss field in data dictionary
  miss_field_list = []
  for field in ed_field_list:
    if field not in dd_field_list:
      print "Miss in data dictionary: " + field
      miss_field_list.append(field)

  # Remove the miss field in export data list
  for miss_field in miss_field_list:
    ed_field_list.remove(miss_field)

  # Cross check
  miss_field_list = []
  for field in dd_field_list:
    if field not in ed_field_list:
      print "Not defined in export data : " + field
      miss_field_list.append(field)

  # Remove the miss field in export data list
  for miss_field in miss_field_list:
    dd_field_list.remove(miss_field)

  if len(dd_field_list) != len(ed_field_list):
    print "Something wrong here"
    sys.exit()

  # Check if there is inconsistent order between those two
  for i in range(len(dd_field_list)):
    if dd_field_list[i] != ed_field_list[i]:
      print "Inconsistent order of : " + dd_field_list[i]
      print "Should be : " + ed_field_list[i]

  # Program ends
  print "Program ends."

  return 0


if __name__ == '__main__':
  main()


