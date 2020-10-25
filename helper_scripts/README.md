# helper_scripts
Esta pasta contém arquivos e scripts que auxiliam no desenvolvimento e testes.

## Pastas

### images
Contém imagens que servem como fonte dos dados e tambem imagens salvas pelos scripts como resultado dessa extração de dados.
### tsv
Contém arquivos de valores separados por tabs, que possuem as coordenadas dos pontos obtidos das imagens, a serem processadas por outros scripts.
### headers
Contém os headers .h da linguagem C automaticamente gerados pelos scripts dessa pasta, para serem incluidos em ransac.c.

## Scripts

##

### segment_downsample.py
Faz o processo de selecionar cor na imagem, segmentar, reduzir a quantidade de samples e extrair os dados na forma de arquivo tsv, opcionalmente pode mostrar imagens do resultado e/ou salvá-las.
#### Uso1: $ segment_downsample.py --all (--save, --show, --x2/--x4/--x8/--x[0-9]+)
#### Uso2: $ segment_downsample.py file0 file1 file2 ... (--save, --show, --x2/--x4/--x8/--x[0-9]+)
##### --all: Executa o script em todas as imagens da pasta "image"
##### --xN: Substituir "N" por um numero inteiro fará um downsample por N. Downsample fracionário não é suportado.
##### --show: Mostra uma imagem do processo executado.
##### --save: Salva a imagem que mostra o processo executado na pasta "images".
##### file0 file1 file2 [...]: Caso -all não seja informado, essa lista informará quais arquivos processar,  aceita caminhos absolutos ou relativos à pasta "images".

##

### generate_c_header.py
Recebe um arquivo tsv contendo os dados dos pontos e gera um arquivo header .h da linguagem C que deve ser incluído em ransac.c para facilitar o desenvolvimento.
#### Uso: $ ransac_python.py tsv_file
##### tsv_file é o arquivo a ser processado, só aceita caminhos absolutos.

##

### ransac_python.py
Executa o algoritmo RANSAC em Python fornecido pela biblioteca Sci-Kit Learn (sklearn) e mostra visualização na tela em forma de gráfico através da biblioteca matplotlib.
#### Uso: $ ransac_python.py tsv_file num_tries
##### tsv_file é o arquivo a ser processado, só aceita caminhos absolutos. 
##### num_tries é o número de retas que o script deve tentar encontrar nos dados.

##

### ransac_result_visualizer.py
Recebe na entrada padrão valores impressos por ransac.c e processa esses valores para exibir na tela um gráfico similar ao gerado por ransac_python.py. Para fins de teste e comparação. É recomendado usar um "pipe" para passar a saída padrão de ransac.c para a entrada padrão deste script.
#### Uso (exemplo): ./ransac.out | python3 ../helper_scripts/ransac_result_visualizer.py
##### Esse exemplo assume o uso de sistema operacional Unix-like, com ransac.c compilado para ransac.out, python3 presente no $PATH do sistema operacional e com $PWD na pasta "ransac_desktop".

##
