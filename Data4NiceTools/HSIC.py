#! /usr/bin/env python

import numpy as np
import pandas as pd
import sys
import csv
import sklearn.metrics
import collections
import matplotlib.pyplot as plt

def HSIC_rbf(X, Y, sigma):
  if (X.shape[0] != Y.shape[0]): 
    print 'Error : size of X and Y must be equal'
    return
  n = X.shape[0]
  if len(X.shape) == 1: X = X.reshape((n,1))
  if len(Y.shape) == 1: Y = Y.reshape((n,1))

  gamma = 1.0/(2*sigma*sigma)
  xK = sklearn.metrics.pairwise.rbf_kernel(X, Y, gamma=gamma)
  yK = sklearn.metrics.pairwise.rbf_kernel(Y, gamma=gamma)
  H = np.eye(n) - (1.0/n)*np.ones((n,n))
  C = 1.0/((n-1)*(n-1))

  HSIC = C*np.sum((xK.dot(H)).T*yK.dot(H))

  return HSIC

def HSIC(raw_data_file):
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

    X = np.array(vector)
    Y = np.array(label)
    result = HSIC_rbf(X, Y, 1)# / HSIC_rbf(X, X, 1)
    results[column].append(result)
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
  plt.ylabel('HSIC Correlation Results')
  
  plt.grid()
  plt.xticks(index + bar_width, feature_list, rotation='vertical')
  #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
  #           ncol=3, mode="expand", borderaxespad=0.)
  plt.tight_layout()
  plt.savefig('hsic.png', format='png', bbox_inches='tight')


def main():
  print ("Start program.")

  if len(sys.argv) < 2:
    print "Too few arguments"
    print "Please specify the raw data file."
    sys.exit()

  filename = sys.argv[1]
  HSIC(filename)

  print ("End program.")
  return 0

if __name__ == '__main__':
  main()


