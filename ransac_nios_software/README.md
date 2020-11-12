### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##

# ransac_desktop
Esta pasta contém arquivos relativos ao projeto do Intel Quartus Prime que contém a implementação do algoritmo RANSAC para Nios II e Cyclone IV E e um testbench rudimentar da sua funcionalidade.

## Diferenças da implementação Nios II para Desktop

### Macros

#### Endereços de memória

Esses macros definem endereços de memória e dão nomes aos mesmos:

```c
#define END_BASE_MEMO (int *) 0x0000 
#define ACUMULADOR (int *) 0x5018 
#define MEDIDOR_LEITURA (int *) 0x5014 
#define MEDIDOR_ESCRITA (int *) 0x5010 
```

#### Semente

Define a semente do gerador aleatório

```c
#define SEED 4096
```

#### Macros relacionados ao testbench e profiling

STOP, INT, FLOAT e TIME_F definem constantes que quando escritas no endereço do acumulador, informam ao testbench qual o tipo do dado que será escrito em seguida, de modo que o testbench pode tomar uma ação de acordo. (Ver explicação do testbench) 

DEBUG_PRINT, caso esteja definido, faz com que o código utilize o testbench para imprimir diversos valores na tela, se nÃo estiver definido, não será feita essa impressão, será apenas executado o algoritmo.

TIME(s) define um macro que representa nada quando DEBUG_PRINT não estiver definido e representa uma função do profiling quando DEBUG_PRINT está definida.

```c
#define STOP 0xffffffff
#define DEBUG_PRINT
#ifdef DEBUG_PRINT
#define FLOAT 0xfffffffe
#define INT 0xfffffffd
#define TIME_F 0xfffffffc
#define TIME(s) pause_print_time(s)
#else
#define TIME(s)
#endif
```

Os macros abaixo representam mnemônicos para várias seções do código, que serão impressas durante o profiling, compondo um conjunto de dados a ser analisado posteriormente pelo script [ransac_profiler.c](https://github.com/gsimoes00/engg57-ransac/blob/main/ransac_profiler/ransac_profiler.py).

A letra representa a seção, 0 representa entrada e 1 representa saída.

[Ver README do profiling.](https://github.com/gsimoes00/engg57-ransac/blob/main/ransac_profiler)


```c
#define FUN_COPY_START "a 0"
#define FUN_COPY_END "a 1"
#define FUN_COMP_START "b 0"
#define FUN_COMP_END "b 1"
#define FUN_DSPL_START "c 0"
#define FUN_DSPL_END "c 1"
#define FUN_LREG_START "d 0"
#define FUN_LREG_END "d 1"
#define FUN_DSPP_START "e 0"
#define FUN_DSPP_END "e 1"
#define ALG_START "f 0"
#define ALG_END "f 1"
#define ITER_START "g 0"
#define ITER_END "g 1"
#define STEP_1_START "h 0"
#define STEP_1_END "h 1"
#define SELECT_2P_START "i 0"
#define SELECT_2P_END "i 1"
#define STEP_2_START "j 0"
#define STEP_2_END "j 1"
#define STEP_3_START "k 0"
#define STEP_3_END "k 1"
#define INLIER_CHECK_START "l 0"
#define INLIER_CHECK_END "l 1"
#define UPDATE_BEST_START "m 0"
#define UPDATE_BEST_END "m 1"
#define STEP_4_START "n 0"
#define STEP_4_END "n 1"
#define LREG_MED_START "o 0"
#define LREG_MED_END "o 1"
#define LREG_SUM_START "p 0"
#define	LREG_SUM_END "p 1"
#define LREG_RES_START "q 0"
#define LREG_RES_END "q 1"
```

##
### Funções

As funções a seguir utilizam o endereço do acumulador como se fosse uma saída padrão, imprimindo diversos caracteres e símbolos para a mesma. Algumas dessas funções utilizam uma constante previamente definida, antes do símbolo, para explicar o seu significado, como INT, FLOAT e TIME_F por exemplo. A constante STOP não é seguida por nenhum símbolo, apenas pausa a simulação. Se nenhuma constante for fornecida, o símbolo é interpretado como um caractere de uma string e impresso.

A função print_str recebe uma string e imprime a mesma no acumulador.

```c
#ifdef DEBUG_PRINT
void print_str(char * str)
{
	int i;
	for(i = 0; str[i] != 0; i++)
	{
		*ACUMULADOR = str[i];
	}
}
```

A função print_int recebe um número inteiro e imprime o mesmo no acumulador.

```c
void print_int(int i)
{
	*ACUMULADOR = INT;
	*ACUMULADOR = i;
}
```

A função print_float recebe um número real e imprime o mesmo no acumulador. O número é impresso como um inteiro ponto fixo decimal de 6 casas após a vírgula, por isso está multiplicado por 100000.

```c
void print_float(float f)
{
	*ACUMULADOR = FLOAT;
	*ACUMULADOR = (int) (f*100000);
}
```

A função pause_print_time pausa o medidor de desempenho, imprime uma string representativa do tempo e da seção atual do algoritmo e então continua a contagem do medidor. Ela é útilizada pelo macro TIME(s) para o profiling.

```c
void pause_print_time(char * stamp)
{
	*MEDIDOR_ESCRITA = 2;
	print_str("@T ");
	//leitura do medidor le sempre a mesma coisa por algum motivo
	//print_int(*MEDIDOR_ESCRITA);
	*ACUMULADOR = TIME_F;
	print_str(" ");
	print_str(stamp);
	print_str("\n");
	*MEDIDOR_ESCRITA = 1;
}
#endif
```

A função stop_simulation pausa a simulação do testbench no Mentor ModelSim e devolve o controle interativo para o usuário. Ela é utilizada ao término do algoritmo.

```c
void stop_simulation(void)
{
	*ACUMULADOR = STOP;
}
```

##
### Exemplo de uso do macro TIME(s) para medir o tempo de execução de uma seção

```c
TIME(SELECT_2P_START);
point1 = (rand()%NUM_POINTS_)*2;
point2 = (rand()%NUM_POINTS_)*2;
bestP1 = point1;
bestP2 = point2;
currentDist = distSquarePointPoint(data_points_[X(point1)], data_points_[Y(point1)], data_points_[X(point2)], data_points_[Y(point2)]);
bestDist = currentDist;
TIME(SELECT_2P_END);
```

##
### Impressão de dados

```c
#ifdef DEBUG_PRINT
//imprimir semente
print_str("@DATA SEED ");
print_int(SEED);
print_str("\n\n");
#endif
```

```c
#ifdef DEBUG_PRINT
//uma reta encontrada (ou nao)
if(modelFound == 0)
{
    //nao achou
    //printf("NOT OK!\nIteracoes: %i\nInliers: %i\n", i+1, bestInliers);
    print_str("\n@DATA OK 0\n@DATA ITERATIONS ");
    print_int(i+1);
    print_str("\n@DATA INLIERS ");
    print_int(bestInliers);
    print_str("\n");
}
else
{
    //achou
    //printf("OK!\nIteracoes: %i\nInliers: %i\nEquacao: Y = %f + %fX\n", i+1, bestInliers, result.a, result.b);
    print_str("\n@DATA OK 1\n@DATA ITERATIONS ");
	print_int(i+1);
	print_str("\n@DATA INLIERS ");
	print_int(bestInliers);
	print_str("\n@DATA EQUATION 1 ");
	print_float(result.a);
	print_str(" ");
	print_float(result.b);
	print_str("\n");
}

print_str("\n");
#endif
```

##
### Fim da execução do algoritmo

```c
//parar simulacao
stop_simulation();

//ficar travado no final
while(1);
```

## Testbench

O testbench é bastante rudimentar porém flexível, ele permite capturar tudo que é escrito no acumulador e usar isso como comandos para efetuar impressões de dados como caracteres, inteiros, números reais ou a quantidade de ciclos contados pelo medidor de desempenho. Possui também a funcionalidade de pausar a simulação de dentro do código do Nios II. O acumulador não mais tem a função de somar valores, ele apenas armazena esses valores momentâneamente e serve como uma saída padrão de impressão.

```SystemVerilog
`timescale 10ns/10ns

module AcumuladorNiosTB;

reg	CLOCK_50;
reg	[3:3] KEY;
reg	[1:0] SW;
wire	[15:0] LEDR;

AcumuladorNios DUV (CLOCK_50, KEY, SW, LEDR);

real temp;

always #1 CLOCK_50 = !CLOCK_50;

initial
	begin
		
		$display("\n########## INICIO DO TESTBENCH ##########\n");
		
		CLOCK_50 = 0;
		KEY[3] = 0;
		SW[0] = 0;
		SW[1] = 0;
		#11 KEY[3] = 1;
		
	end
	
initial 
	begin
		forever
			begin
			
				@(posedge DUV.b2v_inst1.acumulador.write);
	
				case (DUV.b2v_inst1.acumulador.writedata)
				
					32'hffffffff: 
						begin
							$display("\n########## FIM DO TESTBENCH ##########\n");
							$stop;
						end
					32'hfffffffe:
						begin
							@(posedge DUV.b2v_inst1.acumulador.write);
							temp = DUV.b2v_inst1.acumulador.writedata;
							temp = temp / 100000;
							$write("%f", temp);
						end
					32'hfffffffd:
						begin
							@(posedge DUV.b2v_inst1.acumulador.write);
							$write("%d", DUV.b2v_inst1.acumulador.writedata);
						end
					32'hfffffffc:
						begin
							$write("%d", DUV.b2v_inst1.medidordesempenho.CC.clk_count);
						end
					default: $write("%c", DUV.b2v_inst1.acumulador.writedata[7:0]);
					
				endcase
				
			end
	
	end


endmodule

```

##
### Saída típica de uma simulação:

```
########## INICIO DO TESTBENCH ##########
# 
# @DATA SEED       4096
# 
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
# 
# @DATA OK 1
# @DATA ITERATIONS          4
# @DATA INLIERS        145
# @DATA EQUATION 1 250.841440 42948.693740
# 
# 
########## FIM DO TESTBENCH ##########
# 
# ** Note: $stop    : D:/Projetos/Quartus/AcumuladorNios/SistemaEmbarcado/testbench/mentor/../../../AcumuladorNiosTB.v(55)
#    Time: 809775350 ns  Iteration: 8  Instance: /AcumuladorNiosTB
# Break in Module AcumuladorNiosTB at D:/Projetos/Quartus/AcumuladorNios/SistemaEmbarcado/testbench/mentor/../../../AcumuladorNiosTB.v line 55
```

##
### Acerca do tempo de simulação e da precisão da medição

A combinação de caso e semente atualmente escolhidos é do conjunto de dados "cross" com semente 4096. Com as constantes atuais, o resultado encontrado provavelmente está errado, porém esses valores foram mantidos pois o resultado final em si não altera o comportamento do algoritmo e o seu custo de execução, e esses valores específicos fazem o algoritmo executar 4 iterações, que é um número nem muito pequeno nem muito grande, bom para avaliar o comportamento do mesmo.

O tempo de execução dessa combinação é de cerca de meio segundo simulado e o tempo de simulação é de algumas horas, e com a impressão dos dados do profiling, esse tempo é ainda maior, porém esse tempo adicional de impressão não é contabilizado no profiling, pois a função que faz a impressão dos tempos pausa o contador no início e só o retoma no final. Ainda assim vai existir alguma imprecisão de alguns ciclos de clock a cada medição devido a demora de fazer essas ações.

##
### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##
