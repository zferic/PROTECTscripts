# PROTECTscripts

This project consists of python scripts helping facilitate generating format files for cleaning data from PROTECT project. Other than that, there are also several scripts with special usage

# General
This folder contains scripts for producing format files(xsd, vb and sql) purpose

# Special Usage
This folder contains scripts with multiple usages

# Regular work flow
Before taking following steps, update data dictionary through csv_manipulation.py
1. Generate xsd, sql files and code segments files according to a specific data dictionary through gen_xsd.py, gen_sql.py and gen_vb.py
2. Construct vb file through generated code segments manually
3. Check if there is inconsistency in terms of missing field or field order between data dictionary and export data through checkMissFieldAndOrder.py
4. Fix the inconsisitency in xsd file manually until fields in data dictionary and export data are completely consistent.
5. Check the mis-match between xsd and sql file by comparing two generated txt file through checkDataType.py
6. Fix the mis-match in sql file manually
