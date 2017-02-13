#! /bin/bash

if [ $# -lt 1 ]; then
  echo "There should be one argument: The data dictionary "
  exit
fi

DD_CSV=$1

echo "Data dictionary CSV file" $DD_CSV

FORM=("initial_screening" "consent_form" "first_visit" "med_rec_v1" "inhome_visit" 
      "inhome_visit_2nd_part" "geographical_coordinates" "food_frequency" "med_rec_v3"
      "product_use" "status_participante" "birth" "postpartum_data_abstraction"
      "postpartum_interview")

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
