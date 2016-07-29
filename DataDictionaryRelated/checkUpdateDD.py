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
from xml.dom.minidom import parse, parseString

default_label_name = "UNLABELED"

# FieldXml class
class FieldXml:

  form = ""
  section = ""
  constraints = ""
  branch_logic = ""
  choice_dict = collections.OrderedDict()

  def __init__(self, form, section,
               constraints, branch_logic):
    self.form = form
    self.section = section
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
            # Record field value if there is any
            for field_values in field.findall("fieldValues"):
              for field_data in field_values.findall("fieldData"):
                number = field_data.find("fieldValue").text
                content = field_data.find("fieldValueLabelEnglish").text
                field_xml_dict[field_name].choice_dict[number] = content

# Class FieldDD
class FieldDD:

  form = ""
  section = ""
  data_type = ""
  label = ""
  note = ""
  constraints = ""
  branch_logic = ""
  choice_dict = collections.OrderedDict()

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
    self.choice_dict = collections.OrderedDict()


# Function ParsDD
regex_choice = re.compile(r"[+-]?(\d+),.*")
field_dd_dict = collections.OrderedDict()
def ParseDD(dd_filename):
  # read csv file
  dd_file = csv.reader(open(dd_filename, "rb"));
  
  # Iterate through all the rows
  section_name = default_label_name
  form_name = ""
  header = next(dd_file)
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
    if minv and maxv:
      field_constraints = minv + " - " + maxv
    else:
      field_constraints = ""
    field_branch_logic = row[11]
    field_dd_dict[field_name] = FieldDD(form_name, section_name,
                                        data_type, label, note,
                                        field_constraints,
                                        field_branch_logic)
    field_choices = row[5]
    if data_type == "radio" or data_type == "checkbox":
      # extract integers out from field_choices
      sepintlist = field_choices.split('|')

      for item in sepintlist:
        item = item.strip()
        number = regex_choice.match(item).group(1)
        content = item.replace(number+",", "")
        field_dd_dict[field_name].choice_dict[number] = content

# Class CheckResult
class CheckResult:
  field_name = ""
  command = ""
  previous_field_name = ""

  def __init__(self, field_name, command, previous_field_name):
    self.field_name = field_name
    self.command = command
    self.previous_field_name = previous_field_name

# Function CheckField
check_results_list = []
def CheckField():
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
    if field in field_dd_dict:
      if (field_xml_dict[field].constraints == None) and (field_dd_dict[field].constraints == ""):
        continue
      if field_xml_dict[field].constraints != field_dd_dict[field].constraints:
        command = "update_constraints"
        check_results_list.append(CheckResult(field, command, ""))

  # Check missing branch logic
  for field in field_xml_dict:
    if field in field_dd_dict:
      if (field_xml_dict[field].branch_logic == None) and (field_dd_dict[field].branch_logic == ""):
        continue
      if field_xml_dict[field].branch_logic != field_dd_dict[field].branch_logic:
        command = "update_branch_logic"
        check_results_list.append(CheckResult(field, command, ""))

  # Check inconsistent radio items
  for field in field_xml_dict:
    if field in field_dd_dict:
      if field_dd_dict[field].choice_dict and field_xml_dict[field].choice_dict:
        for choice_value in field_dd_dict[field].choice_dict:
          if choice_value not in field_xml_dict[field].choice_dict:
            #print "Field name: ", field
            #print field_dd_dict[field].choice_dict
            #print field_xml_dict[field].choice_dict
            command = "update_field_choice"
            check_results_list.append(CheckResult(field, command, ""))
            break
        continue
        for choice_value in field_xml_dict[field].choice_dict:
          if choice_value not in field_dd_dict[field].choice_dict:
            #print "Field name: ", field
            #print field_dd_dict[field].choice_dict
            #print field_xml_dict[field].choice_dict
            command = "update_field_choice"
            check_results_list.append(CheckResult(field, command, ""))
            break
      elif field_dd_dict[field].choice_dict and (not field_xml_dict[field].choice_dict):
          #print "Field name: ", field
          #print field_dd_dict[field].choice_dict
          #print field_xml_dict[field].choice_dict
          command = "update_field_choice"
          check_results_list.append(CheckResult(field, command, ""))

# Function Generate report
def GenerateReport():
  # Check the XML check results
  if not check_results_list:
    print "Congratulations! Nothing needs to report!"
    return

  print "Totally " + str(len(check_results_list)) + " fields need to be updated"
  # Print out the results
  add_list = []
  remove_list = []
  update_constraints_list = []
  update_branch_logic_list = []
  update_field_choice_list = []
  for result in check_results_list:
    if result.command == "add":
      add_list.append(result.field_name)
    if result.command == "remove":
      remove_list.append(result.field_name)
    if result.command == "update_constraints":
      update_constraints_list.append(result.field_name) 
    if result.command == "update_branch_logic":
      update_branch_logic_list.append(result.field_name)
    if result.command == "update_field_choice":
      update_field_choice_list.append(result.field_name) 
  print "Add number: ", len(add_list)
  print "Remove number: ", len(remove_list)
  print "Update constraints number: ", len(update_constraints_list)
  print "Update branch logic number: ", len(update_branch_logic_list)
  print "Update field choice number: ", len(update_field_choice_list)
  

# Function BuildField
def BuildField(field_name):
  # Create subelement of field
  field = ET.Element("field")
  fieldName = ET.SubElement(field, "fieldName")
  fieldName.text = field_name.decode('utf-8')
  fieldLabelSpanish = ET.SubElement(field, "fieldLabelSpanish")
  fieldLabelEnglish = ET.SubElement(field, "fieldLabelEnglish")
  fieldLabelSpanish.text = field_dd_dict[field_name].label.decode('utf-8')
  fieldLabelEnglish.text = field_dd_dict[field_name].label.decode('utf-8')
  fieldType = ET.SubElement(field, "fieldType")
  fieldType.text = field_dd_dict[field_name].data_type.decode('utf-8')
  fieldNoteSpanish = ET.SubElement(field, "fieldNoteSpanish")
  fieldNoteEnglish = ET.SubElement(field, "fieldNoteEnglish")
  if field_dd_dict[field_name].note:
    fieldNoteSpanish.text = field_dd_dict[field_name].note.decode('utf-8')
    fieldNoteEnglish.text = field_dd_dict[field_name].note.decode('utf-8')
  fieldConstraints = ET.SubElement(field, "fieldConstraints")
  if field_dd_dict[field_name].constraints:
    fieldConstraints.text = field_dd_dict[field_name].constraints.decode('utf-8')
  fieldBranchLogic = ET.SubElement(field, "fieldBranchingLogic")
  if field_dd_dict[field_name].branch_logic:
    fieldBranchLogic.text = field_dd_dict[field_name].branch_logic.decode('utf-8')
  if fieldType.text == "radio" or fieldType.text == "checkbox":
    fieldValues = ET.SubElement(field, "fieldValues")
    for choice_value in field_dd_dict[field_name].choice_dict:
      fieldData = ET.SubElement(fieldValues, "fieldData")
      fieldValue = ET.SubElement(fieldData, "fieldValue")
      fieldValue.text = choice_value.decode('utf-8')
      fieldValueLabelEnglish = ET.SubElement(fieldData, "fieldValueLabelEnglish")
      fieldValueLabelEnglish.text = \
        field_dd_dict[field_name].choice_dict[choice_value].decode('utf-8')
      fieldValueLabelSpanish = ET.SubElement(fieldData, "fieldValueLabelSpanish")
      fieldValueLabelSpanish.text = \
        field_dd_dict[field_name].choice_dict[choice_value].decode('utf-8')

  return field
 
# Function UpdateXml
def UpdateXml(xml_filename, output_xml_filename):
  # Check the XML check results
  if not check_results_list:
    print "Congratulations! Nothing needs to update!"
    return

  # Obtain the 
  tree = ET.parse(xml_filename)

  # Check each item that needs to be updated in XML
  for result in check_results_list:
    # Extract the command
    command = result.command;    

    # Extract previous field alread existing in current XML
    previous_field_name = result.previous_field_name

    # Extract field needs to be updated
    field_name = result.field_name

    # Iterate every node
    root = tree.getroot()
    finished = False
    for form in root.findall("form"):
      if finished == True:
        break
      for sections in form.findall("sections"):
        if finished == True:
          break
        for section in sections.findall("section"):
          if finished == True:
            break
          for fields in section.findall("fields"):
            if finished == True:
              break
            for field in fields.findall("field"):
              if command == "remove":
                if field.find("fieldName").text == field_name:
                  fields.remove(field)
                  finished = True
                  break
              elif command == "add":
                if field.find("fieldName").text == previous_field_name:
                  field_idx = fields.getchildren().index(field) + 1
                  fields.insert(field_idx, BuildField(field_name))
                  finished = True
                  break
              elif command == "update_constraints":
                if field.find("fieldName").text == field_name:
                  field.find("fieldConstraints").text =\
                    field_dd_dict[field_name].constraints.decode('utf-8')
                  finished = True
                  break
              elif command == "update_branch_logic":
                if field.find("fieldName").text == field_name:
                  field.find("fieldBranchingLogic").text =\
                    field_dd_dict[field_name].branch_logic.decode('utf-8')
                  finished = True
                  break
              elif command == "update_field_choice":
                if field.find("fieldName").text == field_name:
                  fieldValues = field.find("fieldValues")
                  if fieldValues != None:
                    field.remove(fieldValues)
                  # Add choice from data ditionary
                  fieldValues = ET.SubElement(field, "fieldValues")
                  for choice_value in field_dd_dict[field_name].choice_dict:
                    fieldData = ET.SubElement(fieldValues, "fieldData")
                    fieldValue = ET.SubElement(fieldData, "fieldValue")
                    fieldValue.text = choice_value.decode('utf-8')
                    fieldValueLabelEnglish = ET.SubElement(fieldData, "fieldValueLabelEnglish")
                    fieldValueLabelEnglish.text = \
                      field_dd_dict[field_name].choice_dict[choice_value].decode('utf-8')
                    fieldValueLabelSpanish = ET.SubElement(fieldData, "fieldValueLabelSpanish")
                    fieldValueLabelSpanish.text = \
                      field_dd_dict[field_name].choice_dict[choice_value].decode('utf-8')
                  finished = True
                  break
              else:
                print "Command NOT recognized"
                exit(1)

  # Debug code
  #for form in root.findall("form"):
  #  print form.find("formName").text
  #  for sections in form.findall("sections"):
  #    for section in sections.findall("section"):
  #      if section.find("sectionLabelEnglish").text:
  #        print "==>" + section.find("sectionLabelEnglish").text
  #      else:
  #        print "\t==> " + "UNDEFINED LABEL"
  #      for fields in section.findall("fields"):
  #        for field in fields.findall("field"):
  #          print "\t==>" + field.find("fieldName").text

  #exit()
  # Write tree to xml file
  #rough_string = ET.tostring(tree.getroot(), encoding='utf-8')
  #reparsed = parseString(rough_string)

  #fn_output_xml = open(output_xml_filename, 'w')
  #fn_output_xml.write(reparsed.toprettyxml(indent=" ", newl="", encoding="utf-8"))
  #fn_output_xml.close()
  tree.write(output_xml_filename, encoding='utf-8')

usage_str = "Usage: ./<script name> <path to data dictionary csv> " \
            "<path to data dictionary xml file> <path to new xml file>"
# Function main
def main():

  if len(sys.argv) < 4:
    print "Too few arguments"
    print "Please specify the csv file and xml file."
    print usage_str
    sys.exit()

  if len(sys.argv) > 4:
    print "Too many arguments. Read one csv file at at time."
    print usage_str
    sys.exit()

  # check the arguments
  # print 'Number of arguments:', len(sys.argv), 'arguments.'
  print "program name : ", sys.argv[0]
  print "data dictionary csv file : ", sys.argv[1]
  print "data dictionary xml file : ", sys.argv[2]
  print "Output xml file : ", sys.argv[3]
  print "Start program."

  csv_filename = sys.argv[1]
  xml_filename = sys.argv[2]
  output_xml_filename = sys.argv[3]

  # Parse XML file
  ParseXml(xml_filename)

  # Parse DD csv file
  ParseDD(csv_filename)

  # Check field
  CheckField()

  # Update Xml
  UpdateXml(xml_filename, output_xml_filename)

  # Generate check report
  GenerateReport()

  print "End program.\n",\

  return 0



if __name__ == '__main__':
  main()
