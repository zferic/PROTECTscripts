#! /usr/bin/python

import sys
import re

if len(sys.argv) < 3:
  print "No input files to check"
  print "Usage: ./checkDataType.py [path to xsd file] [path to sql file]"
  print "Two file will be generated, further comparison is needed"
  exit()

xsd_filename = sys.argv[1]
sql_filename = sys.argv[2]

fn_xsd = open(xsd_filename, 'r')
fn_sql = open(sql_filename, 'r')
fn_xsd_results = open('xsd_type_results.txt', 'w')
fn_sql_results = open('sql_type_results.txt', 'w')

regex_xsd_name = re.compile(r'\s*<xs:element name="(\w+)"(?:\s+nillable="(?:true|false)")?>.*')
regex_xsd_type = re.compile(r'\s*<xs:restriction base="xs:(\w+)">.*')
regex_xsd_name_type = re.compile(r'\s*<xs:element name="(\w+)"\s+type\s*="xs:(\w+)"\s+nillable="(?:true|false)">.*')
xsd_name = ""
xsd_type = ""
for content in fn_xsd.readlines():
  if regex_xsd_name.match(content):
    xsd_name = regex_xsd_name.match(content).group(1)
  if regex_xsd_type.match(content):
    xsd_type = regex_xsd_type.match(content).group(1)
  if regex_xsd_name_type.match(content):
    xsd_name = regex_xsd_name_type.match(content).group(1)
    xsd_type = regex_xsd_name_type.match(content).group(2)
  if xsd_name and xsd_type:
    fn_xsd_results.write(xsd_name.upper() + "  " + xsd_type + "\n")
    xsd_name = ""
    xsd_type = ""

regex_sql_name_type = re.compile(r'(\w+) (\w+)\(?\d*,?\s?\d*\)? NULL,')
regex_sql_type = re.compile(r'')
sql_name = ""
sql_type = ""
for content in fn_sql.readlines():
  if regex_sql_name_type.match(content):
    sql_name = regex_sql_name_type.match(content).group(1)
    sql_type = regex_sql_name_type.match(content).group(2)
    if sql_type == "INT":
      print_type = "integer"
    if sql_type == "DATE":
      print_type = "date"
    if sql_type == "TIME":
      print_type = "time"
    if sql_type == "DECIMAL":
      print_type = "decimal"
    if sql_type == "NVARCHAR":
      print_type = "string"
    fn_sql_results.write(sql_name.upper() + "  " + print_type + "\n")

fn_xsd.close()
fn_sql.close()
fn_xsd_results.close()
fn_sql_results.close()


