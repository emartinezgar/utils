# -*- coding: utf-8 -*-
#########################################################################
#               IDENTIFICA_SRC_TGT      DESCRIPTION                     #
#########################################################################
#AUTHOR: Eva Martinez Garcia (emartinez at lsi.upc.edu)
#FUNCTIONALITY:Script that allows us to add
#                  artificial noise to an input text.
#                  It gets the text by the  standard input
#                  and returns the output text by the standard output
#PARAMETERS: the script can be called as follow:
#               identifica_src_tgt.py
#                where the options are:
#               -h,-H,-help, 
#                without any option:    Usage message
#               -lc:                    lowercase the input text
#               -noEOS:                 delete all the end of sentence marks (.,!,?)
#               -noP:                   delete all the punctuation symbols ( ',' ,.,!,?,",',#,*,(,),[,],-,_,;,...,<,>,/,\,^,%,},{ )
#               -ngrams number:         split the text in 'number'-grams randomly
#               -addE:                  change letters randomly in the text simulating misprints
#               -NP:                    only remain the Noun Phrases of the text: we need that the text has a tree structure to find the NPs.

#########################################################################
#                               IMPORTS                                 #
#########################################################################
import sys
import random
import string
import getopt
import re
import math
from collections import defaultdict
from time import gmtime, strftime
import operator
import os #to make system calls
import freeling #need the freeling library near

########################################################################
#########################################################################
#                       FUNCTIONS DEFINITIONS                           #
#########################################################################
#########################################################################
#getoptions function
# gets the parameters indicated by the user
def getoptions():
        
        try:
                opts, args = getopt.getopt(sys.argv[1:], "ht:o:l:", ["help","target=","output=","lemma_t="])
#               opts, args = getopt.getopt(sys.argv[1:], "ht:s:a:o:l:c:r:", ["help","target=","source=","align=","output=","lemma_t=","--lemma_src=", "--corref_src="])
        except getopt.GetoptError, err:
        # print help information and exit:
                print str(err) # will print something like "option -a not recognized"
                help()
                sys.exit(2)
        return opts, args

#########################################################################
#help function
# shows the usage of the script
def help():
        print 'Usage: check_agreement.py [OPTIONS]'
        print ' options:'
        print ' -h ; --help                       Display this usage message'
        print ' -t; --target            file with the target side of translation'
        #print '        -s; --source            file with the source side of translation'
        #print '        -a; --align             file with the alignments, sentence by sentence'
        print ' -o; --output            file where to save the new output translation,' 
        print '                         otherwise it will be shown by the standard output'
        print ' -l; --lemma_t                   file with the pos + lemmas of the target file'
        #print ' -r; --corref_src      file with the corref analisis of the source file'
        #print '        -c; --lemma_src           file with the pos + lemmas of the source file'
        #print ' -p; --probs  suggest words with probabilities to make a new translation'
        #print ' -u; --uniword suggest only one word to make a new translation'
#########################################################################
def compara_pos_en_es(src_pos, pos_twd):
        iguales=False
        #src_pos -- en:  MD ; EX,PDT, POS, SYM, TO, RP, ,  -- no nos interesa 
        #pos_twd -- es:  W* fechas/horas  F -- punctuation 
        
        if src_pos=='CC' and pos_twd[0] in 'C':
                iguales=True
        elif src_pos=='IN' and pos_twd[0] in 'S':
                iguales=True
        elif src_pos[:2]=='JJ' and pos_twd[0] in 'A':
                iguales=True
        elif src_pos in ['DT','WDT'] and pos_twd[0] in 'D':
                iguales=True
        elif src_pos=='FW' and pos_twd[0] in 'X':
                iguales=True

        elif src_pos=='UH' and pos_twd[0] in 'I':
                iguales=True
        elif src_pos in ['LS','CD'] and pos_twd[0] in 'Z':
                iguales=True
        elif src_pos in ['PRP','PRP$','WP','WP$'] and pos_twd[0] in 'P':
                iguales=True
        elif src_pos in ['NN','NNP','NNS','NNPS'] and pos_twd[0] in 'N':
                iguales=True
        elif src_pos[:2] in ['RB','WR'] and pos_twd[0] in 'R':
                iguales=True
        elif src_pos in ['VBZ','VBP','VBN', 'VBG', 'VBD','VB'] and pos_twd[0] in 'V':
                iguales=True
        
        return iguales



###########################################################################
###########################################################################
maint=0
###########################################################################
###########################################################################
#freeling arrangements

## Modify this line to be your FreeLing installation directory
FREELINGDIR = "/home/usuaris/tools";

DATA = FREELINGDIR+"/share/freeling/";
LANG="es";

freeling.util_init_locale("default");

###########################################################################

#get the option selected by the user
opts,args=getoptions()
#print args
if len(opts)<1:
  help()
  sys.exit()
#check the options chosen by the user
#source_file=0
target_file=0
#align_file=0
output_file=0
lemma_t_file=0
#lemm_src_file=0
#coref_src_file=0
#flag_probs=1
#flag_uniwords=1
#depending on the user options...
for o,a in opts:
        #source file
        if o in ("-s","--source"):
                source_file=a
        #help  
        elif o in ("-h", "--help"):
                help()
                sys.exit()
        #alignments file
        #elif o in ("-a","--align"):
        #       align_file=a
        #target file (traduction) 
        elif o in ("-t","--target"):
                target_file=a
        # output file
        elif o in ("-o","--output"):  
                output_file=a
        elif o in ("-l","--lemma_t"):
                lemma_t_file=a
        #elif o in ("-c", "--lemma_src"):
        #       lemm_src_file=a
        #elif o in ("-r", "--corref_src"):
        #       coref_src_file=a
        #elif o in ("-p","--probs"):
        #probs to translate
        #       flag_probs=1
        #       flag_uniwords=0
        #elif o in ("-u","--uniwords"):
        #       flag_uniwords=1
        #       flag_probs=0
        # any other option  
        else:
                assert False, "unhandled option"
                help()
                sys.exit(2)

#############################
#get the files content
#open files
#source_file_f=open(source_file,'rw')
target_file_f=open(target_file,'rw')
#align_file_f=open(align_file,'rw')
lemma_file_f=open(lemma_t_file,'rw')
#lemm_src_file_f=open(lemm_src_file,'rw')
#coref_src_file_f=open(coref_src_file,'rw')

#get content
#source_content=source_file_f.read()
target_content=target_file_f.read()
#align_content=align_file_f.read()
lemma_content=lemma_file_f.read()
#lemma_src_content=lemm_src_file_f.read()
#coref_src_content=coref_src_file_f.read()

#close files
#source_file_f.close()
target_file_f.close()
#align_file_f.close()
lemma_file_f.close()
#lemm_src_file_f.close()
#coref_src_file_f.close()


#split content sentence by sentence
#source_list=source_content.split("\n")
target_list=target_content.split("\n")
#align_list= align_content.split("\n")
lemma_list_wd=lemma_content.split("\n")
#lemma_src_list_wd=lemma_src_content.split("\n")
#coref_src_list=coref_src_content.split("\n") #list of sentences with its coref analisis

target_sentences=[]
for e in target_list:
        words=e.split(' ')
        target_sentences.append(words)
        #for w in words:
                #diccio_tgt[w]=set()
        


#print lemma_list_wd
#print len(lemma_list_wd)
#print target_sentences
#sys.exit(2)
lemma_list_wd = [wd for wd in lemma_list_wd if wd != '']

target_sentences = [[wt for wt in ts if wt != ''] for ts in target_sentences if ts != ['']]
#build the lemma_sentences for the target side
lemma_sentences=[]
#[sentences] ; sentence=[ [word,lemma,pos]...]
k=0
for i,ts in enumerate(target_sentences):
        #print '####'
        #print i
        #print ts
        ls=[]
        j=0
#       for wt in ts:#enumerate(ts):
        while j<len(ts):
                wt=ts[j]
                #print wt+'aaaa'
                #print lemma_list_wd[k].split(' ')
                if (wt.lower()=='al' or wt.lower()=='del') and k+1 < len(lemma_list_wd): #k --> a k+1-->el ; de- el;
                        add=[wt]
                        add.append(lemma_list_wd[k].split(' ')[1:])
                        add.append(lemma_list_wd[k+1].split(' ')[1:])
                        ls.append(add)
                        k=k+2
                        j=j+1
                else:
                        add=''
                        n=1
                        if k<len(lemma_list_wd):
                                add=lemma_list_wd[k].split(' ')
                                if wt!=add[0] and '_' in add[0]:
                                        n=0
                                        words=add[0].split('_')
                                        pos=lemma_list_wd[k].split(' ')[1:]
                                        for wi in words:
                                                add=[wi] +pos
                                                ls.append(add)
                                                n=n+1
                                        add=''  
                                elif add!='':
                                        ls.append(lemma_list_wd[k].split(' '))
                        k=k+1
                        j=j+n
                        
        #print str(ls)+'AAAaaa'         
        #print '####'
        lemma_sentences.append(ls)        
#check lengths
if len(lemma_sentences) != len(target_sentences) or any([len(lemma_sentences[i])!=len(target_sentences[i]) for i in range(len(lemma_sentences))]):
        print 'HORROR!FUROR TERROR MUJER PON LO QUE YO TE DIGO'
        sys.exit(2)

#### set the freeling dictionary
diccio_file=DATA+LANG+"/dicc.src";
set_false=False
set_true=True
affix=''
diccio=freeling.dictionary("es",diccio_file,set_false,affix,set_true,set_false)
#print diccio

##### CHECH THE GENDER/NUMBER AGREEEMENT IN TARGET SIDE #####
new_target_sentences=[list(ts) for ts in target_sentences]
nchanges=0
changed_lines=[]
for i, tgt_s in enumerate(target_sentences):
        #print tgt_s
        #j2=0 #incremento por palabras al, del --> a + el, de + el
        for j, wt in enumerate(tgt_s):
                #print wt
                if j>=1 and j<len(lemma_sentences[i]) and (wt.lower()!='al' or wt.lower()!='del'): #we're not in the 1st word of the sentence
                        #look at the pos of the word
                        
                        wpos=''
                        if len(lemma_sentences[i][j])>=3:
                                wpos = lemma_sentences[i][j][2]
                        newDet=''       
                        #print wpos
                        #if it is a common noun

                        
                        if wpos!='':
                                if wpos[0] =='N' and wpos[1]=='C':
                                        
                                        #look if the previous word is a determiner
                                        #print '----'+target_sentences[i][j-1]
                                        wb=''
                                        wb_pos=''
                                        if target_sentences[i][j-1].lower()=='del' or target_sentences[i][j-1].lower()=='al':
                                                wb=lemma_sentences[i][j-1]
                                                wb_pos=lemma_sentences[i][j-1][2][1] #['del', ['de', 'SPS00', '1'], ['el', 'DA0MS0', '1']]
                                        else:   
                                                wb=lemma_sentences[i][j-1]
                                                wb_pos=lemma_sentences[i][j-1][2]
                                        #print '#####'
                                        #print target_sentences[i][j-1]
                                        #print wt +' '+wpos
                                        #print wb
                                        #print '#####'
                                        det=target_sentences[i][j-1]
                                        if wb_pos[0]=='D' and wb_pos[1]=='A' and wb_pos[2]=='0': #determinante articulo DA0GN0---
                                                #print '#####'
                                                #print target_sentences[i][j-1] + str(wb_pos)
                                                #print str(wt) +' '+str(wpos)
                                                #print lemma_sentences[i][j-1]
                                                #print '#####'
                                                g_w=wpos[2]
                                                n_w=wpos[3]
                                                g_wb=wb_pos[3]
                                                n_wb=wb_pos[4]
                                                #first, we check the gender agreement:
                                                if (g_w != g_wb and g_w!='C'): #if there is a disagreement and we know the gender of the noun
                                                        #neutral gender --> accept masculine determiners
                                                        # neutro D and M noun --> ok 
                                                        # masculine D and masculine noun --> ok
                                                         
                                                        #suggest new determiner: el la lo los las 
                                                        gn_w=g_w+n_w 
                                                        if gn_w=='FS': 
                                                                newDet='la'                             
                                                                if target_sentences[i][j-1].lower()=='del' :
                                                                        newDet='de la'
                                                                if target_sentences[i][j-1].lower()=='al' :
                                                                        newDet='a la'
                                                                        
                                                        elif (gn_w=='MS' or gn_w=='NS') and (g_wb+n_wb!='NS'):
                                                                newDet='el'
                                                        elif gn_w=='FP':
                                                                newDet='las'
                                                                if target_sentences[i][j-1].lower()=='del' :
                                                                        newDet='de las'
                                                                if target_sentences[i][j-1].lower()=='al' :
                                                                        newDet='a las'
                                                        elif gn_w=='MP' or gn_w=='NP':
                                                                newDet='los'
                                                                if target_sentences[i][j-1].lower()=='del' :
                                                                        newDet='de los'
                                                                if target_sentences[i][j-1].lower()=='al' :
                                                                        newDet='a los'
                                                        else:
                                                                newDet=''
                                                else : #agree in gender but in number
                                                        n_w=wpos[3]
                                                        n_wb=wb_pos[4]
                                                        #det=target_sentences[i][j-1]
                                                        if n_w!=n_wb:
                                                                if n_w=='P':
                                                                        if g_w=='F':
                                                                                newDet='las'
                                                                        else:
                                                                                newDet = 'los'
                                                                                if target_sentences[i][j-1].lower()=='del' :
                                                                                        newDet='de los'
                                                                                if target_sentences[i][j-1].lower()=='al' :
                                                                                        newDet='a los'
                                                                if n_wb=='P': #should be 'S' -> el/la/lo # and det[len(det)-1]=='s':
                                                                        #newDet=det[:len(det)-1]
                                                                        if g_w=='F':
                                                                                newDet='la'
                                                                        elif g_w=='M':
                                                                                newDet='el'
                                                                                if target_sentences[i][j-1].lower()=='de' :
                                                                                        newDet='del'
                                                                                if target_sentences[i][j-1].lower()=='a' :
                                                                                        newDet='al'
                                                                        elif g_w=='N':
                                                                                newDet='lo'
                                                                                if target_sentences[i][j-1].lower()=='de' :
                                                                                        newDet='del'
                                                                                if target_sentences[i][j-1].lower()=='a' :
                                                                                        newDet='al'
                                        elif wb_pos[0]=='D' and wb_pos[1]=='I' and wb_pos[2]=='0' and det.lower() in ['un','una','unos','unas']:#articulo indeterminado DI0GN0--
                                                g_w=wpos[2]
                                                n_w=wpos[3]
                                                g_wb=wb_pos[3]
                                                n_wb=wb_pos[4]
                                                        ###first, we check the gender agreement:
                                                if (g_w != g_wb and g_w!='C'): #if there is a disagreement and we know the gender of the noun
                                                        ###neutral gender --> accept masculine determiners
                                                        ### neutro D and M noun --> ok 
                                                        ### masculine D and masculine noun --> ok
                                                         
                                                        ###suggest new determiner: el la lo los las 
                                                        gn_w=g_w+n_w 
                                                        if gn_w=='FS': 
                                                                newDet='una'                            
                                                                
                                                        elif (gn_w=='MS' or gn_w=='NS') and (g_wb+n_wb!='NS'):
                                                                newDet='un'
                                                        elif gn_w=='FP':
                                                                newDet='unas'
                                                        elif gn_w=='MP' or gn_w=='NP':
                                                                newDet='unos'
                                                        else:
                                                                newDet=''
                                                else : #agree in gender but in number
                                                        n_w=wpos[3]
                                                        n_wb=wb_pos[4]
                                                        #det=target_sentences[i][j-1]
                                                        if n_w!=n_wb:
                                                                if n_w=='P':
                                                                        if det.lower()=='un' or det.lower()=='uno':#det=='un' or det=='Un' or det=='UN' or det=='uN':
                                                                                newDet='unos'
                                                                        else:
                                                                                newDet = det+'s'
                                                                                
                                                                if n_wb=='P' and det[len(det)-1]=='s':
                                                                        if det.lower()=='unas':
                                                                                newDet='una'
                                                                        elif det.lower()=='unos':
                                                                                newDet='un'
                                                                                ##newDet=det[:len(det)-1]               
                                        ##else:
                                        ##      print 'AAAAAA'
                                                
                                if newDet!='':
                                        #print '<<<<<<<<<<<<<<>>>>>>>>>>'       
                                        #print tgt_s
                                        #print target_sentences[i][j-1]+' @@@@@ '+wt+'    '+wpos
                                        #print newDet
                                        
                                        new_target_sentences[i][j-1]=newDet#='----------->'+newDet
                                        nchanges= nchanges+1
                                        if len(changed_lines)==0 or changed_lines[-1]!=i:
                                                changed_lines.append(i)
                                
        #tsent=''                                       
        #for wt in new_target_sentences[i]:
                #tsent=tsent+wt+' '     
        #print tsent

#print '@@@@@@@@@@@@@@@@@@@@@@@'        
#print '########################'       
for s in new_target_sentences:
        print ' '.join(s)
#print '########################'
#for i in changed_lines:
        #print '#'+' '.join(new_target_sentences[i])
#print '########################'
#print nchanges
#####                                    
