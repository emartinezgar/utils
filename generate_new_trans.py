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
#               -noP:                   delete all the punctuation symbols ( ',' ,.,!,?,",',#,*,(,),[,],-,_,;,...,<,>,/,\,^,%,},{ 
)
#               -ngrams number:         split the text in 'number'-grams randomly
#               -addE:                  change letters randomly in the text simulating misprints
#               -NP:                    only remain the Noun Phrases of the text: we need that the text has a tree structure to fi
nd the NPs.

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
#########################################################################
#                       FUNCTIONS DEFINITIONS                           #
#########################################################################
#########################################################################
#getoptions function
# gets the parameters indicated by the user
def getoptions():
        try:
                opts, args = getopt.getopt(sys.argv[1:], "ht:s:a:o:l:c:", ["help","target=","source=","align=","output=","lemma_t=
","--lemma_src="])
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
        print 'Usage: identifica_src_tgt.py [OPTIONS]'
        print ' options:'
        print ' -h ; --help                       Display this usage message'
        print ' -t; --target            file with the target side of translation'
        print ' -s; --source            file with the source side of translation'
        print ' -a; --align             file with the alignments, sentence by sentence'
        print ' -o; --output            file where to save the new output translation,' 
        print '                         otherwise it will be shown by the standard output'
        print ' -l; --lemma_t                   file with the pos + lemmas of the target file'
        print ' -r; --corref_src      file with the corref analisis of the source file'
        print ' -c; --lemma_src           file with the pos + lemmas of the source file'
        print ' -p; --probs  suggest words with probabilities to make a new translation'
        print ' -u; --uniword suggest only one word to make a new translation'
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
#get the option selected by the user
opts,args=getoptions()
#print args
if len(opts)<3:
  help()
  sys.exit()
#check the options chosen by the user

source_file=0
target_file=0
align_file=0
output_file=0
lemma_t_file=0
lemm_src_file=0
coref_src_file=0
flag_probs=0
flag_uniwords=1
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
        elif o in ("-a","--align"):
                align_file=a
        #target file (traduction) 
        elif o in ("-t","--target"):
                target_file=a
        # output file
        elif o in ("-o","--output"):  
                output_file=a
        elif o in ("-l","--lemma_t"):
                lemma_t_file=a
        elif o in ("-c", "--lemma_src"):
                lemm_src_file=a
#       elif o in ("-r", "--corref_src"):
#               coref_src_file=a
        elif o in ("-p","--probs"):
        #probs to translate
                flag_probs=1
                flag_uniwords=0
        elif o in ("-u","--uniwords"):
                flag_uniwords=1
                flag_probs=0
        # any other option  
        else:
                assert False, "unhandled option"
                help()
                sys.exit(2)
                
#############################

#get the files content
#open files
source_file_f=open(source_file,'rw')
target_file_f=open(target_file,'rw')
align_file_f=open(align_file,'rw')
lemma_file_f=open(lemma_t_file,'rw')
lemm_src_file_f=open(lemm_src_file,'rw')
#coref_src_file_f=open(coref_src_file,'rw')

#get content
source_content=source_file_f.read()
target_content=target_file_f.read()
align_content=align_file_f.read()
lemma_content=lemma_file_f.read()
lemma_src_content=lemm_src_file_f.read()
#coref_src_content=coref_src_file_f.read()

#close files
source_file_f.close()
target_file_f.close()
align_file_f.close()
lemma_file_f.close()
lemm_src_file_f.close()
#coref_src_file_f.close()


#split content sentence by sentence
source_list=source_content.split("\n")
target_list=target_content.split("\n")
align_list= align_content.split("\n")
lemma_list_wd=lemma_content.split("\n")
lemma_src_list_wd=lemma_src_content.split("\n")
#coref_src_list=coref_src_content.split("\n") #list of sentences with its coref analisis

#split content word by word and create the dictionaries
diccio_tgt=dict()
diccio_src=dict()

source_sentences=[]
for e in source_list:
        words=e.split(' ')
        source_sentences.append(words)
        for w in words: 
                #diccio_src[w]=set()
                #we count how many times we translate the word to a 'tuple'
                diccio_src[w]=dict()
  
target_sentences=[]
for e in target_list:
        words=e.split(' ')
        target_sentences.append(words)
        for w in words:
                diccio_tgt[w]=set()
        
#build the lemma_sentences for the target side
lemma_sentences=[]
#[sentences] ; sentence=[ [word,lemma,pos]...]
k=0
#print lemma_list_wd
#print len(lemma_list_wd)
for i,ts in enumerate(target_sentences):
        ls=[]
        for j,wt in enumerate(ts):
#               print k
#               print wt
                if wt != '':
                        #print lemma_list_wd[k]
                        ls.append(lemma_list_wd[k].split(' '))
                        k=k+1
        lemma_sentences.append(ls)
  
#build the lemma_sentences for the source side
lemma_source_sentences=[]
#[sentences] ; sentence=[ [word,lemma,pos]...]
k=0
#print len(lemma_src_list_wd)
#print lemma_src_list_wd
for i,ts in enumerate(source_sentences):
        ls=[]
#       print 'AAA'+str(ts)
        for j,wt in enumerate(ts):
                #print 'bbb '+wt
                if wt != '':
                  #print lemma_list_wd[k]
#                       print k
#                       print lemma_src_list_wd[k]
                        ls.append(lemma_src_list_wd[k].split(' '))
                        k=k+1
        lemma_source_sentences.append(ls)  
  
#print lemma_sentences  
#sys.exit(2)  

#study the alignments and fill the dictionaries
align_sentences=[]
for e in align_list:
        words=e.split(' ') #[ 0-0, 1-1, 2-2, 3-3]
        axsentence=[]
        for w in words:
                axsentence.append(w.split('-'))
        align_sentences.append(axsentence)

#FILL THE DICTIONARIES
#fill the target dictionary
k=0 #position in the text
for i,ts in enumerate(target_sentences):
  #ith sentence
  src_sent=source_sentences[i]
  alignments=align_sentences[i]
  #print src_sent
  #print alignments
  for j,wt in enumerate(ts):
        src_wd=[]
        for e in alignments: #alignments [ [
          if len(e)>1:
                if str(j) == str(e[1]):
                  src_ind=int(e[0])
                  if src_sent[src_ind]!='':
                        #src_wd.append(src_sent[src_ind])
                        #[word, lemma, text_pos]
                        src_lemma=lemma_source_sentences[i][src_ind][1]
                
                        src_wd.append(tuple([src_sent[src_ind],src_lemma]))#,k]))
        k=k+1   
        #print wt
        #print '-->'+str(src_wd)
        diccio_tgt[wt].add(tuple(src_wd))

#fill the source dictionary     --> src_word -->[(twd, twd lema), ntimes]
k=0 #position in the text
for i,src_s in enumerate(source_sentences):
        #ith sentence
        ts=target_sentences[i]
        ls=lemma_sentences[i]
  
        alignments=align_sentences[i]
  
        for j,ws in enumerate(src_s):
                t_wd=[]
                for e in alignments: #alignments 
                #t_lemma=''
                        if len(e)>1:
                                if str(j) == str(e[0]):
                                        t_ind=int(e[1])
                                        if ts[t_ind]!='':
                                                print ls[t_ind]
                                                t_lemma = ls[t_ind][1]
                                                #t_wd.append(ts[t_ind])
                                                #[word, lemma, text_pos]
                                                t_wd.append(tuple([ts[t_ind], t_lemma]))
                if t_wd!=[]:
                        if ws in diccio_src:
                                if tuple(t_wd) in diccio_src[ws]: #if tuple in the dictionary diccio_src[ws]
                                        diccio_src[ws][tuple(t_wd)]= diccio_src[ws][tuple(t_wd)]+1#increment the counter
                                else:
                                        diccio_src[ws][tuple(t_wd)]=1
                        else:
                                diccio_src[ws][tuple(t_wd)]=1
                k=k+1
#####           
#print diccio_src
#for e in diccio_src:
#       print e
#       print diccio_src[e]
#       for a in diccio_src[e]:         
#               print a
#               print diccio_src[e][a]
#               if diccio_src[e][a]<1:
#                       print 'AAAAAAAA'

#sys.exit()
###################################################################
###################################################################
###################################################################
###################################################################
###################################################################        
###################################################################
###################################################################
###################################################################
##DEBUGG
#print '######'
#print diccio_src.items()
#print '######'
#print diccio_tgt.items()
#print '######'
#sys.exit(2)


#build the output
#for every word in the target side, the translation
#we check if the aligned source word has more than one
#different word associated --> add an xml tag
#

untranslated_file=open(target_file+'_untranslated','w')
#print untranslated_file
ambiguous_file=open(target_file+'_ambiguous','w')

new_src_file=open(source_file+'_2transRes','w')#Probs','w')#open(source_file+'_2trans','w')
new_src_file2=open(source_file+'_2transProbs','w')
#print ambiguous_file
src_wds_2print=set() #add tuple(senti, wdj)

if output_file!=0:
        #print in the output_file
        print 'IN FILE'
  

else: #standard output
        for i, ts in enumerate(target_sentences):
                #for every sentence
                
                translated_sentence=''
                for j, wt in enumerate(ts):
                        print_wd=0
                        if wt!="" and wt not in string.punctuation and wt != "&quot;" and wt!='¿':
                                #for every word in the sentence
                                #get the aligned source words
                                ####src_wds=diccio_tgt[wt]
                                #we only get the aligned source word
                                 
                                src_wds=[]
                                for a in align_sentences[i]:
                                        if len(a)>1:
                                                if str(j)==str(a[1]):
                                                        src_j=int(a[0])
                                                        src_wds.append(source_sentences[i][src_j])
                                pos_twd=lemma_sentences[i][j][2] #recogemos la pos de la palabra target
                                lema_twd=lemma_sentences[i][j][1]
                                #mark if the tw has several different aligned src words
                                #only if we have a noun in the target side
                                if len(src_wds)>=1 and pos_twd[0] in 'N':# and pos_twd[0] in 'A'#adjectives#lema_twd!='ser' and lema_twd!='estar' and lema_twd!='haber' and lema_twd!='saber':
                                        #print ':::::'+wt+'::::'+pos_twd
                                        
                                        if wt in src_wds:#tuple([wt]) in src_wds:
                                        ####if tuple([wt]) in src_wds:
                                                #pos_twd=lemma_sentences[i][j][2]
                                                #lema_twd=lemma_sentences[i][j][1]
                                                if (pos_twd!='NP' or (pos_twd=='NP' and (lema_twd.capitalize()!=lema_twd))) and not wt.isdigit():
                                                        translated_sentence=translated_sentence+'<untranslated>'+wt+'</untranslated> '
                                                        #print in 'untranslated_file'
                                                        untranslated_file.write('<untranslated>'+wt+'</untranslated> '+'\n')
                                                        print_wd=1
                                        #mark if the src_wd has more than one different tw aligned
                                        else:
                                                # e is a string
                                                for e in src_wds:
                                                        #print e
                                                        if len(e)>0:
                                                                #print e[0]
                                                                #tuple: e[0]; word-> e[0][0]
                                                                #print e[0]+'#####'
                                                                src_pos=''
                                                                for a in align_sentences[i]:
                                                                        if len(a)>1:
                                                                                if str(j)==str(a[1]):
                                                                                        src_j=int(a[0])
                                                                                        src_pos=lemma_source_sentences[i][src_j][2]#(source_sentences[i][src_j])
                                                                #print '###'
                                                                #print src_pos
                                                                #print e
                                                                #print '####'
                                                                #src_pos=lemma_source_sentences[i][j][2]
                                                                #sólo coger las twds de las palabras src alineadas
                                                                #que comparten el mismo pos que en el target side
                                                                #comparar src_pos y pos_twd
                                                                twds=[]
                                                                if e!='will' and e!='Will' and e!='I' and e!='is'and e!='Is' and e!='it' and e!='It' and e!='are' and e!='see' and e!='have' and e!='has' and compara_pos_en_es(src_pos, pos_twd): #si son iguales e interesantes: hazlo! de otra manera... pasa... y deja twds en []
                                                                #only for nouns 
                                                                #if (pos_twd[0] in 'N') and compara_pos_en_es(src_pos, pos_twd): #si son iguales e interesantes: hazlo! de otra manera... pasa... y deja twds en []
                                                                        twds=diccio_src[e]#e[0][0]] #### no puedo buscar un set: hay que mirar el elemento...
                                                                        
                                                                #look for e in the src_text (i,j) --> look for its alignment in the other way round! ^^ 
                                                                #twds is now a dictionary --> we look if the dictionary has more than one element
                                                                #len(dict) return the number of elements in the dictionary
                                                                if len(twds)>1:                                        
                                                                      #print twds
                                                                  
                                                                        ###check the lemmas and see if they are actually a different word
                                                                        #arg in twds has the form of (tuple) --> ntimes
                                                                        argpp = set([tuple([ e[1] for e in arg ]) for arg in twds])
                                                                        #print argpp
                                                                        #print "muahah"
                                                                        argppp = reduce(operator.__and__,[set(t) for t in argpp])
                                                                        #print len(twds)
                                                                        pos_twd=lemma_sentences[i][j][2]
                                                                        #print pos_twd
                                                                        
                                                                        if len(argpp)>1 and ( len(argppp)==0) and (pos_twd[0] not in 'PDCSWYXZR'):
                                                                                # interseccion vacia de lemas y no tiene una PoS poco interesante: 
                                                                                #P pronombre, Dartículo, Cconjuncion, Sdeterminante,fecha, abr., palabra extr, numero, preposicion  ):
                                                                                ### todas menos Nombre y Adjetivos 
                                                                                translated_sentence=translated_sentence+'<ambiguous tw='
                                                                                amb_string='<ambiguous tw='
                                                                                for w in twds:
                                                                                        translated_sentence=translated_sentence+str(w)+','
                                                                                        amb_string = amb_string + str(w)+','
                                                                                for w in  src_wds:
                                                                                        #look for the src_j and save it to workd with it later
                                                                                        for a in align_sentences[i]:
                                                                                                if len(a)>1:
                                                                                                        ####AQUIIIIIIIIII.....
                                                                                                        if str(j)==str(a[1]) and w == source_sentences[i][int(a[0])]:
                                                                                                                
                                                                                                                src_wds_2print.add(tuple((i,int(a[0]))))
                                                                                                                
                                                                                        translated_sentence=translated_sentence+' srcw='+str(w)+', '
                                                                                        amb_string = amb_string + ' srcw='+str(w)+', '
                                                                                translated_sentence=translated_sentence+'>'+wt+' </ambiguous> '
                                                                                amb_string=amb_string + '>'+wt+' </ambiguous> '
                                                                                ambiguous_file.write(amb_string+'\n')
                                         
                                        
                        if wt!="" and print_wd==0 :#or wt in string.punctuation: #if we didn't print the word before, print it in a normal way
                                translated_sentence=translated_sentence+wt+' '
                print translated_sentence

### print new src file
for i,s in enumerate(source_sentences):
        s_sent=''
        s_sent2=''
        for j,ws in enumerate(s):
                if tuple((i,j)) in src_wds_2print:#we have to tell moses to translate somehow the word IF IT HAS BEEN TAGGED AS AMBIGUOUS FIRST!!
                        #choose the word to translate the src_word
                        tuple2trans=[]
                        max2trans=0
                        for elem in diccio_src[ws]:
                                #print str(elem)+'   ' + str(diccio_src[ws][elem])
                                
                                if diccio_src[ws][elem]>=max2trans :
                                        max2trans=diccio_src[ws][elem]
                                        if len(elem)==1:
                                                tuple2trans.append(elem[0])
                                        else: #los socialdemocratas, frases hechas
                                                part1=''
                                                part2=''
                                                for e in elem:
                                                        part1=part1+e[0]+' '
                                                        part2=part2+e[1]+' '
                                                part1=part1[:len(part1)-1]
                                                part2=part2[:len(part2)-1]
                                                #print 'TUUUPLE::'+str(tuple((part1,part2)))
                                                tuple2trans.append(tuple((part1,part2)))
                                                
                                #print str(elem) 
                                #print diccio_src[ws][elem]
                                #idea: if there is more... prob=0.5, 0.5 .. 0.n...n = number of tuples
                        #print '####aaaa'       
                        #print tuple2trans      
                        #print '####aaa2'
                        
                        if len(tuple2trans)==1: #there is only a tuple with the maximum number of appearances
                                
                                #we lowercase the word....(little idea...)      
                                word2trans=tuple2trans[0][0]
                                #exclusive s_sent=s_sent+'<np translation="'+ word2trans+'">' +ws+'</np>'
                                #inclusive moses -xml-input inclusive -f moses.ini
                                s_sent=s_sent+'<n translation="'+ word2trans+'">'+ws+'</n> '# prob="0.8">' 
                                s_sent2=s_sent2+'<n translation="'+word2trans+'">'+ws+'</n> '
                                #inclusive
                                #s_sent=s_sent+'<n translation="'+ word2trans+'" prob="0.8">' +ws+'</n>'
                        elif len(tuple2trans)>1 and flag_probs==1:
                                #redistribute the 0.8 probability among the tuples with the major number of occurrencies
                                n_words=len(tuple2trans)
                        
                                new_prob=float(1)/float(n_words)
                                #print '####'+str(n_words)+' '+str(new_prob)
                                #s_sent=s_sent+'<n '
                                s_sent2=s_sent2+'<n translation="'
                                for k,t in enumerate(tuple2trans):
                                        #       s_sent=s_sent+'translation="'+t[0].lower()+'" prob="'+str(new_prob)+'" '
                                        
                                        if k==0:
                                                s_sent2=s_sent2+t[0].lower()
                                        else:
                                                s_sent2=s_sent2+"||"+t[0].lower()
                                s_sent2=s_sent2+'" prob="'+str(new_prob)
                                k=1
                                while k< len(tuple2trans):
                                        s_sent2=s_sent2+'||'+str(new_prob)
                                        k=k+1
                                #s_sent=s_sent+'>'+ws+'</n> '   
                                s_sent2=s_sent2+'">'+ws+'</n> ' 
                        else:
##                              print 'no trans ind'
                                s_sent=s_sent+ws+' '
                                s_sent2=s_sent2+ws+' '
                else:
                        s_sent=s_sent+ws+' '
                        s_sent2=s_sent2+ws+' '
                
        new_src_file.write(s_sent+'\n')
        new_src_file2.write(s_sent2+'\n')
#close files
untranslated_file.close()
ambiguous_file.close()
new_src_file.close()
new_src_file2.close()
#provisional:list of possible ambiguous/bad translated words
###print dictionaries             
##target dictionary
#for w in diccio_tgt:
#  print w
#  print diccio_tgt[w]
#  print '#######'
#print '#######'  
#print '#######'
##src dictionary
#print '#######'
#print '#######'
#for w in diccio_src:
#  print w
#  print diccio_src[w]
#print '#######'

################DEBUGGG
#print align_sentences
#print target_sentences
#print source_sentences
#sys.exit(2)

