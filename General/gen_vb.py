#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gen_vb.py
#  6/16/2015
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
import collections

target_table = ""

Template_ErrorMsg1 = \
"Case EddErrors.CustomError_cond_no\n"\
"\tReturn \"If _condition is not _value, this must be NULL.\"\n"

Template_ErrorMsg2 = \
"Case EddErrors.CustomError_cond_no\n"\
"\tReturn \"Possible Error 1) Must be NULL if _condition is not _value "\
"2) Content is not an valid option.\"\n"

Template_CheckFunc = \
"Case \"_condition\", \"_field\"\n"\
"\tERR_error_no(e)\n"

Template_CustomCheck1 = \
"Friend Sub ERR_error_no(ByVal e As System.Data.DataColumnChangeEventArgs)\n"\
"\tWith e.Row\n"\
"\n"\
"\t\t\'\'space checking\n"\
"\t\tDim q As Integer = 1\n"\
"\t\tIf Not IsDBNull(.Item(\"_field\")) Then\n"\
"\t\t\tDim inputstr As String = .Item(\"_field\")\n"\
"\t\t\tDim cnt As Integer = 0\n"\
"\t\t\tFor Each c As Char In inputstr\n"\
"\t\t\t\tIf c <> \" \" Then\n"\
"\t\t\t\t\tcnt += 1\n"\
"\t\t\t\tEnd If\n"\
"\t\t\tNext\n"\
"\n"\
"\t\t\t\'\' consider empty\n"\
"\t\t\tIf cnt = 0 Then\n"\
"\t\t\t\tq = 99999\n"\
"\t\t\tEnd If\n"\
"\t\tElse\n"\
"\t\t\t\'\' consider empty\n"\
"\t\t\tq = 99999\n"\
"\t\tEnd If\n"\
"\n"\
"\t\tIf Not IsDBNull(.Item(\"_condition\")) Then\n"\
"\t\t\tIf .Item(\"_condition\") = _value Then\n"\
"\t\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tElseIf .Item(\"_condition\") <> _value And q = 99999 Then\n"\
"\t\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tElse\n"\
"\t\t\t\tMe.AddError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tEnd If\n"\
"\t\tElse\n"\
"\t\t\tIf q = 99999 Then\n"\
"\t\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tElse\n"\
"\t\t\t\tMe.AddError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tEnd If\n"\
"\t\tEnd If\n"\
"\tEnd With\n"\
"End Sub\n\n"\

Template_CustomCheck2 = \
"Friend Sub ERR_error_no(ByVal e As System.Data.DataColumnChangeEventArgs)\n"\
"\tWith e.Row\n"\
"\n"\
"\t\t\'\'space checking\n"\
"\t\tDim q As Integer = 1\n"\
"\t\tDim content As Integer = 99999 \'Invalid content\n"\
"\t\tIf Not IsDBNull(.Item(\"_field\")) Then\n"\
"\t\t\tDim inputstr As String = .Item(\"_field\")\n"\
"\t\t\tDim cnt As Integer = 0\n"\
"\t\t\tFor Each c As Char In inputstr\n"\
"\t\t\t\tIf c <> \" \" Then\n"\
"\t\t\t\t\tcnt += 1\n"\
"\t\t\t\tEnd If\n"\
"\t\t\tNext\n"\
"\n"\
"\t\t\t\'\' consider empty\n"\
"\t\t\tIf cnt = 0 Then\n"\
"\t\t\t\tq = 99999\n"\
"\t\t\tElse\n"\
"\t\t\t\tcontent = CInt(inputstr)\n"\
"\t\t\tEnd If\n"\
"\t\tElse\n"\
"\t\t\t\'\' consider empty\n"\
"\t\t\tq = 99999\n"\
"\t\tEnd If\n"\
"\n"\
"\t\tIf Not IsDBNull(.Item(\"_condition\")) Then\n"\
"\t\t\tIf .Item(\"_condition\") = _value And (q = 99999 Or _choice_string) Then\n"\
"\t\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tElseIf .Item(\"_condition\") <> _value And q = 99999 Then\n"\
"\t\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tElse\n"\
"\t\t\t\tMe.AddError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tEnd If\n"\
"\t\tElse\n"\
"\t\t\tIf q = 99999 Then\n"\
"\t\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tElse\n"\
"\t\t\t\tMe.AddError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_cond_no)\n"\
"\t\t\tEnd If\n"\
"\t\tEnd If\n"\
"\tEnd With\n"\
"End Sub\n\n"\

Template_GridEvents_Case = \
"Case \"_condition\"\n"\

Template_GridEvents_Item = \
"\tedp.AfterCellUpdate(sender, e.Cell.Row.Cells.Item(\"_field\"))\n"

# regular expression needed
regex_branch_logic = re.compile(r"\[(\w+)\]\s?=\s?'(\d+)'")

# Function of generating error message type 1
def GenErrorMsg1(cond_no, condition, value):
  format_string = Template_ErrorMsg1.replace("_cond_no", cond_no).\
                  replace("_condition", condition).\
                  replace("_value", value)
  return format_string

# Function of generating error message type 2
def GenErrorMsg2(cond_no, condition, value):
  format_string = Template_ErrorMsg2.replace("_cond_no", cond_no).\
                  replace("_condition", condition).\
                  replace("_value", value)
  return format_string

# Function of generating check function
def GenCheckFunc(error_no, condition, field):
  format_string = Template_CheckFunc.replace("_error_no", error_no).\
                  replace("_condition", condition).\
                  replace("_field", field)
  return format_string

# Function of generating custom check type 1
def GenCustomCheck1(error_no, cond_no, condition, field, value):
  format_string = Template_CustomCheck1.replace("_error_no", error_no).\
                  replace("_cond_no", cond_no).\
                  replace("_condition", condition).\
                  replace("_field", field).\
                  replace("_value", value)
  return format_string

def GenCustomCheck2(error_no, cond_no, condition, field, value, choice_str):
  format_string = Template_CustomCheck2.replace("_error_no", error_no).\
                  replace("_cond_no", cond_no).\
                  replace("_condition", condition).\
                  replace("_field", field).\
                  replace("_value", value).\
                  replace("_choice_string", choice_str)
  return format_string

#Function of generating grid event case
def GenGridEventCase(condition):
  format_string = Template_GridEvents_Case.replace("_condition", condition)
  return format_string

#Function of generating grid event item
def GenGridEventItem(field):
  format_string = Template_GridEvents_Item.replace("_field", field)
  return format_string

# Condition information class
class ConditionInfo:
  def __init__(self, number, field, value, choice_included, choice_str):
    self.number = number
    self.field = field
    self.value = value
    self.choice_included = choice_included
    self.choice_str = choice_str

# Some global data dictionary needed
condition_info_dict = collections.OrderedDict()
 
condition_number = 1
def GenConditionInfo(info):

  ## extract related fields
  ## branching logic is not considered here
  field_name     = info[0]        # name
  field_choices  = info[5]        # data options
  field_branch   = info[11]

  # target table name
  target_table = info[1]

  # check "|" symbol
  sym_index = field_choices.find("|")

  # Branch logic and choice check
  condition = ""
  value = -1
  choice_included = False
  choice_str = ""
  global condition_number
  if regex_branch_logic.match(field_branch):
    # Obtain the branch logic information
    condition = regex_branch_logic.match(field_branch).group(1)
    value = regex_branch_logic.match(field_branch).group(2)

    # Obtain the choices if there is any
    if sym_index > -1:
      # extract integers out from field_choices
      seplist = field_choices.split('|')
      for item in seplist:
        # extract the 1st integer in each item
        found_int = re.search("\d+", item)
        choice_str += "content = " + found_int.group() + " Or "
      choice_included = True
      choice_str = choice_str[:-4]

    # Set the condition field dictionary
    if condition not in condition_info_dict:
      condition_info_dict[condition] = []
      condition_info_dict[condition].append(ConditionInfo(condition_number, \
                                                          field_name, \
                                                          value, \
                                                          choice_included, \
                                                          choice_str))
      condition_number += 1
    else:
      value_list = []
      choice_included_list = []
      condition_info = condition_info_dict[condition]
      for info in condition_info:
        value_list.append(info.value)
        choice_included_list.append(info.choice_included)
      if value not in value_list:
        # The value of condition is different from previous one
        condition_info.append(ConditionInfo(condition_number, \
                                            field_name, \
                                            value, \
                                            choice_included, \
                                            choice_str))
        condition_number += 1
      else:
        # Other siutations
        same_value_index_list = [i for i, x in enumerate(condition_info) \
                                 if x.value == value]

        # 1) current field doesn't include choices
        if choice_included == False:
          choice_included_false_exist = False
          for i in same_value_index_list:
            # Get the condition number of its predecessor
            if condition_info[i].choice_included == False:
              previous_condition_number = condition_info[i].number
              condition_info.append(ConditionInfo(previous_condition_number, \
                                                  field_name, \
                                                  value, \
                                                  choice_included, \
                                                  choice_str))
              choice_included_false_exist = True
              break
          if choice_included_false_exist == False:
            condition_info.append(ConditionInfo(condition_number, \
                                                field_name, \
                                                value, \
                                                choice_included, \
                                                choice_str))
            condition_number += 1

        # 2) Current field includes choices
        else:
          choice_included_true_exist = False
          for i in same_value_index_list:
            if condition_info[i].choice_included == True:
              previous_condition_number = condition_info[i].number
              condition_info.append(ConditionInfo(previous_condition_number, \
                                                  field_name, \
                                                  value, \
                                                  choice_included, \
                                                  choice_str))
              choice_included_true_exist = True
              break
          if choice_included_true_exist == False:
            condition_info.append(ConditionInfo(condition_number, \
                                                field_name, \
                                                value, \
                                                choice_included, \
                                                choice_str))
            condition_number += 1

error_msg_str = ""
check_func_str = ""
custom_check_str = ""
grid_event_str = ""
usage_str = "[Usage]: ./<script name> <path to data dictionary csv> " \
            "<target table>"

def main():

  global error_msg_str
  global check_func_str
  global custom_check_str
  global grid_event_str

  if len(sys.argv) < 3:
    print "Too few arguments"
    print "Please specify the csv file and target."
    print usage_str
    sys.exit()

  if len(sys.argv) > 3:
    print "Too many. Read one csv file at at time."
    print usage_str
    sys.exit()

  # check the arguments
  # print 'Number of arguments:', len(sys.argv), 'arguments.'
  print "program name : ", sys.argv[0]
  print "csv file : ", sys.argv[1]
  print "target table : ", sys.argv[2], "This has to be correct"
  print "Start program."

  filename = sys.argv[1]
  target_table = sys.argv[2]

  # read csv file
  file = csv.reader(open(filename, "rb"));

  # open text file to write
  error_msg_fname = target_table + "_error_msg.txt"
  check_func_fname = target_table + "_check_func.txt"
  custom_check_fname = target_table + "_custom_check.txt"
  grid_event_fname = target_table + "_grid_event.txt"
  error_msg_file = open(error_msg_fname, "w")
  check_func_file = open(check_func_fname, "w")
  custom_check_file = open(custom_check_fname, "w")
  grid_event_file = open(grid_event_fname, "w")

  # look at the second column, find the right table to work on
  # You can specify which table to work on !!!
  for row in file:
    tablename = row[1].strip()
    if tablename == target_table:
      GenConditionInfo(row)

  # Generate error msg string
  error_no = 1
  for key in condition_info_dict:
    condition = key
    condition_info = condition_info_dict[key]
    grid_event_str += GenGridEventCase(condition)
    cond_no_list = []
    for info in condition_info:
      if info.number not in cond_no_list:
        cond_no_list.append(info.number)
        if not info.choice_included:
          error_msg_str += GenErrorMsg1(str(info.number), condition, info.value)
        else:
          error_msg_str += GenErrorMsg2(str(info.number), condition, info.value)

      if not info.choice_included:
        custom_check_str += GenCustomCheck1(str(error_no),\
                                            str(info.number),\
                                            condition, \
                                            info.field, info.value)
      else:
        custom_check_str += GenCustomCheck2(str(error_no),\
                                            str(info.number),\
                                            condition, \
                                            info.field, info.value, \
                                            info.choice_str)
      check_func_str += GenCheckFunc(str(error_no), condition, info.field)
      grid_event_str += GenGridEventItem(info.field)
      error_no += 1

  # Write output file
  error_msg_file.write(error_msg_str)
  check_func_file.write(check_func_str)
  custom_check_file.write(custom_check_str)
  grid_event_file.write(grid_event_str)

  # close output file
  error_msg_file.close()
  check_func_file.close()
  custom_check_file.close()
  grid_event_file.close()

  # Program ends
  print "End program.\n"

  return 0

if __name__ == '__main__':
  main()


