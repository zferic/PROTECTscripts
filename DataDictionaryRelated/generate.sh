#! /bin/sh

if [ $# -lt 2 ]; then
  echo "There should be two arguments. 1) Resulted XML file"
  echo "2) CSV data dictionary file"
  exit
fi

RESULT_XML=$1

if [ -r $2 ]; then
  DD_CSV=$2
fi

echo "Result XML file $RESULT_XML" 
echo "Data dictionary CSV file" $DD_CSV

# Run the python script under same director
# ./genDataDictXml.py <data dictionary file> <temp xml file>

SCRIPT=./genDataDictXml.py
TEMP=temp.xml
if [ -r $SCRIPT ]; then
  $SCRIPT $DD_CSV $TEMP
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

if [ -f $TEMP ]; then
  rm -f $RESULT_XML

  xmllint --encode utf8 --format $TEMP > $RESULT_XML

  sed -i -e "1d" $RESULT_XML
  sed -i -e "s/<\(\w\+\)\/>/<\1 \/>/g" $RESULT_XML

  rm $TEMP
  echo "Format finalize DONE"
  echo "Don't forget to manually check the difference between original xml and updated one"
fi

# Don't forget to manually check the difference between original xml and
# updated one

echo "Finished"
