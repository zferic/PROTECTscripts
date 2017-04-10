#! /usr/bin/env python

import numpy as np
import pandas as pd
import sys
import csv
from sklearn.metrics.cluster import normalized_mutual_info_score
import collections
import matplotlib.pyplot as plt

def NMI(raw_data_file):
  data = pd.read_csv(raw_data_file)
  raw_label = data['PPTERM'].tolist()
  data.drop('PPTERM', axis=1, inplace=True)
  results = collections.OrderedDict()
  for column in data.columns:
    results[column] = []
    vector = []
    label = []
    null_flags = data[column].isnull().tolist()
    for i in range(len(null_flags)):
      if null_flags[i] == False:
        vector.append(float(data[column][i]))
        label.append(float(raw_label[i]))
    results[column].append(normalized_mutual_info_score(np.array(vector),
                                                np.array(label)))
  print results
  print len(results)
  feature_list = []
  correlation_results_list = []
  for column in results:
    feature_list.append(column)
    correlation_results_list.append(results[column][0])
  n_groups = len(results) 
  opacity = 0.8
  index = np.arange(n_groups)
  
  bar_width = 0.35
  plt.figure(1)
  fig, ax = plt.subplots()
  rects1 = plt.bar(index, correlation_results_list, bar_width,
                   alpha=opacity,
                   color='b')
  
  plt.xlabel('Fields')
  plt.ylabel('Correlation Results')
  
  plt.grid()
  plt.xticks(index + bar_width, feature_list, rotation='vertical')
  #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
  #           ncol=3, mode="expand", borderaxespad=0.)
  plt.tight_layout()
  plt.savefig('nmi.png', format='png', bbox_inches='tight')


def main():
  print ("Start program.")

  if len(sys.argv) < 2:
    print "Too few arguments"
    print "Please specify the raw data file."
    sys.exit()

  filename = sys.argv[1]
  NMI(filename)

  print ("End program.")
  return 0

if __name__ == '__main__':
  main()


