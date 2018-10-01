# -*- coding: utf-8 -*-

__author__="E.M.G."

#--------------------------------------------------------------------#
#-- Author: Eva Martinez Garcia                                    --#
#--------------------------------------------------------------------#

from io import open
import unicodedata
import string
import re
import random
import argparse,codecs
import os, sys
import numpy as np 

p = argparse.ArgumentParser(prog="partition", description="Extract a random partition of train,dev and test set from parallel data files.")
p.add_argument('-src',   help="Source training corpus.", required=True)
p.add_argument('-tgt',  type=str, help="Target training corpus.", required=True)

p.add_argument('-ntrain', type=int,required=True)
p.add_argument('-ndev', type=int,required=True)
p.add_argument('-ntest', type=int,required=True)


opt = p.parse_args()
src_sents=[]
tgt_sents=[]
with codecs.open(opt.src, encoding='utf-8', mode = 'r') as src:
	with codecs.open(opt.tgt, encoding='utf-8', mode = 'r') as tgt:
		for elements in zip(src,mt,pe,hter):
			src_sents.append(elements[0])
			tgt_sents.append(elements[1])
		
assert len(src_sents) == len(tgt_sents)

num_sents = len(src_sents)
assert opt.ntrain+opt.ntest+opt.ndev == num_sents
rndm_sents = np.random.permutation(num_sents)

src_dev=[]
tgt_dev=[]
src_train=[]
tgt_train=[]
src_test=[]
tgt_test=[]

for i,e in enumerate(rndm_sents) :

	if i<opt.ntrain :
		src_train.append(src_sents[e])
		tgt_train.append(mt_sents[e])
	
	elif i>=opt.ntrain and i< opt.ntrain+opt.ndev :
		src_dev.append(src_sents[e])
        tgt_dev.append(mt_sents[e])
        
	elif i>=opt.ntrain+opt.ndev and i<opt.ntrain+opt.ndev+opt.ntest:
		src_test.append(src_sents[e])
        tgt_test.append(mt_sents[e])
        
#debug:        
#print(len(src_test))
#print(len(src_dev))
#print(len(src_train))

with codecs.open(opt.src+'.train', encoding='utf-8', mode = 'w') as src_t:
	with codecs.open(opt.tgt+'.train', encoding='utf-8', mode = 'w') as tgt_t:	
		for i,t in enumerate(zip(src_train,tgt_train)):
			src_t.write(t[0])
			tgt_t.write(t[1])
			
with codecs.open(opt.src+'.dev', encoding='utf-8', mode = 'w') as src_d:
	with codecs.open(opt.tgt+'.dev', encoding='utf-8', mode = 'w') as mt_d:      
    	for i,t in enumerate(zip(src_dev,mt_dev,pe_dev,hter_dev)):
	    		src_d.write(t[0])
        	    tgt_d.write(t[1])
            			

with codecs.open(opt.src+'.test', encoding='utf-8', mode = 'w') as src_te:
    with codecs.open(opt.tgt+'.test', encoding='utf-8', mode = 'w') as tgt_te:  
        for i,t in enumerate(zip(src_test,mt_test,pe_test,hter_test)):
        	    src_te.write(t[0])
            tgt_te.write(t[1])
            