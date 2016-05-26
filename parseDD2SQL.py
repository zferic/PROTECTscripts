#! /usr/bin/python

import csv
import re
import sys

if len(sys.argv) < 2
  print "No input data dictionary"
  print "Usage: ./parseDD2SQL [path to data dictionary]"
  exit()

rownum = 0
regx_char_limit = re.compile(r"(\d+) [cC]haracters")
regx_branch_logic = re.compile(r"\[(\w+_?\w+)\]\s?=\s?'(\d+)'")
regx_choice = re.compile(r"(\d+),")
with open(sys.argv[1], "rb") as dd_csv:
  dd_reader = csv.reader(dd_csv)
  for row in dd_reader:
    statement1 = ""
    statement2 = ""
    if rownum == 0:
      header = row
    else:
      dict_row = {}
      for i in range(len(header)):
        dict_row[header[i]] = row[i]
      if dict_row["Form Name"] == "postpartum_data_abstraction":
        # Generate first statement
        ucase_field = dict_row[header[0]].upper()
        statement1 += ucase_field
        if dict_row["Text Validation Type OR Show Slider Number"] == "date_mdy":
   	  statement1 += " DATE"
        elif dict_row["Text Validation Type OR Show Slider Number"] == "time":
          statement1 += " DATETIME"
        elif dict_row["Text Validation Type OR Show Slider Number"] == "integer":
          statement1 += " INT"
        elif dict_row["Text Validation Type OR Show Slider Number"] == "number": 
          statement1 += " INT"
        elif dict_row["Field Type"] == "radio" or dict_row["Field Type"] == "checkbox":
          statement1 += " INT"
        else:
          if regx_char_limit.match(dict_row["Field Note"]):
            char_limit = regx_char_limit.match(dict_row["Field Note"]).group(1)
            statement1 += " NVARCHAR(" + char_limit + ")"
          else:
            statement1 += " NVARCHAR(100)"
        statement1 += " NULL,"
        print statement1
        #Generate second statement
        branch_logic_str = dict_row["Branching Logic (Show field only if...)"]
        choice_str = dict_row["Choices, Calculations, OR Slider Labels"]
        min_str = dict_row["Text Validation Min"]
        max_str = dict_row["Text Validation Max"]
                
        choice_primitive = ""
        if choice_str:
          choice_primitive += "(" + ucase_field + " IN ("
          choice_number_list = []
          choice_list = choice_str.split(" | ")
          for idx in range(len(choice_list)):
            if regx_choice.match(choice_list[idx]):
              choice_primitive += regx_choice.match(choice_list[idx]).group(1)
              if idx != len(choice_list) - 1:
                choice_primitive += ","
          choice_primitive += "))"

        range_primitive = ""
        if min_str and max_str and (dict_row["Text Validation Type OR Show Slider Number"] == "integer" or dict_row["Text Validation Type OR Show Slider Number"] == "number"):
          range_primitive += "(" + ucase_field + " between " + min_str + " and " + max_str + ")"

        if branch_logic_str:                                                    
          if regx_branch_logic.match(branch_logic_str):                         
            condition_str = regx_branch_logic.match(branch_logic_str).group(1).upper()  
            condition_value = regx_branch_logic.match(branch_logic_str).group(2)
            statement2 += "CONSTRAINT POSTPARTUM_DATA_ABSTRACTION_" + ucase_field + "_CK CHECK ( (" + condition_str + "=" + condition_value            
            if choice_primitive:
              statement2 += " AND " + choice_primitive
            if range_primitive:
              statement2 += " AND " + range_primitive
            statement2 += ") OR (" + condition_str + "<>" + condition_value + " AND " + condition_str + " = NULL ) ),"
        else:
          if choice_primitive and range_primitive:
            statement2 += "CONSTRAINT POSTPARTUM_DATA_ABSTRACTION_" + ucase_field + "_CK CHECK " + choice_primitive + " AND " + range_primitive + ","
          elif choice_primitive:
            statement2 += "CONSTRAINT POSTPARTUM_DATA_ABSTRACTION_" + ucase_field + "_CK CHECK " + choice_primitive + ","
          elif range_primitive:
            statement2 += "CONSTRAINT POSTPARTUM_DATA_ABSTRACTION_" + ucase_field + "_CK CHECK " + range_primitive + ","
        if statement2:
          print statement2
        print ""

    rownum += 1



