%SPIEGAZIONE ADDUTTIVA (EMC)
%dato output(X), trovare qual'è il subset di feature più piccolo possibile che mi porta allo stesso risultato
%scegli se prendere o meno una feature
%esplora il percorso che ti porta se espori con quelle feature
%se il percorso porta allo stesso risultato, conta quante feature hai e fai in modo che sia il numero minimo possibile


fpresa(X,Y) | fnonpresa(X,Y) :- input(X,Y).
fpresa(X,Y) :- root(X), input(X,Y).

passoe(0,P) :- root(P).
 
passoe(P+1,N2) :- passoe(P,N1), edge(N1,N2,"+"), node(N1,V1), node(N2,_), fpresa(V1,1).
passoe(P+1,N2) :- passoe(P,N1), edge(N1,N2,"-"), node(N1,V1), node(N2,_), fpresa(V1,0).
 
:- #max{ P : passoe(P,_)} = M, passoe(M,X), not output(X).
:~ #count{ X : fpresa(X,Y)} = S. [S@1]

#show fpresa/2.