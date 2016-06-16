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
"Case EddErrors.CustomError_error_no\n"\
"\tReturn \"If _condition is not _value, this must be NULL.\"\n"

Template_ErrorMsg2 = \
"Case EddErrors.CustomError_error_no\n"\
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
"\t\t\t\tIf c <> " " Then\n"\
"\t\t\t\t\tcnt += 1\n"\
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
"\t\tIf .Item(\"_condition\") = _value Then\n"\
"\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"field\"), EddErrors.CustomError_error_no)\n"\
"\t\tElseIf .Item(\"_condition\") <> _value And q = 99999 Then\n"\
"\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_error_no)\n"\
"\t\tElse\n"\
"\t\t\tMe.AddError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_error_no)\n"\
"\t\tEnd If\n"\
"\tEnd With\n"\
"End Sub\n"\

Template_CustomCheck2 = \
"Friend Sub ERR_error_no(ByVal e As System.Data.DataColumnChangeEventArgs)\n"\
"\tWith e.Row\n"\
"\n"\
"\t\t\'\'space checking\n"\
"\t\tDim q As Integer = 1\n"\
"\t\tDim content As Integer = 99999 \'Invalid content"\
"\t\tIf Not IsDBNull(.Item(\"_field\")) Then\n"\
"\t\t\tDim inputstr As String = .Item(\"_field\")\n"\
"\t\t\tDim cnt As Integer = 0\n"\
"\t\t\tFor Each c As Char In inputstr\n"\
"\t\t\t\tIf c <> " " Then\n"\
"\t\t\t\t\tcnt += 1\n"\
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
"\t\tIf .Item(\"_condition\") = _value And (_choice_string) Then\n"\
"\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"field\"), EddErrors.CustomError_error_no)\n"\
"\t\tElseIf .Item(\"_condition\") <> _value And q = 99999 Then\n"\
"\t\t\tMe.RemoveError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_error_no)\n"\
"\t\tElse\n"\
"\t\t\tMe.AddError(e.Row, e.Row.Table.Columns.Item(\"_field\"), EddErrors.CustomError_error_no)\n"\
"\t\tEnd If\n"\
"\tEnd With\n"\
"End Sub\n"\

Template_GridEvents_Case = \
"Case \"condition\"\n"\

Template_GridEvents_Item = \
"\tedp.AfterCellUpdate(sender, e.Cell.Row.Cells.Item(\"field\")\n)"

# regular expression needed
regex_branch_logic = re.compile(r"\[(\w+)\]\s?=\s?'(\d+)'")

# Some data dictionary needed
condition_field_dict = collections.OrderedDict()

# Function of generating error message type 1
def GenErrorMsg1(error_no, condition, value):
  format_string = Template_ErrorMsg1.replace("_error_no", error_no).\
                  replace("_condition", condition).\
                  replace("_value", value)
  return format_string

# Function of generating error message type 2
def GenErrorMsg1(error_no, condition, value):
  format_string = Template_ErrorMsg2.replace("_error_no", error_no).\
                  replace("_condition", condition).\
                  replace("_value", value)
  return format_string

# Function of generating check function
def GenCheckFunc(error_no, condition, field):
  format_string = Template_CheckFunc.replace("_error_no", error_no).\
                  replace("_condition", condition).\
                  replace("_field", filed)
  return format_string

# Function of generating custom check type 1
def GenCustomCheck1(error_no, condition, field, value):
  format_string = Template_CustomCheck1.replace("_error_no", error_no).\
                  replace("_condition", condition).\
                  replace("_field", field).\
                  replace("_value", value)
  return format_string

def GenCustomCheck2(error_no, condition, field, value):
  format_string = Template_CustomCheck2.replace("_error_no", error_no).\
                  replace("_condition", condition).\
                  replace("_field", field).\
                  replace("_value", value)
  return format_string

#Function of generating grid event case
def GenGridEventCase(condition, field):
  format_string = Template_GridEvents_Case.replace("_condition", condition).\
                  replace("_field", field).\
  return format_string

#Function of generating grid event item
def GenGridEventItem(condition, field):
  format_string = Template_GridEvents_Item.replace("_condition", condition).\
                  replace("_field", field).\
  return format_string

def genVbTemplate(info, part)
  format_string = ""

  ## extract related fields
  ## branching logic is not considered here
  field_name     = info[0]        # name
  field_choices  = info[5]        # data options
  field_branch   = info[11]

  # target table name
  target_table = info[1]

  # Flags
  choice_exist = False
  logic_exist = False

  # check "|" symbol
  sym_index = field_choices.find("|")

  # Branch logic exits
  if regex_branch_logic.match(field_branch):
    logic_exist = True
    if sym_index > -1:
      choice_exist = True

  #
  # (4) generate the choice string
  #
  choicestr = ""
  # extract the integers
  if need_check_choice:
    #integer list
    list_int = []

    # extract integers out from field_choices
    sepintlist = field_choices.split('|')

    for item in sepintlist:
      # extract the 1st integer in each item
      found_int = re.search("\d+", item)
      list_int.append(found_int.group())

    pipe_int = ""
    for items in list_int:
      pipe_int = pipe_int + items + ","
    # remove the last symbol ","
    pipe_int = pipe_int[:-1]
    choicestr = field_name + " IN (" + pipe_int + ")"

  #
  # (5) generate the range string
  #
  rangestr = ""
  if need_check_range:
    rangestr = field_name + " between " + minv + " and " + maxv

  #
  # (6) produce the overall condition string
  #
  if need_check_logic: 
    fieldstr = regex_branch_logic.match(field_branch).group(1).upper() 
    fieldvalue = regex_branch_logic.match(field_branch).group(2)
    condstr = "(" + fieldstr + "=" + fieldvalue            
    if choicestr:
      condstr += " AND " + "(" + choicestr + ")"
    if rangestr:
      condstr += " AND " + "(" + rangestr + ")"
    condstr += ") OR (" + fieldstr + "<>" + fieldvalue + " AND " + \
               fieldstr + " = NULL )"
  else:
    if choicestr and rangestr:
      condstr = "(" + choicestr + ")" + " AND " + "(" + rangestr + ")"
    elif choicestr:
      condstr = choicestr
    elif rangestr:
      condstr = rangestr
  #
  # (7) format the output string
  #
  if not need_check:
    format_string = Template_No_Constraint.replace('name', field_name)
    format_string = format_string.replace('type', FType)
    format_string = format_string.replace('null_str', null_str)

  if need_check:
    format_string = Template_Constraint.replace('fieldname', field_name)
    format_string = format_string.replace('type', FType)
    format_string = format_string.replace('null_str', null_str)
    format_string = format_string.replace('tablename', target_table.upper())
    # replace the conditions
    format_string = format_string.replace('conditions', condstr)

  return format_string


usage_str = "Usage: ./[script name] [path to data dictionary csv] " \
            "[target table]"

def main():

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
  o_fname = "./sql_output.txt"
  o_file = open(o_fname, "w")

  # look at the second column, find the right table to work on
  # You can specify which table to work on !!!
  for row in file:
    tablename = row[1].strip()
    if tablename == target_table:
      row_temp = GenVbTemplate(row, part)

      # output the row_temp to the text file
      o_file.write(row_temp)
      o_file.write("\n")

  # close output file
  o_file.close()

  #
  print "End program.\n",\
    "The decimal cases are only handled when there are obvious "\
    "decimal number in the data dictionary.\n"\
    "Most of the case are not considered here.\n",\
    "You still need to manually fix the output."

  return 0



if __name__ == '__main__':
  main()


