#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  genDataDictXml.py
#  7/29/2015
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

# Class FieldDD
class FieldDD:

  data_type = ""
  label = ""
  note = ""
  constraints = ""
  branch_logic = ""
  choice_dict = collections.OrderedDict()

  def __init__(self, data_type, label, note,
               constraints, branch_logic):
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
    if form_name not in field_dd_dict:
      field_dd_dict[form_name] = collections.OrderedDict()
      field_dd_dict[form_name][section_name] = collections.OrderedDict()
    else:
      if section_name not in field_dd_dict[form_name]:
        field_dd_dict[form_name][section_name] = collections.OrderedDict()
    field_dd_dict[form_name][section_name][field_name] = FieldDD(data_type, label, note,
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
        field_dd_dict[form_name][section_name][field_name].choice_dict[number] = content

# Function BuildField
def BuildField(element, form_name, section_name, field_name):
  # Create subelement of field
  field = ET.SubElement(element, "field")
  fieldName = ET.SubElement(field, "fieldName")
  fieldName.text = field_name.decode('utf-8')
  fieldLabelSpanish = ET.SubElement(field, "fieldLabelSpanish")
  fieldLabelEnglish = ET.SubElement(field, "fieldLabelEnglish")
  fieldLabelSpanish.text = field_dd_dict[form_name][section_name][field_name].label.decode('utf-8')
  fieldLabelEnglish.text = field_dd_dict[form_name][section_name][field_name].label.decode('utf-8')
  fieldType = ET.SubElement(field, "fieldType")
  fieldType.text = field_dd_dict[form_name][section_name][field_name].data_type.decode('utf-8')
  fieldNoteSpanish = ET.SubElement(field, "fieldNoteSpanish")
  fieldNoteEnglish = ET.SubElement(field, "fieldNoteEnglish")
  if field_dd_dict[form_name][section_name][field_name].note:
    fieldNoteSpanish.text = field_dd_dict[form_name][section_name][field_name].note.decode('utf-8')
    fieldNoteEnglish.text = field_dd_dict[form_name][section_name][field_name].note.decode('utf-8')
  fieldConstraints = ET.SubElement(field, "fieldConstraints")
  if field_dd_dict[form_name][section_name][field_name].constraints:
    fieldConstraints.text = field_dd_dict[form_name][section_name][field_name].constraints.decode('utf-8')
  fieldBranchLogic = ET.SubElement(field, "fieldBranchingLogic")
  if field_dd_dict[form_name][section_name][field_name].branch_logic:
    fieldBranchLogic.text = field_dd_dict[form_name][section_name][field_name].branch_logic.decode('utf-8')
  if fieldType.text == "radio" or fieldType.text == "checkbox":
    fieldValues = ET.SubElement(field, "fieldValues")
    for choice_value in field_dd_dict[form_name][section_name][field_name].choice_dict:
      fieldData = ET.SubElement(fieldValues, "fieldData")
      fieldValue = ET.SubElement(fieldData, "fieldValue")
      fieldValue.text = choice_value.decode('utf-8')
      fieldValueLabelEnglish = ET.SubElement(fieldData, "fieldValueLabelEnglish")
      fieldValueLabelEnglish.text = \
        field_dd_dict[form_name][section_name][field_name].choice_dict[choice_value].decode('utf-8')
      fieldValueLabelSpanish = ET.SubElement(fieldData, "fieldValueLabelSpanish")
      fieldValueLabelSpanish.text = \
        field_dd_dict[form_name][section_name][field_name].choice_dict[choice_value].decode('utf-8')

# Function UpdateXml
def BuildXml(xml_filename):
  e_root = ET.Element("dataDictionary")
  for form in field_dd_dict:
    e_form = ET.SubElement(e_root, "form")
    e_formName = ET.SubElement(e_form, "formName")
    e_formName.text = form.decode('utf-8')
    e_formLabelEnglish = ET.SubElement(e_form, "formLabelEnglish")
    e_formLabelSpanish = ET.SubElement(e_form, "formLabelSpanish")
    e_formLabelEnglish.text = form.decode('utf-8')
    e_formLabelSpanish.text = form.decode('utf-8')
    e_sections = ET.SubElement(e_form, "sections")
    for section in field_dd_dict[form]:
      e_section = ET.SubElement(e_sections, "section")
      e_sectionLabelEnglish = ET.SubElement(e_section, "sectionLabelEnglish")
      e_sectionLabelSpanish = ET.SubElement(e_section, "sectionLabelSpanish")
      e_sectionLabelEnglish.text = section.decode('utf-8')
      e_sectionLabelSpanish.text = section.decode('utf-8')
      for field in field_dd_dict[form][section]:
        BuildField(e_section, form, section, field)

  rough_string = ET.tostring(e_root, encoding='utf-8')
  fn_output_xml = open(xml_filename, 'w')
  fn_output_xml.write(rough_string)
  fn_output_xml.close()

usage_str = "Usage: ./<script name> <path to data dictionary csv> " \
            "<path to new xml file>"
# Function main
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
  print "Output xml file : ", sys.argv[2]
  print "Start program."

  csv_filename = sys.argv[1]
  xml_filename = sys.argv[2]

  # Parse DD csv file
  ParseDD(csv_filename)

  # Update Xml
  BuildXml(xml_filename)

  print "End program.\n",\

  return 0



if __name__ == '__main__':
  main()
