#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  checkUpdateDD.py
#  7/16/2015
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

# Items to update in current XML file
# (1) Unnecessary field -> remove
# (2) New field -> add
# (3) Miss constraint -> add constraint
# (4) Miss branch logic -> add branch logic


import sys
import collections
import csv
import re
import xml.etree.ElementTree as ET

default_label_name = "UNLABELED"

class FieldXml:

  form = ""
  section = ""
  constraints = ""
  branch_logic = ""

  def __init__(self, form, section,
               constraints, branch_logic):
    self.form = form
    self.section = section
    self.constraints = constraints
    self.branch_logic = branch_logic

field_xml_dict = collections.OrderedDict()
def ParseXml(xml_filename):
  global field_xml_dict
  tree = ET.parse(xml_filename)
  root = tree.getroot()
  for form in root.findall("form"):
    form_name = form.find("formName").text
    for sections in form.findall("sections"):
      for section in sections.findall("section"):
        section_name = ""
        if(sections.find("sectionLabelEnglish")):
          section_name = sections.find("sectionLabelEnglish").text
        else:
          section_name = default_label_name
        for fields in section.findall("fields"):
          for field in fields.findall("field"):
            field_name = field.find("fieldName").text
            field_constraints = field.find("fieldConstraints").text
            field_branch_logic = field.find("fieldBranchingLogic").text
            field_xml_dict[field_name] = FieldXml(form_name, section_name,
                                               field_constraints,
                                               field_branch_logic)

class FieldDD:

  form = ""
  section = ""
  data_type = ""
  label = ""
  note = ""
  constraints = ""
  branch_logic = ""

  def __init__(self, form, section,
               data_type, label, note,
               constraints, branch_logic):
    self.form = form
    self.section = section
    self.data_type = data_type
    self.label = label
    self.note = note
    self.constraints = constraints
    self.branch_logic = branch_logic


field_dd_dict = collections.OrderedDict()
def ParseDD(dd_filename):
  global field_dd_dict

  # read csv file
  dd_file = csv.reader(open(dd_filename, "rb"));
  
  # Iterate through all the rows
  section_name = default_label_name
  form_name = ""
  for row in dd_file:
    field_name = row[0]
    if form_name != row[1]:
      form_name = row[1]
      section_name = default_label_name
    if row[2]:
      section_name = row[2]
    data_type = row[3]
    label = row[4]
    note = row[6]
    minv = row[8]
    maxv = row[9]
    field_constraints = minv + " - " + maxv
    field_branch_logic = row[11]
    field_dd_dict[field_name] = FieldDD(form_name, section_name,
                                         data_type, label, note,
                                         field_constraints,
                                         field_branch_logic)

class CheckResult:
  field_name = ""
  command = ""
  previous_field_name = ""

  def __init__(self, field_name, command, previous_field_name):
    self.field_name = field_name
    self.command = command
    self.previous_field_name = previous_field_name

check_results_list = []
def CheckField():
  global check_results_list
  global field_xml_dict
  global field_dd_dict

  print (not field_xml_dict)
  print (not field_dd_dict)

  # If the two dictionary are empty, then return immdiately
  if (not field_xml_dict) or (not field_dd_dict):
    print "Haven't parse either xml or csv data dicationary"
    return

  # Obtain fields list from dictionary of XML file
  field_xml_list = field_xml_dict.keys()
  field_dd_list = field_dd_dict.keys()

  # Initialize the command
  command = ""

  # Check unnecessary field
  for field in field_xml_dict:
    if field not in field_dd_dict:
      command = "remove"
      current_index = field_xml_list.index(field)
      previous_field_name = field_xml_list[current_index-1]
      check_results_list.append(CheckResult(field, command,
                                            previous_field_name))      
  # Check new field
  for field in field_dd_dict:
    if field not in field_xml_dict:
      command = "add"
      current_index = field_dd_list.index(field)
      previous_field_name = field_dd_list[current_index-1]
      check_results_list.append(CheckResult(field, command,
                                            previous_field_name))

  # Check missing constraints
  for field in field_xml_dict:
    if field_xml_dict[field].constraints == "":
      command = "update_constraints"
      check_results_list.append(CheckResult(field, command, ""))

  # Check missing branch logic
  for field in field_xml_dict:
    if field_xml_dict[field].branch_logic == "":
      command = "update_branch_logic"
      check_results_list.append(CheckResult(field, command, ""))

def GenerateReport():
  # Check the XML check results
  if not check_results_list:
    print "Congratulations! Nothing needs to update!"
    return

  print "Totally " + str(len(check_results_list)) + " fields need to be updated"
  # Print out the results
  #for result in check_results_list:
  #  print "--------------------------"
  #  print "Field name: " + result.field_name
  #  print "Command: " + result.command
  

def BuildField(field):
  # Create subelement of field
  return
 
def UpdateXml():
  return

usage_str = "Usage: ./<script name> <path to data dictionary csv> " \
            "<path to data dictionary xml file>"

def main():

  if len(sys.argv) < 3:
    print "Too few arguments"
    print "Please specify the csv file and xml file."
    print usage_str
    sys.exit()

  if len(sys.argv) > 3:
    print "Too many arguments. Read one csv file at at time."
    print usage_str
    sys.exit()

  # check the arguments
  # print 'Number of arguments:', len(sys.argv), 'arguments.'
  print "program name : ", sys.argv[0]
  print "data dictionary csv file : ", sys.argv[1]
  print "data dictionary xml file : ", sys.argv[2]
  print "Start program."

  csv_filename = sys.argv[1]
  xml_filename = sys.argv[2]

  # Parse XML file
  ParseXml(xml_filename)

  # Parse DD csv file
  ParseDD(csv_filename)

  # Check field
  CheckField()

  # Generate check report
  GenerateReport()

  print "End program.\n",\

  return 0



if __name__ == '__main__':
  main()
