import numpy as np
import pandas as pd
from funcoesTermosol import *
from trelica import *
from gauss import *

n_nos,matriz_nos,n_membros,matriz_incidencia,n_cargas,vetor_carregamento,n_restricoes,vetor_restricoes = importa('entrada-modelo.xls')

lock_flattened = [int(i) for i in vetor_restricoes.flatten()]
carregamento_flatenned = vetor_carregamento.flatten()
lis_no = []
for index_no in range(n_nos):
    x = matriz_nos[0,index_no]
    y = matriz_nos[1,index_no]
    x_numeracao_liberdade = 2*index_no
    y_numeracao_liberdade = 2*index_no+1
    x_lock = x_numeracao_liberdade in lock_flattened
    y_lock = y_numeracao_liberdade in lock_flattened
    x_carga = carregamento_flatenned[x_numeracao_liberdade]
    y_carga = carregamento_flatenned[y_numeracao_liberdade]
    no = No(matriz_nos[0,index_no],matriz_nos[1,index_no],x_lock,y_lock,x_carga,y_carga,x_numeracao_liberdade,y_numeracao_liberdade)
    lis_no.append(no)

lis_barra = []
for barra in matriz_incidencia:
    no1 = lis_no[int(barra[0])-1]
    no2 = lis_no[int(barra[1])-1]
    modulo_elasticidade = barra[2]
    area_secao = barra[3]
    lis_barra.append(Barra(no1,no2,modulo_elasticidade,area_secao))

matrix_rigidez = np.zeros(shape=(2*len(lis_no),2*len(lis_no)))
for i in range(len(lis_barra)):
    barra = lis_barra[i]
    matrix_rigidez[np.ix_(barra.dof,barra.dof)] += barra.k_local

vector_carga = np.zeros(shape=(2*len(lis_no),1))
for no in lis_no:
    vector_carga[no.x_numeracao_liberdade] = no.x_carga
    vector_carga[no.y_numeracao_liberdade] = no.y_carga

for no in lis_no:
    if no.x_lock:
        idx = no.x_numeracao_liberdade
        matrix_rigidez[idx,:] = 0
        matrix_rigidez[:,idx] = 0
        matrix_rigidez[idx,idx] = 1
        vector_carga[idx] = 0
    if no.y_lock:
        idx = no.y_numeracao_liberdade
        matrix_rigidez[idx,:] = 0
        matrix_rigidez[:,idx] = 0
        matrix_rigidez[idx,idx] = 1
        vector_carga[idx] = 0

det = np.linalg.det(matrix_rigidez)
u = np.linalg.solve(matrix_rigidez,vector_carga)
u_gauss = gaussSeidel(1000, 1e-20, matrix_rigidez, vector_carga)
inverte = np.linalg.inv(matrix_rigidez) @ vector_carga
print(inverte.shape)
print(matrix_rigidez.shape)

f = open('resultados.txt', 'w', encoding='utf-8')
f.write('número de nós = '+str(n_nos)+'\n')
f.write('número de membros = '+str(n_membros)+'\n')
f.write('número de cargas = '+str(n_cargas)+'\n')
f.write('número de restrições = '+str(n_restricoes)+'\n\n')
f.write('matriz de nós = \n')
f.write(str(matriz_nos) + '\n\n')
f.write('matriz de rigidez = \n')
f.write(str(matrix_rigidez) + '\n\n')
f.write('vetor de carga = \n')
f.write(str(vector_carga) + '\n\n')
f.write('deslocamentos (Numpy linalg solve) = \n')
f.write(str(u) + '\n\n')
f.write('deslocamentos (método Gauss-Seidel) = \n')
f.write(str(u_gauss))
f.write('\nmetodo 3 \n\n')
f.write(str(inverte) + '\n\n')
f.close()