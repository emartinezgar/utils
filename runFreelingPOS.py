#! /usr/bin/python


import freeling
import sys


## ------------  output a parse tree ------------
def printTree(node, depth):

    sys.stdout.write(''.rjust(depth*2));
    info = node.get_info();
    if (info.is_head()): sys.stdout.write('+');

    nch = node.num_children();
    if (nch == 0) :
        w = info.get_word();
        sys.stdout.write ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()));

    else :
        sys.stdout.write('{0}_['.format(info.get_label())+'\n');

        for i in range(nch) :
            child = node.nth_child_ref(i);
            printTree(child, depth+1);

        sys.stdout.write(''.rjust(depth*2));
        sys.stdout.write(']');
        
    sys.stdout.write('\n');

## ------------  output a parse tree ------------
def printDepTree(node, depth):

    sys.stdout.write(''.rjust(depth*2));

    info = node.get_info();
    link = info.get_link();
    linfo = link.get_info();
    sys.stdout.write ('{0}/{1}/'.format(link.get_info().get_label(), info.get_label()));

    w = node.get_info().get_word();
    sys.stdout.write ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()));

    nch = node.num_children();
    if (nch > 0) :
        sys.stdout.write(' [\n');

        for i in range(nch) :
            d = node.nth_child_ref(i);
            if (not d.get_info().is_chunk()) :
                printDepTree(d, depth+1);

        ch = {};
        for i in range(nch) :
            d = node.nth_child_ref(i);
            if (d.get_info().is_chunk()) :
                ch[d.get_info().get_chunk_ord()] = d;
 
        for i in sorted(ch.keys()) :
            printDepTree(ch[i], depth + 1);

        sys.stdout.write(''.rjust(depth*2));
        sys.stdout.write(']');

    sys.stdout.write('\n');

## ----------------------------------------------
## -------------    MAIN PROGRAM  ---------------
## ----------------------------------------------

## Modify this line to be your FreeLing installation directory
FREELINGDIR = "/home/usuaris/tools";

DATA = FREELINGDIR+"/share/freeling/";
LANG=sys.argv[1]; #"es";

freeling.util_init_locale("default");

# create language analyzer
#la=freeling.lang_ident(DATA+"common/lang_ident/ident.dat");
#print 'land ident'
# create options set for maco analyzer. Default values are Ok, except for data files.
op= freeling.maco_options(LANG);
#old func #op.set_active_modules(0,1,1,1,1,1,1,1,1,1,1,1);
#old func #op.set_data_files("",DATA+LANG+"/locucions.dat", DATA+LANG+"/quantities.dat", 
#                  DATA+LANG+"/afixos.dat", DATA+LANG+"/probabilitats.dat", 
#                  DATA+LANG+"/dicc.src", DATA+LANG+"/np.dat",  
#                  DATA+"common/punct.dat");
op.set_data_files("", DATA+"common/punct.dat", DATA+LANG+"/dicc.src", 
                  DATA+LANG+"/afixos.dat", "", DATA+LANG+"/locucions.dat", 
                  DATA+LANG+"/np.dat", DATA+LANG+"/quantities.dat", DATA+LANG+"/probabilitats.dat");

#print 'options setted'
# create analyzers
tk=freeling.tokenizer(DATA+LANG+"/tokenizer.dat");
#print 'tokenizer'
sp=freeling.splitter("/home/usuaris/emartinez/DLTI/pre_proc/freeling_config/splitter.dat");#(DATA+LANG+"/splitter.dat");
sid=sp.open_session(); #new thing to do to the splitter... maybe later I wont need it... but still...
#print 'splitter'

mf=freeling.maco(op);
mf.set_active_options(0, 1, 1, 0, #select 
                      1, 0, 0, 0, #submodules
                      0, 0, 0, 1);#default : all
#print 'maco'
tg=freeling.hmm_tagger(DATA+LANG+"/tagger.dat",1,2);
#print 'tagger'
#sen=freeling.senses(DATA+LANG+"/senses.dat");
#print 'sense'
#parser= freeling.chart_parser(DATA+LANG+"/chunker/grammar-chunk.dat");
#print 'parser'
#dep=freeling.dep_txala(DATA+LANG+"/dep_txala/dependences.dat", parser.get_start_symbol());
#print 'dep parser'

#lin=sys.stdin.readline();
#lin="Estoy probando que el Freeling funcione bien ."
#"Architectural empresa de disenyo , Arch.Design , cuyos estudios elaborado un numero importante de edificios en Brno , hemos incluido el espacio de su pequenyo guarderia incluso en la primera dibujos del Avriopoint edificio .".decode('utf8')
#sys.stdout.write ("Text language is: "+la.identify_language(lin,["es","ca","en","it"])+"\n");


#print "Text language is: " +la.identify_language(lin,["es","ca","en","it"])+"\n"
lin=sys.stdin.read().split("\n")
for l in lin:
        #print lin    
        #l = tk.tokenize(lin);
        #print l
        l_aux=l.split()
        lin_tok=[]

        for e in l_aux :
                #if e!=' ':
                #       w=freeling.word(e.decode("utf8"))
                #else:
                w=freeling.word(e.decode('utf-8'))
                #print w.get_form()
                lin_tok.append(w)
        lin_an=[]
        lin_an.append(freeling.sentence(lin_tok))
        #ls=sp.split(l,0);
#ls = sp.split(sid,l,0);#change!
        lin_an=mf.analyze(lin_an);
        lin_an=tg.analyze(lin_an);
  
#    ls = mf.analyze(ls);
#    ls = tg.analyze(ls);
#    ls = sen.analyze(ls);
#    ls = parser.analyze(ls);
#    ls = dep.analyze(ls);

    ## output results
        ws=[]
        for s in lin_an :
                ws = s.get_words();
        for w in ws :
                print w.get_form().encode("utf-8")+" "+w.get_lemma().encode("utf-8")+" "+w.get_tag().encode("utf-8")#+'\n' #+" "+w.get_senses_string()+'\n');
#      sys.stdout.write('\n');

#      tr = s.get_parse_tree();
      # printTree(tr.begin(), 0);

#      dp = s.get_dep_tree();
       #printDepTree(dp.begin(), 0)

#   lin=sys.stdin.readline();

#clean up....    
sp.close_session(sid); 