#! /usr/bin/python
# This script adds one study ID column to original EDD error log in HTML format
# Two input files are needed:
# 1) The original EDD error log generated from Equis
# 2) The export data file where the relation between line_number and study_id
#    can be obtained
# The output would be a new HTML report with fixed name "finalReport.html"

import sys
import re
import csv

if len(sys.argv) < 3:
  print "No input files to check"
  print "Usage: ./[script] [path to original html report file] " \
        "[path to export file]"
  print "Two file will be generated, further comparison is needed"
  exit()

regex_line_number = re.compile(r"^<td align='right'> (\d+) <\/td>.*")
regex_header = re.compile(r"(?:<th align='left'>\w+<\/th>)+<\/tr>")

html_report_filename = sys.argv[1]
export_data_filename = sys.argv[2]

fn_html_report = open(html_report_filename, 'rb')
fn_export_data = open(export_data_filename, 'rb')

fn_final_report = open("finalReport.html", "wb")
export_data = csv.reader(fn_export_data)

study_id = []
for row in export_data:
  study_id.append(row[0])

modified_header = "<th align='left'>Table</th><th align='left'>Line</th>"\
                  "<th align='left'>StudyID</th>"\
                  "<th align='left'>Column</th><th align='left'>Value</th>"\
                  "<th align='left'>Message</th><th align='left'>Type</th></tr>"\
                  "\n"

for content in fn_html_report:
  if regex_header.match(content):
    fn_final_report.write(modified_header)
  else:
    fn_final_report.write(content) 
  if regex_line_number.match(content):
    line_number = int(regex_line_number.match(content).group(1)) - 1
    fn_final_report.write("<td align='right'> " + str(study_id[line_number])\
                           +" </td>\n")

fn_final_report.close()
fn_html_report.close()
fn_export_data.close()

