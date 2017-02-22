import pypyodbc
import collections
import csv
import matplotlib.pyplot as plt
import numpy as np

username = ""
password = ""
connection = pypyodbc.connect('Driver={SQL Server};'
                                'Server=129.10.52.119;'
                                'Database=PROTECT_E;'
                                'uid='+username+';pwd='+password)
cursor = connection.cursor()

formfile = csv.reader(open("AllFromsInDataBase.csv", "r", encoding="utf8"))
total_count = 0
for row in formfile:
    table = row[0]
    SQLCommand = ("SELECT COUNT(*) FROM " + table)
    cursor.execute(SQLCommand)
    num_row = cursor.fetchone()
    SQLCommand = ("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '" + table + "'")
    cursor.execute(SQLCommand)
    num_col = cursor.fetchone()
    total_count += num_row[0] * num_col[0]

print ("Number Of Records: ", total_count)

human_subject_table_list = ["dt_screening", "dt_consent", "dt_first_visit", "dt_medrec_v1",
              "dt_secondvisit_1stpart", "dt_secondvisit_2ndpart", "dt_thirdvisit",
              "dt_geo_coordinates", "dt_foodfrequency", "dt_medrec_v3", "dt_product_use",
              "dt_postpartum_interv", "dt_gestational_age_medical_record", "dt_first_trimester_scan",
              "dt_anatomy_scan", "dt_edd_confirmation"]
total_count_human_subject = 0
total_count_human_subject_fields = 0
for table in human_subject_table_list:
    SQLCommand = ("SELECT COUNT(*) FROM " + table)
    cursor.execute(SQLCommand)
    num_row = cursor.fetchone()
    SQLCommand = ("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '" + table + "'")
    cursor.execute(SQLCommand)
    num_col = cursor.fetchone()
    total_count_human_subject_fields += num_col[0]
    total_count_human_subject += num_row[0] * num_col[0]

print ("Number Of Fields in human subject data: ", total_count_human_subject_fields)
print ("Number Of Records in human subject data: ", total_count_human_subject)

site_contaminant_detected_file = csv.reader(open("siteContaminantDetected.csv", "r", encoding="utf8"))
site_contaminant_detected_list = []
for row in site_contaminant_detected_file:
    site_contaminant_detected_list.append(row[0])

wellsite_current_file = csv.reader(open("wellsite_Current_082016.csv", "r", encoding="utf8"))
wellsite_hist_file = csv.reader(open("wellsite_Hist_082016.csv", "r", encoding="utf8"))

current_header = next(wellsite_current_file)
hist_header = next(wellsite_hist_file)

site_id_list = []
num_wellsite_with_contaminant = 0
for row in wellsite_current_file:
    site_id = row[0]
    if site_id not in site_id_list:
        site_id_list.append(site_id)
    if site_id in site_contaminant_detected_list:
        num_wellsite_with_contaminant += 1

for row in wellsite_hist_file:
    site_id = row[0]
    if site_id not in site_id_list:
        site_id_list.append(site_id)

print ("Number of Well Site: ", len(site_id_list))
print ("Number of Well Site with contaminant: ", num_wellsite_with_contaminant)

tapwatersite_current_file = csv.reader(open("tapwatersite_Current_082016.csv", "r", encoding="utf8"))

current_header = next(tapwatersite_current_file)

tapwatersite_id_list = []
num_tapwatersite_with_contaminant = 0
for row in tapwatersite_current_file:
    site_id = row[0]
    if site_id not in tapwatersite_id_list:
        tapwatersite_id_list.append(site_id)
    if site_id in site_contaminant_detected_list:
        num_tapwatersite_with_contaminant += 1

print ("Number of Tap Water Site: ", len(tapwatersite_id_list))
print ("Number of Tap Water Site with contaminant: ", num_tapwatersite_with_contaminant)


SQLCommand = ("SELECT DISTINCT SYS_LOC_CODE FROM dt_spring_site")
cursor.execute(SQLCommand)
spring_site_id = cursor.fetchall()

num_springsite_with_contaminant = 0
for site_id in spring_site_id:
    if site_id in site_contaminant_detected_list:
        num_springsite_with_contaminant += 1
print ("Number of Spring Site with contaminant: ", num_springsite_with_contaminant)

connection.close()
