%Calcola la classificazione (inferenza)
passo(0,P) :- root(P).
 
passo(P+1,N2) :- passo(P,N1), edge(N1,N2,"+"), node(N1,V1), node(N2,_), input(V1,1).
passo(P+1,N2) :- passo(P,N1), edge(N1,N2,"-"), node(N1,V1), node(N2,_), input(V1,0).
 
output(X) :- #max{ P : passo(P,_) } = M, passo(M,X).

outputName(Y) :- output(X), node(X,Y).

#show output/1.
#show outputName/1.