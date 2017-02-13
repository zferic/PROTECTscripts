#! /bin/bash

if [ $# -lt 1 ]; then
  echo "There should be one argument: The data dictionary "
  exit
fi

DD_CSV=$1

echo "Data dictionary CSV file" $DD_CSV

FORM=("gestational_age_medical_record" "first_trimester_scan" "anatomy_scan" "edd_confirmation")

SCRIPT=./csv_manipulation.py

if [ -r $SCRIPT ]; then
  for form in "${FORM[@]}"; do
    $SCRIPT extract $DD_CSV $form
    $SCRIPT refine $form".csv"
  done
else
  echo "Script doesn't exist"
  exit 1
fi
