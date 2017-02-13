#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  genDataDictCsv.py
#  1/29/2017
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

#  For Biological data only
## current layout of the generated csv
# info[0]       :   field name
# info[1]       :   form name
# info[2]       :   field type
# info[3]       :   choices, calculations, labels
# info[4]       :   Text Validation Type OR Show Slider Number
# info[5]       :   Text Validation Min
# info[6]       :   Text Validation Max
# info[7]       :   Branching Logic (Show field only if...)
# there are other fields, but not important

import sys
import collections
import csv
import re
import xml.etree.ElementTree as ET

# FieldXml class
class FieldXml:

  field_type = ""
  constraints = ""
  branch_logic = ""
  choice_dict = collections.OrderedDict()

  def __init__(self, field_type,
               constraints, branch_logic):
    self.field_type = field_type
    self.constraints = constraints
    self.branch_logic = branch_logic
    self.choice_dict = collections.OrderedDict()

# Function ParseXml
field_xml_dict = collections.OrderedDict()
def ParseXml(xml_filename):
  tree = ET.parse(xml_filename)
  root = tree.getroot()
  for form in root.findall("form"):
    form_name = form.find("formName").text
    for sections in form.findall("sections"):
      for section in sections.findall("section"):
        section_name = ""
        section_name = section.find("sectionLabelEnglish").text
        field_xml_dict[section_name] = collections.OrderedDict()
        for fields in section.findall("fields"):
          for field in fields.findall("field"):
            field_name = field.find("fieldName").text
            field_type = field.find("fieldType").text
            field_constraints = ""#field.find("fieldConstraints").text
            field_branch_logic = ""#field.find("fieldBranchingLogic").text
            field_xml_dict[section_name][field_name] = FieldXml(field_type,
                                               field_constraints,
                                               field_branch_logic)
            # Record field value if there is any
            for field_values in field.findall("fieldValues"):
              for field_data in field_values.findall("fieldData"):
                number = field_data.find("fieldValue").text
                content = field_data.find("fieldValueLabelEnglish").text
                field_xml_dict[section_name][field_name].choice_dict[number] = content

usage_str = "Usage: ./<script name> <path to data dictionary csv> " \
            "<path to new xml file>"

# Function main
def main():

  if len(sys.argv) < 3:
    print "Too few arguments"
    print "Please specify the xml file and csv file."
    print usage_str
    sys.exit()

  if len(sys.argv) > 3:
    print "Too many arguments. Read one xml file at at time."
    print usage_str
    sys.exit()

  # check the arguments
  # print 'Number of arguments:', len(sys.argv), 'arguments.'
  print "program name : ", sys.argv[0]
  print "Iutput xml file : ", sys.argv[1]
  print "Output data dictionary csv file : ", sys.argv[2]
  print "Start program."

  xml_filename = sys.argv[1]
  csv_filename = sys.argv[2]

  # Parse Xml
  ParseXml(xml_filename)

  writefile = csv.writer(open(csv_filename, "wb"))
  for section_name in field_xml_dict:
    for field_name in field_xml_dict[section_name]:
      refined_row = ["", "", "", "", "", "", "", ""]
      refined_row[0] = field_name
      refined_row[1] = section_name
      refined_row[2] = field_xml_dict[section_name][field_name].field_type
      choice_str = ""
      for choice in field_xml_dict[section_name][field_name].choice_dict:
        choice_str += choice + ", " + field_xml_dict[section_name][field_name].choice_dict[choice] + " | "
      choice_str = choice_str[:-3]
      refined_row[3] = choice_str
      
      writefile.writerow(refined_row)

  print "End program.\n",\

  return 0



if __name__ == '__main__':
  main()
