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

v1_table_list = ["dt_first_visit", "dt_medrec_v1"]
general_table_list = ["dt_biological", "dt_product_use"]
ignore_list = ["SYS_LOC_CODE", "SUBFACILITY_CODE", "FACILITY_ID", "REDCAP_EVENT_NAME", "VISITID",
               "EBATCH"]
num_table = len(v1_table_list) + len(general_table_list)
visit_id = 1

header = []
fields_list = []
table_fields_dict = collections.OrderedDict()
study_id_count_dict = collections.OrderedDict()
for table in v1_table_list:
    print ("In ", table)
    SQLCommand = ("SELECT DISTINCT SYS_LOC_CODE FROM " + table)
    cursor.execute(SQLCommand)
    
    study_id_list_from_sql = cursor.fetchall()
    for i in study_id_list_from_sql:
        study_id = int(i[0])
        if study_id not in study_id_count_dict:
            study_id_count_dict[study_id] = 1
        else:
            study_id_count_dict[study_id] += 1  

    SQLCommand = ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '" + table + "'")
    cursor.execute(SQLCommand)
    table_fields_dict[table] = []
    current_field = cursor.fetchone()
    while current_field:
        field = current_field[0]
        if field in ignore_list:
            current_field = cursor.fetchone()
            continue
        fields_list.append(field)
        table_fields_dict[table].append(field)
        current_field = cursor.fetchone()

for table in general_table_list:
    print ("In ", table)
    SQLCommand = ("SELECT DISTINCT SYS_LOC_CODE FROM " + table + " WHERE VISITID='" + str(visit_id) + "'")
    cursor.execute(SQLCommand)
    
    study_id_list_from_sql = cursor.fetchall()
    for i in study_id_list_from_sql:
        study_id = int(i[0])
        if study_id not in study_id_count_dict:
            study_id_count_dict[study_id] = 1
        else:
            study_id_count_dict[study_id] += 1  

    SQLCommand = ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '" + table + "'")
    cursor.execute(SQLCommand)
    table_fields_dict[table] = []
    current_field = cursor.fetchone()
    while current_field:
        field = current_field[0]
        if field in ignore_list:
            current_field = cursor.fetchone()
            continue
        fields_list.append(field)
        table_fields_dict[table].append(field)
        current_field = cursor.fetchone()

header.append("STUDY_ID")
for field in fields_list:
    header.append(field)
header.append("PPTERM")

study_id_list = []
for study_id in study_id_count_dict:
    if study_id_count_dict[study_id] >= num_table:
        study_id_list.append(study_id)

final_data_4_nice = collections.OrderedDict()

for study_id in study_id_list:
    if study_id not in final_data_4_nice:
        final_data_4_nice[study_id] = []
    for table in v1_table_list:
        for field in table_fields_dict[table]:
            SQLCommand = ("SELECT " + field + " FROM " + table + " WHERE SYS_LOC_CODE='" + str(study_id) + "'")
            cursor.execute(SQLCommand)
            value = cursor.fetchone()
            if value[0] != None:
                final_data_4_nice[study_id].append(value[0])
            else:
                final_data_4_nice[study_id].append("")
    for table in general_table_list:
        for field in table_fields_dict[table]:
            SQLCommand = ("SELECT " + field + " FROM " + table + " WHERE SYS_LOC_CODE='" + str(study_id) + "' AND " + "VISITID='" + str(visit_id) + "'")
            cursor.execute(SQLCommand)
            value = cursor.fetchone()
            if value[0] != None:
                final_data_4_nice[study_id].append(value[0])
            else:
                final_data_4_nice[study_id].append("")
    # Save one space for ppterm
    final_data_4_nice[study_id].append("")


# Using CSV file for now
#postpartum_file = csv.reader(open("postpartum_data.csv", "r", encoding="utf8"))
postpartum_file = csv.reader(open("postpartum_data.csv", "r"))
postpartum_header = next(postpartum_file)
study_id_idx = 0
ppterm_idx = postpartum_header.index("ppterm")
print ("index for ppterm: ", ppterm_idx)
for row in postpartum_file:
    if int(row[study_id_idx]) not in final_data_4_nice:
        continue
    final_data_4_nice[int(row[study_id_idx])][-1] = row[ppterm_idx]


f = open("v1data4nice.csv", "w", newline='')
writefile = csv.writer(f)
writefile.writerow(header)
print ("Number of participants: ", len(final_data_4_nice))
for study_id in final_data_4_nice:
    written_row = []
    written_row.append(str(study_id))
    for content in final_data_4_nice[study_id]:
        written_row.append(content)
    writefile.writerow(written_row)
f.close()


connection.close()
