### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##

# ransac_profiler

Esta pasta contém arquivos e scripts que auxiliam na avaliação do desempenho do algoritmo.

## ransac_profiler.py

Esse script recebe um arquivo que possui linhas similares às mostradas abaixo, opera sobre elas e então fornece os dados sobre todas seções do algoritmo, incluindo o mnemônico e a string que representam a seção, o número de vezes que foi executada, o tempo total de execução e a porcentagem que ele representa do total. O algoritmo imprime essas informações na tela e também em arquivo, ordenadas do menor para o maior tempo.

```
# @T         85 f 0
# @T        321 g 0
# @T        454 h 0
# @T        587 i 0
# @T      13999 e 0

...

# @T   25419600 q 1
# @T   25419733 d 1
# @T   25419930 n 1
# @T   25420063 g 1
# @T   25420203 f 1
```

## Análise da implementação em software para Nios II

O arquivo de saída com os resultados para a implementação do algoritmo RANSAC em software para a plataforma Nios II, no caso de teste escolhido estão abaixo:

```
| Label: a | Section: FUN_COPY     | Executions:     2 | Mean:       156 | Time:       312 | %:   0.001 |
| Label: m | Section: UPDATE_BEST  | Executions:     4 | Mean:       204 | Time:       816 | %:   0.003 |
| Label: q | Section: LREG_RES     | Executions:     1 | Mean:      6981 | Time:      6981 | %:   0.028 |
| Label: b | Section: FUN_COMP     | Executions:     4 | Mean:      8846 | Time:     35382 | %:   0.143 |
| Label: j | Section: STEP_2       | Executions:     4 | Mean:      9332 | Time:     37330 | %:   0.151 |
| Label: e | Section: FUN_DSPP     | Executions:     5 | Mean:      7602 | Time:     38012 | %:   0.154 |
| Label: i | Section: SELECT_2P    | Executions:     5 | Mean:     22509 | Time:    112545 | %:   0.456 |
| Label: h | Section: STEP_1       | Executions:     4 | Mean:     28587 | Time:    114349 | %:   0.463 |
| Label: o | Section: LREG_MED     | Executions:     1 | Mean:    424806 | Time:    424806 | %:   1.721 |
| Label: p | Section: LREG_SUM     | Executions:     1 | Mean:   1743982 | Time:   1743982 | %:   7.065 |
| Label: d | Section: FUN_LREG     | Executions:     1 | Mean:   2175952 | Time:   2175952 | %:   8.815 |
| Label: n | Section: STEP_4       | Executions:     4 | Mean:    544880 | Time:   2179522 | %:   8.829 |
| Label: c | Section: FUN_DSPL     | Executions:  1724 | Mean:     12134 | Time:  20918899 | %:  84.745 |
| Label: l | Section: INLIER_CHECK | Executions:  1724 | Mean:     12869 | Time:  22185515 | %:  89.876 |
| Label: k | Section: STEP_3       | Executions:     4 | Mean:   5588054 | Time:  22352215 | %:  90.551 |
| Label: g | Section: ITER         | Executions:     4 | Mean:   6171038 | Time:  24684152 | %:  99.998 |
| Label: f | Section: ALG          | Executions:     1 | Mean:  24684596 | Time:  24684596 | %: 100.000 |
```

Essa saída representa cada uma das seções do código por uma letra (mnemônico) e uma string, algumas delas estão dentro das outras e por isso a porcentagem não soma 100%. O profiling foi feito com base em simulação e testbench no ModelSim da implementação para Nios II do algoritmo RANSAC.

A seção f, ou ALG, corresponde ao total do algoritmo e a seção g, ou ITER, corresponde a cada uma de suas iterações, por isso ambas somam aproximadamente 100%.

A seção k, ou STEP_3, corresponde ao passo 3 do algoritmo, que consome 90.551% do tempo do mesmo.

A seção l, ou INLIER_CHECK, corresponde à checagem de inliers, que faz parte do passo 3, ela consome 89.876% do tempo do algoritmo.

A seção c, ou FUN_DSPL, corresponde à função que calcula distância entre ponto e reta, que faz parte da checagem de inliers, ela consome 84.745% do tempo do algoritmo.

89.876% - 84.745% = 5.131% corresponde ao restante da checagem de inliers que não faz parte da função citada, ela corresponde a operações de comparação, incremento e atribuição em vetor.

Aproximadamente 8.829% do tempo corresponde às seções n, ou STEP_4, que é o passo 4 do algoritmo, e d, ou FUN_LREG, que é a função de regressão linear, que domina completamente o tempo nesse passo, sendo 7.065% correspondente à seção p, ou LREG_SUM, que é o cálculo de um somatório e 1.721% a seção o, ou LREG_MED, que faz cálculo de médias.

Todo o restante do algoritmo é irrelevante em termos de tempo, correspondendo a menos de 1% somando todas as seções restantes.

### Prioridade de desenvolvimento no caso de implementação via software

Ficou claro através da análise, que a função mais crítica dessa implementação é a FUN_DSPL, que corresponde a aproximadamente 85% do tempo do algoritmo, e logo em seguida a FUN_LREG, que consome aproximadamente 9% do tempo, juntas essas funções representam aproximadamente 94% do tempo total do algoritmo, sendo infrutífero tentar otimizar qualquer outra seção do mesmo. 

Portanto o objetivo de desenvolvimento será implementar um acelerador de hardware para cálculo de distância entre ponto e reta e, caso haja tempo hábil após isso, implementar um acelerador de cálculo de regressão linear.

### Acerca da precisão e erros nas medidas

Toda medida efetuada aqui possui um erro de 23 ciclos, que é o tempo necessário para uma escrita, que serve para parar o contador de clocks. Esse acréscimo não é relevante na medida do tempo em que iniciou a seção, já que ele acontece antes dessa medida, sendo contabilizado apenas uma vez, quando é feita a medida do tempo de fim da seção, sabendo disso, basta subtrair 23 ciclos de cada medida individual no script Python para ter uma análise livre desse problema, que é o que foi feito.

## Análise da implementação com acelerador para Nios II

O arquivo de saída com os resultados para a implementação do algoritmo RANSAC com acelerador para a plataforma Nios II, no mesmo caso de teste acima e com a mesma semente estão abaixo:

```
| Label: a | Section: FUN_COPY     | Executions:     2 | Mean:       156 | Time:       312 | %:   0.013 |
| Label: m | Section: UPDATE_BEST  | Executions:     4 | Mean:       204 | Time:       816 | %:   0.034 |
| Label: q | Section: LREG_RES     | Executions:     1 | Mean:      6849 | Time:      6849 | %:   0.286 |
| Label: e | Section: FUN_DSPP     | Executions:     5 | Mean:      1993 | Time:      9963 | %:   0.417 |
| Label: b | Section: FUN_COMP     | Executions:     4 | Mean:      2625 | Time:     10501 | %:   0.439 |
| Label: j | Section: STEP_2       | Executions:     4 | Mean:      3112 | Time:     12449 | %:   0.521 |
| Label: i | Section: SELECT_2P    | Executions:     5 | Mean:     16831 | Time:     84153 | %:   3.519 |
| Label: h | Section: STEP_1       | Executions:     4 | Mean:     21138 | Time:     84550 | %:   3.535 |
| Label: o | Section: LREG_MED     | Executions:     1 | Mean:     88336 | Time:     88336 | %:   3.693 |
| Label: l | Section: INLIER_CHECK | Executions:  1724 | Mean:       166 | Time:    285876 | %:  11.953 |
| Label: k | Section: STEP_3       | Executions:     4 | Mean:    113826 | Time:    455304 | %:  19.037 |
| Label: p | Section: LREG_SUM     | Executions:     1 | Mean:   1739205 | Time:   1739205 | %:  72.719 |
| Label: d | Section: FUN_LREG     | Executions:     1 | Mean:   1834591 | Time:   1834591 | %:  76.708 |
| Label: n | Section: STEP_4       | Executions:     4 | Mean:    459545 | Time:   1838180 | %:  76.858 |
| Label: g | Section: ITER         | Executions:     4 | Mean:    597805 | Time:   2391219 | %:  99.981 |
| Label: f | Section: ALG          | Executions:     1 | Mean:   2391663 | Time:   2391663 | %: 100.000 |
```

A seção f, ou ALG, corresponde ao total do algoritmo e a seção g, ou ITER, corresponde a cada uma de suas iterações, por isso ambas somam aproximadamente 100%.

A seção n, ou STEP_4, agora corresponde a quase 77% do tempo do algoritmo, quando antes era apenas 8.8%, sendo dominada pelo cálculo de regressão linear, que é a seção d, ou FUN_LREG, dentro dessa seção temos as seções p e o, que são LREG_SUM e LREG_MED, correspondendo a 72.719% e 3.693% do tempo do algoritmo respectivamente. LREG_MED teve seu tempo reduzido devido a substituícao de 2 variáveis por inteiros.

A seção k, ou STEP_3 agora corresponde a apenas 19% do tempo aproximadamente, sendo que antes era acima de 90%. Esta seção tem em seu interior a seção l, ou INLIER_CHECK, que foi o principal alvo de otimização, tendo sua porcentagem reduzida de um pouco abaixo de 90% para cerca de 12%.

A seção h, ou STEP_1, passou a ser significativa devido a queda no tempo das outras e agora representa 3.5% do tempo.

Todo o restante do algoritmo é irrelevante em termos de tempo, correspondendo a menos de 2% somando todas as seções restantes.

## Comparação do tempo médio para cada seção nas duas implementações

Na lista abaixo é possível observar a queda absoluta no tempo médio de cada seção, também a queda percentual e a taxa de redução.

```
| Label: a | Section: FUN_COPY     | Mean:         0 | %:  -0.000 | Factor:   1.000 |
| Label: m | Section: UPDATE_BEST  | Mean:         0 | %:  -0.000 | Factor:   1.000 |
| Label: p | Section: LREG_SUM     | Mean:     -4777 | %:  -0.274 | Factor:   1.003 |
| Label: q | Section: LREG_RES     | Mean:      -132 | %:  -1.891 | Factor:   1.019 |
| Label: n | Section: STEP_4       | Mean:    -85335 | %: -15.661 | Factor:   1.186 |
| Label: d | Section: FUN_LREG     | Mean:   -341361 | %: -15.688 | Factor:   1.186 |
| Label: i | Section: SELECT_2P    | Mean:     -5678 | %: -25.225 | Factor:   1.337 |
| Label: h | Section: STEP_1       | Mean:     -7449 | %: -26.057 | Factor:   1.352 |
| Label: j | Section: STEP_2       | Mean:     -6220 | %: -66.652 | Factor:   2.999 |
| Label: b | Section: FUN_COMP     | Mean:     -6221 | %: -70.326 | Factor:   3.370 |
| Label: e | Section: FUN_DSPP     | Mean:     -5609 | %: -73.783 | Factor:   3.814 |
| Label: o | Section: LREG_MED     | Mean:   -336470 | %: -79.206 | Factor:   4.809 |
| Label: f | Section: ALG          | Mean: -22292933 | %: -90.311 | Factor:  10.321 |
| Label: g | Section: ITER         | Mean:  -5573233 | %: -90.313 | Factor:  10.323 |
| Label: k | Section: STEP_3       | Mean:  -5474228 | %: -97.963 | Factor:  49.093 |
| Label: l | Section: INLIER_CHECK | Mean:    -12703 | %: -98.710 | Factor:  77.524 |
```

De tal modo que podemos observar que a seção otimizada reduziu em mais de 98% seu tempo de execução e o algoritmo foi acelerado por um fator 10.

##
### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##