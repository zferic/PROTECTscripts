# This script has to be used on Windows

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

table_list = ["dt_screening", "dt_consent", "dt_first_visit", "dt_medrec_v1",
              "dt_secondvisit_1stpart", "dt_secondvisit_2ndpart", "dt_thirdvisit",
              "dt_geo_coordinates", "dt_foodfrequency", "dt_medrec_v3", "dt_product_use",
              "dt_postpartum_interv", "dt_gestational_age_medical_record", "dt_first_trimester_scan",
              "dt_anatomy_scan", "dt_edd_confirmation"]

cohort_list = []
cohortfile = csv.reader(open("500cohort.csv", "r", encoding="utf8"))
header = next(cohortfile)
for row in cohortfile:
    cohort_list.append(int(row[0]))

total_num = 500
if len(cohort_list) != total_num:
    print ("Number of participants: Wrong!!!")
    exit()

participants_table_dict = collections.OrderedDict()
table_participants_dict = collections.OrderedDict()
table_fields_dict = collections.OrderedDict()
for table in table_list:
    print ("In ", table)
    SQLCommand = ("SELECT SYS_LOC_CODE FROM " + table)
    cursor.execute(SQLCommand)

    if table not in table_participants_dict:
        table_participants_dict[table] = []
    
    current_study_id = cursor.fetchone()
    while current_study_id:
        key = int(current_study_id[0])
        if key not in cohort_list:
            current_study_id = cursor.fetchone()
            continue
        if key not in participants_table_dict:
            participants_table_dict[key] = []
        if table not in participants_table_dict[key]:
            participants_table_dict[key].append(table)

        table_participants_dict[table].append(key)

        current_study_id = cursor.fetchone()

    SQLCommand = ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '" + table + "'")
    cursor.execute(SQLCommand)
    table_fields_dict[table] = []
    current_field = cursor.fetchone()
    while current_field:
        field = current_field[0]
        table_fields_dict[table].append(field)
        current_field = cursor.fetchone()

# 1 Print general information
num_total_participants = len(participants_table_dict)
print ("Number of total participants", num_total_participants)
print ("Number of total forms", len(table_list))

# 2 Print the distribution of number of participants based on their number of finished form
##distribution_finished_forms = collections.OrderedDict()
##for participant in participants_table_dict:
##    num_forms_finished = len(participants_table_dict[participant])
##    if num_forms_finished not in distribution_finished_forms:
##        distribution_finished_forms[num_forms_finished] = 1
##    else:
##        distribution_finished_forms[num_forms_finished] += 1

table_num_participants_in_500 = []
for table in table_participants_dict:
    table_num_participants_in_500.append(len(set(table_participants_dict[table])))
print (table_num_participants_in_500)

##n_groups = len(table_num_participants_in_500)
##
##opacity = 0.8
##index = np.arange(n_groups) * 2

##def autolabel(rects):
##    """
##    Attach a text label above each bar displaying its height
##    """
##    for rect in rects:
##        height = rect.get_height()
##        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
##                '%d' % float(height),
##                ha='center', va='bottom')
##
##bar_width = 1
##plt.figure(1)
##fig, ax = plt.subplots()
##ax.set_title('Number of Recorded 500 Cohorts Participants')
##ax.set_ylim(0, 700)
##rects = plt.bar(index + bar_width, table_num_participants_in_500, bar_width,
##                 alpha=opacity,
##                 color='b')
##autolabel(rects)
##
##plt.xlabel('Forms')
##plt.ylabel('Number of Recorded 500 Cohorts Participants')
##
##plt.grid()
##plt.xticks(index + bar_width, table_list, rotation='vertical')
##plt.tight_layout()
##plt.savefig('number_of_recorded_500participants.png', format='png', bbox_inches='tight')

fields_file = csv.reader(open("fieldsNeedToBeConsidered.csv", "r", encoding="utf8"))


# 3&4 Print the number of valid fields by each participants and the percentage of valid participants by each field


number_finished_fields = collections.OrderedDict()
number_finished_fields_per_form = collections.OrderedDict()
number_finished_participants = collections.OrderedDict()
number_finished_participants_per_form = collections.OrderedDict()
valid_fields_number = 0
valid_fields_number_per_form = collections.OrderedDict()
for table in table_list:
    number_finished_fields_per_form[table] = collections.OrderedDict()
    number_finished_participants_per_form[table] = collections.OrderedDict()
    valid_fields_number_per_form[table] = 0

for row in fields_file:
    current_table = row[0]
    current_field = row[1]
    if current_field not in table_fields_dict[current_table]:
        continue
    else:
        valid_fields_number += 1
        valid_fields_number_per_form[current_table] += 1

    # Create dict for number of participants per fields
    if current_field not in number_finished_participants:
        number_finished_participants[current_field] = 0
    if current_field not in number_finished_participants_per_form[current_table]:
        number_finished_participants_per_form[current_table][current_field] = 0

    for study_id in cohort_list:
        SQLCommand = ("SELECT " + current_field + " FROM " + current_table + " WHERE SYS_LOC_CODE=" + "'" + str(study_id) + "'" )
        cursor.execute(SQLCommand)

        # Create dict for number of fields per participants
        if study_id not in number_finished_fields:
            number_finished_fields[study_id] = 0
        if study_id not in number_finished_fields_per_form[current_table]:
            number_finished_fields_per_form[current_table][study_id] = 0
        current_content = cursor.fetchone()
        if current_content != None:
            if current_content[0] != None:
                number_finished_fields[study_id] += 1
                number_finished_participants[current_field] += 1
                number_finished_fields_per_form[current_table][study_id] += 1
                number_finished_participants_per_form[current_table][current_field] += 1
    

f = open("num_of_completed_fields_all.csv", "w", newline='')
writefile = csv.writer(f)
total_fields_num = valid_fields_number
print ("Total fields number: ", total_fields_num)
for study_id in number_finished_fields:
    row = []
    row.append(str(study_id))
    #number_finished_fields[study_id] = float(number_finished_fields[study_id]) * float(100) / float(total_fields_num)
    row.append(str(number_finished_fields[study_id]))
    writefile.writerow(row)
f.close()

for table in number_finished_fields_per_form:
    print (table, " : ", valid_fields_number_per_form[table])
    f = open("num_of_completed_fields_" + table + ".csv", "w", newline='')
    writefile = csv.writer(f)
    for study_id in number_finished_fields_per_form[table]:
        row = []
        row.append(str(study_id))
        #number_finished_fields[study_id] = float(number_finished_fields[study_id]) * float(100) / float(total_fields_num)
        row.append(str(number_finished_fields_per_form[table][study_id]))
        writefile.writerow(row)
    f.close()

f = open("percentage_of_completed_participants_all.csv", "w", newline='')
writefile = csv.writer(f)
total_fields_num = valid_fields_number
for field in number_finished_participants:
    row = []
    row.append(field)
    number_finished_participants[field] = float(number_finished_participants[field]) * float(100) / float(total_num)
    row.append(str(number_finished_participants[field]))
    writefile.writerow(row)
f.close()

for table in number_finished_participants_per_form:
    f = open("percentage_of_completed_participants_" + table + ".csv", "w", newline='')
    writefile = csv.writer(f)
    for field in number_finished_participants_per_form[table]:
        row = []
        row.append(field)
        number_finished_participants_per_form[table][field] = float(number_finished_participants_per_form[table][field]) * float(100) / float(total_num)
        row.append(number_finished_participants_per_form[table][field])
        writefile.writerow(row)
    f.close()

connection.close()
