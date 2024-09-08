%SPIEGAZIONE CONTROFATTUALE (ECO)
%dato output(X), trovare qual'è il subset di feature più piccolo possibile che mi porta ad un risultato diverso
%scegli se modificare o meno una feature
%esplora il percorso che ti porta se espori con quelle feature
%se il percorso porta ad un risultato diverso, conta quante feature hai modificato e fai in modo che sia il numero minimo possibile

fmod(X,Y) | fnonmod(X,Y) :- input(X,Y).
ecofeature(X,0) :- fmod(X,1).
ecofeature(X,1) :- fmod(X,0).
ecofeature(X,Y) :- fnonmod(X,Y).

ecopasso(0,P) :- root(P).
 
ecopasso(P+1,N2) :- ecopasso(P,N1), edge(N1,N2,"+"), node(N1,V1), node(N2,_), ecofeature(V1,1).
ecopasso(P+1,N2) :- ecopasso(P,N1), edge(N1,N2,"-"), node(N1,V1), node(N2,_), ecofeature(V1,0).

outputName(Y) :- output(X), node(X,Y).
:~ #count{ X : fmod(X,Y)} = S. [S@1]
ecooutput(X) :- #max{ P : ecopasso(P,_) } = M, ecopasso(M,X).
:- ecooutputname(X), outputName(X).
ecooutputname(Y) :- ecooutput(X), node(X,Y).


#show ecooutput/1.
#show ecooutputname/1.
#show fmod/2.