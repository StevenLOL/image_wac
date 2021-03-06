# coding: utf-8

'''
Model 11

refcoco + grex, 90/10 + refcoco_splits, no rel, min 40, logregL1, 5, random
'''

from __future__ import division
import numpy as np
import gzip
import cPickle as pickle
import json
from time import strftime

import pandas as pd

from sklearn import linear_model

import sys
sys.path.append('../../Utils')
sys.path.append('..')
from utils import filter_by_filelist

from train_model import train_model
from train_model import filter_relational_expr, wordlist_by_criterion


####### The training pipeline ########

print strftime("%Y-%m-%d %H:%M:%S")


## some parameters are fixed / documented here
##  processing steps still need to be triggered explicitly

model = {
    'rcorp': 'refcoco+grex',
    'rel':   'excl',
    'wrdl':  'min',
    'wprm':  40,
    'clsf':  'logreg-l1',
    'nneg':  5,
    'nsrc':  'random',
    'notes': ''
}

basename = 'model11_rg5r'


### I. Get the refexp data (the refdf)

with gzip.open('../../Preproc/PreProcOut/refcoco_refdf.pklz', 'r') as f:
    refdf_b = pickle.load(f)
with gzip.open('../../Preproc/PreProcOut/grex_refdf.pklz', 'r') as f:
    refdf_c = pickle.load(f)

refdf = pd.concat([refdf_b, refdf_c])

### II. Set the split to use

with open('../../Preproc/PreProcOut/refcoco_splits.json', 'r') as f:
    splits = json.load(f)


tlist = splits['train']

refdf_t = filter_by_filelist(refdf, tlist)

### III. Preprocess: remove relational expressions from training

refdf_tr = filter_relational_expr(refdf_t)

### IV. Set list of words to train

wordlist = wordlist_by_criterion(refdf_tr, model['wrdl'], model['wprm'])

### V. Get the region features

X = np.load('../../ExtractFeats/ExtrFeatsOut/mscoco.npz')
X = X['arr_0']


### VI. And... train away!

clsf = train_model(refdf_tr, X, wordlist,
                   (linear_model.LogisticRegression, {'penalty':'l1'}),
                   nneg=model['nneg'], nsrc=model['nsrc'])

with gzip.open('../TrainedModels/' + basename + '.pklz', 'w') as f:
    pickle.dump(clsf, f)

with open('../TrainedModels/' + basename + '.json', 'w') as f:
    json.dump(model, f)

print strftime("%Y-%m-%d %H:%M:%S")
