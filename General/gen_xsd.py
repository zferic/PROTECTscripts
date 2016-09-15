#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gen_xsd.py
#  6/12/2015
#  Copyright 2016 shi dong <dong.sh@husky.neu.edu>
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


# for each field type, there could be multiple specific types
# For example,
#   text        :   date, char(string)
#   radio       :   integer list
#   checkbox    :   integer list
#   notes       :   char(string)

#   text->date  :   MM-DD-YYY / hh:mm / Military Time
#   text->char  :   char(200)
#   radio->integer list :   looking for '|' as separator and extract integers
#   checkbox->integer   :   same as radio
#   notes->char :   always char, using char(200) as default

start_string = \
"<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"\
"<xs:schema id=\"consent\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\"\n"\
" xmlns:edd=\"http://www.earthsoft.com/support/edp/ff\" version=\"3.0.$Revision: 25 $\"\n"\
" xmlns:msdata=\"urn:schemas-microsoft-com:xml-msdata\">\n"\
"\t<xs:element name=\"target_table\" msdata:IsDataSet=\"true\">\n"\
"\t\t<xs:annotation>\n"\
"\t\t\t<xs:appinfo>\n"\
"\t\t\t\t<edd:name>dt_target_table</edd:name>\n"\
"\t\t\t\t<edd:publisher>Northeastern University</edd:publisher>\n"\
"\t\t\t\t<edd:handler language=\"vb\" source=\"target_table\" class=\"target_tableHandler\" />\n"\
"\t\t\t</xs:appinfo>\n"\
"\t\t\t<xs:documentation>dt_target_table</xs:documentation>\n"\
"\t\t</xs:annotation>\n\n"\
"\t\t<xs:complexType>\n"\
"\t\t\t<xs:sequence>\n\n"\
"\t\t\t\t<xs:element name=\"target_table\">\n"\
"\t\t\t\t\t<xs:annotation>\n"\
"\t\t\t\t\t\t<xs:documentation>consent</xs:documentation>\n"\
"\t\t\t\t\t\t<xs:appinfo>\n"\
"\t\t\t\t\t\t\t<edd:table mode=\"create\" target=\"dt_target_table\">\n"\
"\t\t\t\t\t\t\t\t<edd:field default=\"1\" target=\"FACILITY_ID\"/>\n"\

intermediate_string = \
"\t\t\t\t\t\t\t</edd:table>\n"\
"\t\t\t\t\t\t</xs:appinfo>\n"\
"\t\t\t\t\t</xs:annotation>\n\n"\
"\t\t\t\t\t<!-- set up definition-->\n"\
"\t\t\t\t\t<xs:complexType>\n"\
"\t\t\t\t\t\t<xs:sequence>\n\n"\

end_string = \
"\t\t\t\t\t\t</xs:sequence>\n"\
"\t\t\t\t\t</xs:complexType>\n"\
"\t\t\t\t\t<!-- finish setting up definition-->\n"\
"\t\t\t\t</xs:element>\n"\
"\t\t\t</xs:sequence>\n"\
"\t\t</xs:complexType>\n\n"\
"\t</xs:element>\n"\
"</xs:schema>\n"\

# For part 1
indent_p1 = "\t\t\t\t\t\t\t\t"
mapping_string = \
indent_p1 + "<edd:field source=\"small_name\" target=\"cap_name\"/>\n"

# For part 2
indent_p2 = "\t\t\t\t\t\t\t"
Format_String = \
indent_p2 + "<xs:element name=\"_elename_\" nillable=\"true\">\n" + \
indent_p2 + "\t<xs:simpleType>\n" + \
indent_p2 + "\t\t<xs:restriction base=\"xs:string\">\n" + \
indent_p2 + "\t\t\t<xs:length value=\"200\" />\n" + \
indent_p2 + "\t\t</xs:restriction>\n" + \
indent_p2 + "\t</xs:simpleType>\n" + \
indent_p2 + "</xs:element>\n"

Format_Date = \
indent_p2 + "<xs:element name=\"_elename_\" type=\"xs:date\" nillable=\"true\">\n" + \
indent_p2 + "</xs:element>\n"

Format_Time = \
indent_p2 + "<xs:element name=\"_elename_\" type=\"xs:time\" nillable=\"true\">\n" + \
indent_p2 + "</xs:element>\n"

Format_Int_Simple = \
indent_p2 + "<xs:element name=\"_elename_\" type=\"xs:integer\" nillable=\"true\">\n" + \
indent_p2 + "</xs:element>\n"

Format_Int_Range = \
indent_p2 + "<xs:element name=\"_elename_\" nillable=\"true\">\n" + \
indent_p2 + "\t<xs:simpleType>\n" + \
indent_p2 + "\t\t<xs:restriction base=\"xs:integer\">\n" + \
indent_p2 + "\t\t\t<xs:minInclusive value=\"_min_\"/>\n" + \
indent_p2 + "\t\t\t<xs:maxInclusive value=\"_max_\"/>\n" + \
indent_p2 + "\t\t</xs:restriction>\n" + \
indent_p2 + "\t</xs:simpleType>\n" + \
indent_p2 + "</xs:element>\n"

Format_Decimal = \
indent_p2 + "<xs:element name=\"_elename_\" nillable=\"true\">\n" + \
indent_p2 + "\t<xs:simpleType>\n" + \
indent_p2 + "\t\t<xs:restriction base=\"xs:decimal\">\n" + \
indent_p2 + "\t\t\t<xs:totalDigits value=\"8\" />\n" + \
indent_p2 + "\t\t\t<xs:fractionDigits value=\"4\" />\n" + \
indent_p2 + "\t\t</xs:restriction>\n" + \
indent_p2 + "\t</xs:simpleType>\n" + \
indent_p2 + "</xs:element>\n"

Format_Decimal_Range = \
indent_p2 + "<xs:element name=\"_elename_\" nillable=\"true\">\n" + \
indent_p2 + "\t<xs:simpleType>\n" + \
indent_p2 + "\t\t<xs:restriction base=\"xs:decimal\">\n" + \
indent_p2 + "\t\t\t<xs:totalDigits value=\"16\" />\n" + \
indent_p2 + "\t\t\t<xs:fractionDigits value=\"8\" />\n" + \
indent_p2 + "\t\t\t<xs:minInclusive value=\"_min_\"/>\n" + \
indent_p2 + "\t\t\t<xs:maxInclusive value=\"_max_\"/>\n" + \
indent_p2 + "\t\t</xs:restriction>\n" + \
indent_p2 + "\t</xs:simpleType>\n" + \
indent_p2 + "</xs:element>\n"

Format_Int_Enum_part1 = \
indent_p2 + "<xs:element name=\"_elename_\" nillable=\"true\">\n" + \
indent_p2 + "\t<xs:simpleType>\n"   + \
indent_p2 + "\t\t<xs:restriction base=\"xs:integer\">\n"


Format_Int_Enum_part3 = \
indent_p2 + "\t\t</xs:restriction>\n" + \
indent_p2 + "\t</xs:simpleType>\n"  + \
indent_p2 + "</xs:element>\n"

# the first column is the data field
# to generate the xml format, we need to know
# 1) data type  2) data range
def GenMappingInfo(info, first_field_processed):
  format_string = ""

  ## extract related fields
  ## branching logic is not considered here
  field_name     = info[0]        # name

  # change to lower case
  name_low = field_name.strip().lower()
  name_upp = field_name.strip().upper()

  # remove the empty space
  name_low = name_low.strip()
  name_upp = name_upp.strip()

  format_string = mapping_string.replace('small_name', name_low)
  if not first_field_processed:
    format_string = format_string.replace('cap_name', 'SYS_LOC_CODE')
  else:
    format_string = format_string.replace('cap_name', name_upp)

  return format_string


def GenDefInfo(info):
  format_string = ""
  ## extract related fields
  ## branching logic is not considered here
  field_name     = info[0]        # name
  field_type     = info[3]        # data type
  field_choices  = info[5]        # data options
  field_note     = info[6]        # specific notes, such as date format
  field_valid    = info[7]
  field_min      = info[8]
  field_max      = info[9]


  # change to lower case
  field_name = field_name.strip().lower()

  # remove the empty space
  field_type = field_type.strip()

  ##
  ## Use previously defined format to generate the field sections
  ##

  # notes field :
  #                use the string format
  if(field_type == 'notes'):
    # replace _elename_ in Format_String with the current field_name
    format_string = Format_String.replace('_elename_', field_name)

  # text field :
  #               date format
  #               time format
  #               integer format
  #               string format
  if(field_type == 'text'):

    # date
    index_date = field_valid.find('date_mdy')

    # time
    index_time = field_valid.find('time')

    # integer
    index_int = field_valid.find('integer')
      
    # number
    index_number = field_valid.find('number')

    # decimal
    index_decimal = field_valid.find('decimal')

    # string
    n = 0

    if index_date > -1:
      n = 1
    elif index_time > -1:
      n = 2
    elif index_int > -1:
      n = 3
    elif index_number > -1:
      n = 4
    elif index_decimal > -1:
      n = 5

    
    field_min = field_min.strip()
    field_max = field_max.strip()
    regex_decimal = re.compile(r"\d+\.\d*")
    if n == 4:
      if not (regex_decimal.match(field_min) and regex_decimal.match(field_max)):
        n = 3

    if n == 1:
      format_string = Format_Date.replace('_elename_', field_name)
    elif n == 2:
      format_string = Format_Time.replace('_elename_', field_name)
    elif n == 3:
      # integer list, check min and max
      if len(field_min) == 0 and len(field_max) == 0:
        format_string = Format_Int_Simple.replace('_elename_', field_name)

      if len(field_min) > 0 and len(field_max) > 0:
        format_string = Format_Int_Range.replace('_elename_', field_name)
        format_string = format_string.replace('_min_', field_min)
        format_string = format_string.replace('_max_', field_max)
    elif n == 4 or n == 5:
      field_min = field_min.strip()
      field_max = field_max.strip()
      if len(field_min) == 0 and len(field_max) == 0:
        format_string = Format_Decimal.replace('_elename_', field_name)

      if len(field_min) > 0 and len(field_max) > 0:
        format_string = Format_Decimal_Range.replace('_elename_', field_name)
        format_string = format_string.replace('_min_', field_min)
        format_string = format_string.replace('_max_', field_max)
    else:
      format_string = Format_String.replace('_elename_', field_name)

  # radio and checkbox :
  #                   multiple choices format
  if(field_type == 'radio' or field_type == 'checkbox'):
    # integer list
    list_int = []

    # extract integers out from field_choices
    sepintlist = field_choices.split('|')

    for item in sepintlist:
      # extract the 1st integer in each item
      found_int = re.search("\d+", item)
      list_int.append(found_int.group())

    #print list_int
    format_str1 = Format_Int_Enum_part1.replace('_elename_', field_name)
    format_str3 = Format_Int_Enum_part3
    format_str2 = ""

    for i in list_int:
      format_str2 += indent_p2 + "\t\t\t<xs:enumeration value=\"" + i + "\" />\n"

    format_string = format_str1 + format_str2 + format_str3

  format_string += "\n"
  return format_string


usage_string = "[Usage] ./<script_name> <dd csv file> <target table> <command>\n"\
               "The <command> is optional and has two choice 1) map 2) def"

def main():

  if len(sys.argv) < 3:
    print "Too few argument"
    print usage_string
    sys.exit()

  if len(sys.argv) > 4:
    print "Too many. Read one csv file at at time."
    print usage_string
    sys.exit()

  command = ""
  if len(sys.argv) == 4:
    command = sys.argv[3]

  # check the arguments
  # print 'Number of arguments:', len(sys.argv), 'arguments.'
  print "program name : ", sys.argv[0]
  print "csv dd file : ", sys.argv[1]
  print "target table : ", sys.argv[2]
  if command:
    print "command : ", command
  print "Start program."


  filename = sys.argv[1]
  target_table = sys.argv[2]

  # read csv file
  file = csv.reader(open(filename, "rb"));

  # open text file to write
  o_fname = target_table + command + ".xsd"
  o_file = open(o_fname, "w")

  # look at the second column, find the right table to work on
  # You can specify which table to work on !!!
  mapping_info = ""
  definition_info = ""
  first_field_processed = False
  for row in file:
    tablename = row[1]
    tablename = tablename.strip()
    if tablename == target_table:
      # Gen mapping info
      mapping_info += GenMappingInfo(row, first_field_processed)
      # In SQL file, the first field should be mapped to SYS_LOC_CODE
      if not first_field_processed:
        first_field_processed = True
      # Gen definition info
      definition_info += GenDefInfo(row)

  # output the string
  if not command:
    start_string_modified = start_string.replace("target_table", target_table)
    o_file.write(start_string_modified)
    o_file.write(mapping_info)
    o_file.write(intermediate_string)
    o_file.write(definition_info)
    o_file.write(end_string)
  else:
    if command == "map":
      o_file.write(mapping_info)
    elif command == "def":
      o_file.write(definition_info)
    else:
      print "Illigel command: ", command
      sys.exit()

  # close output file
  o_file.close()

  #
  print "End program.\n",\
    "The decimal case is only partially considered here.\n",\
    "You still need to manually fix some output."

  return 0



if __name__ == '__main__':
  main()


