#! /bin/sh

# Proprocessing current XML file
# (1) Keep all the field name consisten with that in the data dictionary
#     sed -i -e 's/<fieldName>\([[:upper:]]\+\)/<fieldName>\L\1/' <target>.xml
#     sed -i -e 's/<fieldName>\([[:upper:]]\+_\?[[:upper:]]\+\)/<fieldName>\L\1/' <target>.xml
# (2) Remove all the ID field, e.g formId sectionId etc.
#     sed -i -e '/<\w\+Id>/d' <target>.xml


# Run the python script under same director
# ./checkUpdateDD.py <data dictionary file> <original xml file> <output xml file>

# Finalize the XML format
# (1) Remove the final output file if there is one with same name
#     rm result.xml
# (2) Regularize the XML format by using xmllint
#     xmllint --encode utf8 --format <output xml file> > result.xml
# (3) Further regularize the XML format
#     sed -i -e "s/<\(\w\+\)\/>/<\1 \/>/g" result.xml
