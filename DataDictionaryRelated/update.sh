#! /bin/sh

if [ $# -lt 3 ]; then
  echo "There should be two arguments. 1) Original XML file 2) Resulted XML file"
  echo "3) CSV data dictionary file"
  exit
fi

# Proprocessing current XML file
# (1) Keep all the field name consisten with that in the data dictionary
#     sed -i -e 's/<fieldName>\([[:upper:]]\+\)/<fieldName>\L\1/' <target>.xml
#     sed -i -e 's/<fieldName>\([[:upper:]]\+_\?[[:upper:]]\+\)/<fieldName>\L\1/' <target>.xml
# (2) Remove all the ID field, e.g formId sectionId etc.
#     sed -i -e '/<\w\+Id>/d' <target>.xml

echo "Start Preprocessing..."
if [ -r $1 ]; then
  ORIGINAL_XML=$1
fi

RESULT_XML=$2

if [ -r $3 ]; then
  DD_CSV=$3
fi

echo "Original XML file: $ORIGINAL_XML"
echo "Result XML file $RESULT_XML" 
echo "Data dictionary CSV file" $DD_CSV

sed -i -e 's/<fieldName>\([[:upper:]]\+\)/<fieldName>\L\1/' $ORIGINAL_XML
sed -i -e 's/<fieldName>\([[:upper:]]\+_\?[[:upper:]]\+\)/<fieldName>\L\1/' $ORIGNAL_XML

echo "Upper case conversion DONE(Further manual check is still needed)"

sed -i -e '/<\w\+Id>/d' $ORIGINAL_XML

echo "ID fields remove DONE"

# Run the python script under same director
# ./checkUpdateDD.py <data dictionary file> <original xml file> <temp xml file>

SCRIPT=./checkUpdateDD.py
if [ -r $SCRIPT ]; then
  $SCRIPT $DD_CSV $ORIGINAL_XML temp.xml
else
  echo "Script doesn't exist"
  exit 1
fi

# Finalize the XML format
# (1) Remove the final output file if there is one with same name
#     rm result.xml
# (2) Regularize the XML format by using xmllint
#     xmllint --encode utf8 --format <temp xml file> > <result xml file>
# (3) Further regularize the XML format
#     sed -i -e "s/<\(\w\+\)\/>/<\1 \/>/g" <result xml file>

rm -f $RESULT_XML

xmllint --encode utf8 --format temp.xml > $RESULT_XML

sed -i -e "1d" $RESULT_XML
sed -i -e "s/<\(\w\+\)\/>/<\1 \/>/g" $RESULT_XML

rm temp.xml

echo "Format finalize DONE"
echo "Don't forget to manually check the difference between original xml and updated one"
# Don't forget to manually check the difference between original xml and
# updated one
