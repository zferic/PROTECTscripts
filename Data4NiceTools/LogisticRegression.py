#! /usr/bin/env python

import numpy as np
import pandas as pd
import sys
import csv
import collections
import matplotlib.pyplot as plt
from sklearn import linear_model


field_list = ['WTPREPREG', 'FVPREGSTWT', 'FVCURRWT', 'MR1WGHTLBR', 'MR1HCT', \
              'MR1PLTS', 'MR1NEUTRPH', 'MR1LYMPHS']

def Run(raw_data_file):
  data = pd.read_csv(raw_data_file)
  raw_label = data['PPTERM'].tolist()
  data.drop('PPTERM', axis=1, inplace=True)
  results = collections.OrderedDict()
  num_features = len(field_list)
  num_samples = len(data.index)
  samples = []
  labels = []
  for i in data.index:
    sample = []
    for column in field_list:
      if pd.isnull(data[column][i]):
        sample = []
        break
      sample.append(data[column][i])
    if len(sample) > 0:
      samples += sample
      labels.append(raw_label[i])
  num_samples_final = len(samples) / num_features
  x = np.array(samples)
  x = np.reshape(x, (num_samples_final, num_features))
  y = np.array(labels)
  num_test_samples = 50
  num_training_samples = num_samples_final - num_test_samples
  logreg = linear_model.LogisticRegression()
  logreg.fit(x[:num_training_samples], y[:num_training_samples])
  prediction = logreg.predict(x[num_training_samples:])
  print "Overall sample: " + str(num_samples_final)
  print "Prediction: "
  print prediction
  print "Label:"
  print y[num_training_samples:]

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


