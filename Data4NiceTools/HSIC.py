#! /usr/bin/env python

import numpy as np
import pandas as pd
import sys
import csv
import sklearn.metrics
from sklearn import preprocessing
import collections
import matplotlib.pyplot as plt

def Allocation_2_Y(allocation):
	
  N = np.size(allocation)
  unique_elements = np.unique(allocation)
  num_of_classes = len(unique_elements)
  class_ids = np.arange(num_of_classes)
  
  i = 0
  Y = np.zeros(num_of_classes)
  for m in allocation:
    class_label = np.where(unique_elements == m*np.ones(unique_elements.shape))[0]
    
    a_row = np.zeros(num_of_classes)
    a_row[class_label] = 1
    Y = np.hstack((Y, a_row))
  
  Y = np.reshape(Y, (N+1,num_of_classes))
  Y = np.delete(Y, 0, 0)

  return Y

def calc_gamma(X):
  d_matrix = sklearn.metrics.pairwise.pairwise_distances(X, metric='euclidean')
  sigma = np.median(d_matrix)
  if(sigma == 0): sigma = np.mean(d_matrix)
  gamma = 1.0/(2*sigma*sigma)
  return gamma



def HSIC(X, Y, X_kernel='Gaussian', Y_kernel='Delta'): # X is n by d, n=# of sample, d=# of features
  if (X.shape[0] != Y.shape[0]): 
    print 'Error : size of X and Y must be equal'
    exit()

  n = X.shape[0]
  if len(X.shape) == 1: X = X.reshape((n,1))
  if len(Y.shape) == 1: Y = Y.reshape((n,1))


  #import pdb; pdb.set_trace()	
  if X_kernel == 'Gaussian':
    #X = preprocessing.scale(X)
    xK = sklearn.metrics.pairwise.rbf_kernel(X, gamma=calc_gamma(X))

  elif X_kernel == 'Linear':
    xK = X.dot(X.T)
  elif X_kernel == 'Delta':
    if X.shape[1] > 1:
      print 'Error : Cannot use delta kernel for multiple column Y'
      exit()
    
    X = Allocation_2_Y(X)
    xK = X.dot(X.T)

  if Y_kernel == 'Gaussian':
    #Y = preprocessing.scale(Y)
    d_matrix = sklearn.metrics.pairwise.pairwise_distances(Y, metric='euclidean')
    sigma = np.median(d_matrix)
    if(sigma == 0): sigma = np.mean(d_matrix)
    gamma = 1.0/(2*sigma*sigma)
    gamma = 1
    
    yK = sklearn.metrics.pairwise.rbf_kernel(Y, gamma=calc_gamma(Y))
  elif Y_kernel == 'Linear':
    yK = Y.dot(Y.T)
  elif Y_kernel == 'Delta':
    if Y.shape[1] > 1:
      print 'Error : Cannot use delta kernel for multiple column Y'
      exit()
    	
    Y = Allocation_2_Y(Y)
    yK = Y.dot(Y.T)
  
  gamma = 1.0/2
  n = X.shape[0]
  xK = sklearn.metrics.pairwise.rbf_kernel(X, gamma=gamma)
  yK = sklearn.metrics.pairwise.rbf_kernel(Y, gamma=gamma)
  
  H = np.eye(n) - (1.0/n)*np.ones((n,n))
  C = 1.0/((n-1)*(n-1))
  
  #HSIC_value = C*np.trace(H.dot(xK).dot(H).dot(Y).dot(Y.T))
  HSIC_value = C*np.sum((xK.dot(H)).T*yK.dot(H))
  return HSIC_value



def Run(raw_data_file):
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
    result = HSIC(X, Y, 'Gaussian') / HSIC(X, X, 'Gaussian')
    results[column].append(result)
  print results
  print len(results)
  feature_list = []
  correlation_results_list = []
  for column in results:
    feature_list.append(column)
    correlation_results_list.append(results[column][0])
    if results[column][0] > 0.05:
      print column


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
  Run(filename)

  print ("End program.")
  return 0

if __name__ == '__main__':
  main()


