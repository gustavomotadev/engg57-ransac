### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##

# ransac_desktop
Implementação em software para a plataforma Desktop PC do algoritmo RANSAC. Use os scripts segment_downsample.py para gerar pontos a partir de imagens e generate_c_header.py para gerar os cabeçalhos da linguagem C com os dados necessários. Compare os resultados com os fornecidos por ransac_python.py usando ransac_result_visualizer.py.

Os defines no topo do arquivo definem sobre quais dados o programa estará trabalhando.

Para economizar no custo computacional e evitar o cálculo de módulos e raízes quadradas, esse algoritmo trabalha com distâncias quadradas, ele também salva constantes mais utilizadas evitando calcular mais de uma vez onde possível.

## Constantes

#### DIST_TH: 
Distância máxima da reta aleatoriamente sorteada para o ponto ser considerado um inlier (Não é necessário fornecer o quadrado da distância, esse valor é calculado em outro macro).

#### MAX_IT: 
Número máximo de iterações aleatórias do algoritmo RANSAC sobre os dados antes de desistir de encontrar um modelo válido. Se esse número for alcançado sem sucesso, o algoritmo para sem fornecer uma reta.

#### INLIER_TH:
Número mínimo de inliers a partir do qual o algoritmo RANSAC decide que encontrou um modelo válido e para as iterações aleatórias para fazer regressão linear.

#### MIN_SAMPLE_DIST:
Essa constante faz parte de uma heurística que evita sortear aleatoriamente pontos muito próximos, que produziriam um modelo que é valido apenas localmente e não representa todos os dados. Essa constante define a distância mínima entre 2 pontos sorteados para aceitá-los. (Não é necessário fornecer o quadrado da distância, esse valor é calculado em outro macro).

#### MAX_RANDOM_TRIES:
Número máximo de vezes que a heurística será aplicada no sorteio dos pontos, se esse valor for atingido sem sucesso, o par de pontos mais distantes sorteado até agora será escolhido.

## Macros

#### X(p)
Retorna o próprio p, na prática é utilizado para se referir ao valor x no vetor de dados de pontos de forma mais legível.

#### Y(p)
Retorna p+1, na prática é utilizado para se referir ao valor y no vetor de dados de pontos de forma mais legível.

#### MASK(p)
Retorna metade de p usando deslocamento binário para a direita. Utilizado para se referir ao vetor de máscara de inliers, que tem metade do tamanho do vetor de dados dos pontos.

## Definições do Cabeçalho Automaticamente Gerado

#### NUM_POINTS_
Número de pontos fornecidos pelo cabeçalho.
#### DATA_SIZE_
Tamanho do vetor de dados de x e y dos pontos fornecido pelo cabeçalho.
#### data_points_[DATA_SIZE_]
Vetor de dados de x e y dos pontos fornecido pelo cabeçalho.
#### inlier_mask_[NUM_POINTS_]
Vetor de máscara de inliers, se o índice do ponto tiver valor zero nessa máscara ele é um outlier, se for 1 ele é um inlier (Pode ser expandido para múltiplas retas com modificações no algoritmo usando valores 2, 3, 4...).

## Tipos

#### ModelConstants
Estrutura que guarda cosntantes referentes ao modelo (reta) sorteado que são utilizadas por outras funções.
##### -> deltaX = x2 - x1
É equivalente ao coeficiente B na forma padrão da equação da reta: Ax + By + C = 0.
##### -> deltaY = y2 - y1
É equivalente ao coeficiente A na forma padrão da equação da reta: Ax + By + C = 0.
##### -> alpha = 1 / (deltaX² + deltaY²)
Aparece como fator multiplicador no cálculo do quadrado da distância entre ponto e reta.

[Link para artigo da Wikipedia sobre a formula da distância entre ponto e reta.](https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points)
##### -> beta = x2\*y1 - y2\*x1
É equivalente ao coeficiente C na forma padrão da equação da reta: Ax + By + C = 0.

#### RegressionResult
Estrutura que contém o resultado de uma regressão linear simples, ou seja, seus coeficientes.

##### -> a
##### -> b
A regressão está na forma: Y = A + BX.

[Link para artigo da Wikipedia sobre a regressão linear simples.](https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line)

## Funções

#### void computeConstants(ModelConstants * cts, unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2)

Faz o cálculo das constantes a partir dos valores x1, y1, x2, y2 e guarda o resultado em cts.

#### float distSquarePointLine(ModelConstants * cts, unsigned char x3, unsigned char y3)
Calcula a distância quadrada entre o ponto (x3, y3) e a reta representada por cts, retorna o valor em float.

Fórmula: D² = alpha * (deltaY\*x3 - deltaX\*y3 + beta)².

[Link para artigo da Wikipedia sobre a formula da distância entre ponto e reta.](https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points)

#### void linearRegression(RegressionResult * res, const unsigned char * data, const unsigned char * mask)
Efetua uma regressão linear simples utilizando o método dos mínimos quadrados. Recebe os vetores de dados e a máscara de inliers pois considera apenas os pontos inliers na regressão, guarda o resultado em res.

[Link para artigo da Wikipedia sobre a regressão linear simples.](https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line)

#### float distSquarePointPoint(unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2)
Calcula a distância quadrada entre os pontos (x1, y1) e (x2, y2), retorna o valor em float.

Fórmula: d² = deltaX² + deltaY². (deltaX = x2-x1; deltaY = y2-y1).

[Link para artigo da Wikipedia sobre o Teorema de Pitágoras.](https://en.wikipedia.org/wiki/Pythagorean_theorem)


## Algoritmo

#### Passo 1:

Selecionar aleatoriamente 2 pontos do conjunto de dados utilizando os critérios da heurística descrita acima. Mínima distância MIN_SAMPLE_DIST, máximo de tentativas MAX_RANDOM_TRIES.

#### Passo 2:
Encontrar os parâmetros do modelo (reta). Ou seja, descobrir qual reta passa por esses dois pontos e calcular suas constantes, deltaX, deltaY, alpha, beta.

#### Passo 3:
Computar quantos pontos do conjunto de dados se ajustam à reta (inliers) de acordo com uma tolerância previamente estabelecida por DIST_TH. Ou seja, quantos dos pontos estão de acordo com o modelo suposto. Enquanto faz essa análise, produzir uma máscara de inliers colocando 1 nos pontos que concordam e 0 nos que discordam.

#### Passo 4:
Se o numero de inliers for satisfatório de acordo com uma tolerância previamente estabelecida por INLIER_TH, reestimar o modelo utilizando os inliers identificados através da regressão linear simples e terminar o loop.

#### Passo 5:
Se nao cumpriu os requisitos do passo 4, e ainda restam tentativas dentro do máximo MAX_IT, repetir o loop. Caso contrário terminar apresentando o resultado encontrado ou nenhuma resposta.

## Exemplo de Saída Típica com Sucesso

```
OK!
Iteracoes: 1
Inliers: 198
Equacao: Y = 28.170586 + 0.739307X
@DATA_START
@DATA_POINTS
26,50,30,50,30,54,30,58,30,218,30,222,34,50,34,54,34,58,34,62,34,214,34,218,34,222,38,54,38,58,38,62,38,66,38,210,38,214,38,218,38,222,38,226,42,54,42,58,42,62,42,66,42,206,42,210,42,214,42,218,42,222,42,226,46,58,46,62,46,66,46,70,46,206,46,214,46,218,46,222,46,226,50,58,50,62,50,66,50,70,50,202,50,206,50,210,50,214,50,218,50,222,54,66,54,70,54,74,54,198,54,202,54,206,54,210,54,214,58,66,58,70,58,74,58,78,58,194,58,198,58,202,58,206,58,210,58,214,62,66,62,70,62,74,62,78,62,82,62,190,62,198,62,202,62,206,62,210,66,70,66,74,66,78,66,82,66,190,66,194,66,198,66,202,66,206,70,70,70,74,70,86,70,186,70,190,70,194,70,198,70,202,74,78,74,82,74,90,74,182,74,186,74,190,74,194,74,198,78,78,78,82,78,86,78,90,78,178,78,182,78,186,78,190,78,194,82,78,82,82,82,86,82,94,82,170,82,174,82,178,82,182,82,186,82,190,82,194,86,98,86,166,86,170,86,174,86,178,86,182,86,186,86,190,90,98,90,102,90,162,90,166,90,170,90,174,90,178,90,182,94,94,94,98,94,102,94,106,94,158,94,162,94,166,94,170,94,174,94,178,98,94,98,98,98,102,98,106,98,110,98,154,98,158,98,162,98,166,98,170,98,174,102,98,102,102,102,106,102,110,102,146,102,154,102,158,102,162,102,166,106,98,106,102,106,106,106,110,106,114,106,142,106,146,106,150,106,166,110,102,110,106,110,110,110,114,110,118,110,138,110,142,110,146,110,150,110,154,110,158,114,106,114,110,114,114,114,118,114,138,114,142,114,150,114,154,118,114,118,118,118,122,118,130,118,138,118,142,118,146,118,150,122,110,122,114,122,118,122,122,122,126,122,130,122,134,122,138,122,142,122,146,126,114,126,118,126,122,126,126,126,130,126,134,126,138,130,118,130,122,130,126,130,130,130,134,130,138,134,118,134,122,134,126,134,130,134,134,134,138,138,114,138,122,138,126,138,130,138,134,138,142,142,110,142,114,142,118,142,122,142,126,142,130,142,134,142,142,146,110,146,114,146,118,146,122,146,126,146,130,146,134,146,138,146,146,150,102,150,106,150,114,150,122,150,126,150,130,150,134,150,138,150,142,150,146,154,98,154,106,154,114,154,130,154,134,154,138,154,142,154,146,154,150,158,94,158,98,158,102,158,106,158,110,158,114,158,134,158,138,158,142,158,146,158,150,158,154,162,86,162,90,162,94,162,106,162,110,162,142,162,146,162,150,162,154,162,158,166,82,166,86,166,90,166,94,166,98,166,146,166,150,166,154,166,158,166,162,170,78,170,86,170,94,170,98,170,150,170,154,170,158,170,162,174,74,174,78,174,82,174,86,174,154,174,158,174,162,174,166,178,70,178,78,178,86,178,158,178,162,178,166,178,170,182,62,182,66,182,70,182,74,182,78,182,158,182,162,182,166,182,170,186,58,186,62,186,70,186,74,186,78,186,162,186,166,186,170,186,174,190,54,190,58,190,62,190,66,190,70,190,74,190,166,190,170,190,174,190,178,194,50,194,54,194,58,194,62,194,66,194,70,194,170,194,174,194,178,194,182,198,46,198,50,198,54,198,58,198,62,198,66,198,170,198,174,198,178,198,182,202,50,202,54,202,58,202,174,202,178,202,182,202,186,206,42,206,46,206,50,206,54,206,178,206,182,206,186,206,190,210,38,210,42,210,46,210,50,210,54,210,182,210,186,210,190,214,42,214,46,214,182,214,186,214,190,214,194,218,46,218,186,218,190,218,194,218,198,222,42,222,190,222,194,222,198,222,202,226,194,226,198,226,202,226,206,230,198,230,202,230,206,230,210,234,202,234,206,234,210,234,214,
@INLIER_MASK
1,1,1,1,0,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,1,0,0,1,1,1,1,0,1,1,1,0,0,1,1,1,0,1,1,1,0,1,1,0,0,1,1,0,0,
@EQUATIONS
1, 28.170586, 0.739307
@DATA_END
```
##

### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##
