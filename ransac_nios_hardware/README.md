### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##

# ransac_nios_hardware
Esta pasta contém arquivos relativos ao projeto do Intel Quartus Prime que contém a implementação do algoritmo RANSAC para Nios II e Cyclone IV E usando um acelerador em hardware e um testbench rudimentar da sua funcionalidade.

## Diferenças da implementação com acelerador para versão software

### Macros

#### Endereços de memória

Estes macros definem os endereços do acelerador mapeado em memória para sua utilização.

```
#define INLIER_LEITURA (int *) 0x4000
#define INLIER_ESCRITA (int *) 0x4004
```

#### Macros de reset da máquina de estados

Este macro é utilizado para reiniciar a máquina de estados do acelerador quando necessário, bastando para isso escrevê-lo no mesmo.

```
#define RESET_INLIER 0xffffffff
```

#### Seções de execução

A seção "d", apesar de ainda estar no código, não existe mais, tendo sido substituída pelo acelerador.

```
#define FUN_LREG_START "d 0"
#define FUN_LREG_END "d 1"
```

##
### Tipos

Para permitir a construção de um acelerador mais eficiente, as constantes do modelo foram todas transformadas em números inteiros. Em específico, o parâmetro alpha foi substituído pelo seu inverso, denominado inv_alpha, o que possibilita eliminar um cálculo com números reais. Os valores que devem ser informados para o acelerador são: deltaX, deltaY, beta e inv_alpha multiplicado pelo quadrado do limiar, ou seja: inv_alpha*DIST_TH_SQ.

```
typedef struct ModelConstants
{

	int32_t deltaX, deltaY, beta, inv_alpha;

} ModelConstants;
```

##
### Funções

A forma de imprimir floats no testbench foi alterada, pois a anterior possuía problemas. Ver mais na seção apropriada abaixo.

[Ver testbench.](https://github.com/gsimoes00/engg57-ransac/tree/main/ransac_nios_hardware#Testbench)

```
void print_float(float f)
{
	*ACUMULADOR = 'f';
	*ACUMULADOR = '(';
	if(f < 0)
	{
		*ACUMULADOR = '-';
		f *= -1;
	}
	*ACUMULADOR = FLOAT;
	*ACUMULADOR = (int) f;
	*ACUMULADOR = '.';
	f = (f - (int) f) * 1000000;
	*ACUMULADOR = FLOAT;
	*ACUMULADOR = (int) f;
	*ACUMULADOR = 'E';
	*ACUMULADOR = '-';
	*ACUMULADOR = '6';
	*ACUMULADOR = ')';
}
```

As funções abaixo foram alteradas de acordo com a substituição de alpha por inv_alpha:

```
void copyConstants(const ModelConstants * source, ModelConstants * dest);

void computeConstants(ModelConstants * cts, unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2);
```

A função abaixo deixou de existir pois foi substituída pelo acelerador:

```
float distSquarePointLine(ModelConstants * cts, unsigned char x3, unsigned char y3);
```

Dois somatórios que usavam floats na função de regressão linear foram substituídos por inteiros sem prejuízo de precisão, para um possível ganho de desempenho. As outras variáveis floats não podem ser substituídas por inteiros sem prejuízo de desempenho. O restante da função está mantido como antes.

```
void linearRegression(RegressionResult * res, const unsigned char * data, const unsigned char * mask)
{
	TIME(FUN_LREG_START);

    int p;
    float temp;
    int numInliers = 0;
    float mediaX = 0, mediaY = 0, sumUp = 0, sumDown = 0;
	int totalX = 0, totalY = 0;

    //calcular as medias de x e de y
    TIME(LREG_MED_START);
    for(p = 0; p < DATA_SIZE_; p += 2)
    {
        if(mask[MASK(p)] == 1)
        {
            //mediaX += data[X(p)];
            //mediaY += data[Y(p)];
			totalX += data[X(p)];
			totalY += data[Y(p)];
            numInliers++;
        }
    }
    //mediaX /= numInliers;
    //mediaY /= numInliers;
	mediaX = (float) totalX / numInliers;
	mediaY = (float) totalY / numInliers;
	
	...
}
```

Todas as variáveis float na função abaixo foram substituídas por inteiros, sem prejuízo de precisão:

```
int distSquarePointPoint(unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2)
{
	TIME(FUN_DSPP_START);

    //float deltaX = (float) x2 - x1;
    //float deltaY = (float) y2 - y1;
	int deltaX = x2 - x1;
    int deltaY = y2 - y1;

    //float temp = deltaX * deltaX + deltaY * deltaY;
	int temp = deltaX * deltaX + deltaY * deltaY;
	
	TIME(FUN_DSPP_END);
	
    return temp;

}
```

##
### Código principal

O ponteiro abaixo foi adicionado para acessar os dados dos pontos 2 bytes de cada vez, de modo a fornecer x e y ao mesmo tempo para o acelerador.

```
uint16_t * x3y3_pointer = (uint16_t *) &data_points_[0];
```

Sendo o mais crítico, o passo 3 foi a principal alteração. Em seu início as constantes são passadas para o acelerador na forma de 4 escritas antes do loop começar. Então o ponteiro é utilizado a cada iteração para obter o valor de x e y do ponto e esse valor é escrito no acelerador. Em vez de usar a função removida para checar se é inlier, basta realizar uma leitura no acelerador. Ao fim do passo 3 a máquina de estados do acelerador é reiniciada para mantê-la pronta para novas iterações.

```
//Passo 3: Computar quantos pontos do conjunto se ajustam a reta de acordo com uma tolerancia (inliers)
TIME(STEP_3_START);

*INLIER_ESCRITA = model.deltaX;
*INLIER_ESCRITA = model.deltaY;
*INLIER_ESCRITA = model.beta;
*INLIER_ESCRITA = (model.inv_alpha)*DIST_TH_SQ;

inliers = 0;
x3y3_pointer = (uint16_t *) &data_points_[0];
for(p = 0; p < DATA_SIZE_; p += 2)
{
	TIME(INLIER_CHECK_START);
	*INLIER_ESCRITA = (uint32_t) (*x3y3_pointer);
	x3y3_pointer = (uint16_t *) &data_points_[p];
	if(*INLIER_LEITURA)
	{
		inliers++;
		inlier_mask_[MASK(p)] = 1;
	}
	else inlier_mask_[MASK(p)] = 0;
	TIME(INLIER_CHECK_END);
}

TIME(UPDATE_BEST_START);
if(inliers > bestInliers)
{
	bestInliers = inliers;
	copyConstants(&model, &bestModel);
}
TIME(UPDATE_BEST_END);

*INLIER_ESCRITA = RESET_INLIER;

TIME(STEP_3_END);
```

##
## Descrição do acelerador

O acelerador implementado é capaz de receber quatro constantes que representam a reta candidata e em seguida receber pontos, efetuar cálculos e informar se aquele ponto está de acordo ou não com a reta sob o limiar estabelecido. Ele é composto por um circuito de cálculo, uma máquina de estados e uma interface com o barramento Avalon.

### inlier_checker

![alt text](https://github.com/gsimoes00/engg57-ransac/blob/main/ransac_nios_hardware/images/inlier_checker.png?raw=true)

Este módulo executa a funcionalidade de cálculo do acelerador, ele é formado por multiplicadores, somadores e um comparador. Este módulo recebe dados que vem de registradores, opera sobre eles para calcular a distância do ponto até a reta atual e por fim compara esse valor com um limiar estabelecido previamente, se estiver de acordo o resultado é nivel lógico um, se não zero. Entre os módulos multiplicadores, somadores e comparador existem registradores que guardam valores parciais que vão se propagando para frente até atingir o resultado final.

### inlier_function

![alt text](https://github.com/gsimoes00/engg57-ransac/blob/main/ransac_nios_hardware/images/inlier_function.png?raw=true)

Este módulo implementa um conjunto de registradores que alimenta as entradas de inlier_checker e uma máquina de estados que controla tais registradores.

![alt text](https://github.com/gsimoes00/engg57-ransac/blob/main/ransac_nios_hardware/images/inlier_fsm.png?raw=true)

Esta máquina de estados finitos somente altera seu estado ao receber uma escrita via Avalon ou sinal de reset. 
* Inicialmente encontra-se no estado deltaX, caso receba uma escrita, a máquina utiliza o valor recebido para alimentar o registrador deltaX e se move para o estado deltaY. 
* O estado deltaY é analogo ao estágio deltaX, porém alimenta o registrador deltaY.
* O estado beta é análogo aos dois anteriores, porém alimenta o registrador beta.
* O estado threshold é análogo aos três anteriores, porém alimenta o registrador threshold.
* O estado x3y3 é o principal estado da máquina, as únicas formas de sair deste estado são receber um sinal de reset ou receber o valor 0xFFFFFFFF, que faz a máquina retornar para o início para o cálculo de uma nova reta. Neste estado qualquer escrita diferente desse valor de retorno é interpretada como contendo o valor de X e Y na porção [15:0] (15 downto 0), ou seja, seus 16 bits menos significativos, sendo o byte menos significativo o X e o outro o Y em vez da ordem usual. Este estado utiliza tais valores para alimentar os registradores x3 e y3.

A forma de utilizar este módulo consiste em fazer 4 escritas sobre ele contendo constantes apropriadas da reta e em seguida escrever o valor das coordenadas do ponto e ler o resultado, se o mesmo for um o ponto é inlier, se for zero é outlier.

### inlier_interface

![alt text](https://github.com/gsimoes00/engg57-ransac/blob/main/ransac_nios_hardware/images/inlier_interface.png?raw=true)

Este módulo apenas interliga o módulo inlier_function com o barramento Avalon seguindo o padrão necessário e com nomenclatura descritiva.

##
## Testbench

O testbench é extremamente similar ao usado na versão software, com apenas uma pequena mudança na porção que imprime floats, que foi alterada. 

[Ver testbench do ransac_nios_software.](https://github.com/gsimoes00/engg57-ransac/tree/main/ransac_nios_software#Testbench)

```
32'hfffffffe:
  begin
    @(posedge DUV.b2v_inst1.acumulador.write);
    $write("%g", DUV.b2v_inst1.acumulador.writedata);
    $fwrite(fd, "%g", DUV.b2v_inst1.acumulador.writedata);
  end
```

O formato de impressão dos números reais foi alterado para um formato f(sA.BE-6), onde s representa o sinal e pode ser "-" ou "" representando negativo e positivo respectivamente, A representa a porção inteira do número e B representa uma mantissa que deve ser multiplicada por 10^(-6), exemplos:

```
f(227.665954E-6) = 227.665964
```
```
f(-0.720425E-6) = -0.720425
```

##
### Saída típica de uma simulação:

```
########## INICIO DO TESTBENCH ##########
# 
# @DATA SEED       4096
# 
# @T         23 f 0
# @T        149 g 0
# @T        172 h 0
# @T        195 i 0
# @T      13497 e 0

...

# @T    2391536 q 1
# @T    2391559 d 1
# @T    2391656 n 1
# @T    2391679 g 1
# @T    2391709 f 1
# 
# @DATA OK 1
# @DATA ITERATIONS          4
# @DATA INLIERS        145
# @DATA EQUATION 1 f(227.665954E-6) f(-0.720425E-6)
# 
# 
########## FIM DO TESTBENCH ##########
# 
# ** Note: $stop    : D:/Projetos/Quartus/AcumuladorNios/SistemaEmbarcado/testbench/mentor/../../../AcumuladorNiosTB.v(67)
#    Time: 210179010 ns  Iteration: 8  Instance: /AcumuladorNiosTB
# Break in Module AcumuladorNiosTB at D:/Projetos/Quartus/AcumuladorNios/SistemaEmbarcado/testbench/mentor/../../../AcumuladorNiosTB.v line 67

```

##
### Acerca do tempo disponível para o acelerador

Através de medições, foi possível determinar o tempo de leituras e escritas no ambiente do trabalho. Uma escrita leva 23 ciclos e uma leitura leva 25 ciclos. Porém, no caso de uma leitura logo em seguida de uma escrita, o tempo entre o pulso de write e o pulso de read é de 16 ciclos. Portanto se for desejado operar o acelerador no máximo possível de sua capacidade, fornecendo um resultado a cada ciclo de leitura e escrita, é necessário que seu resultado esteja pronto em 16 ciclos. Nesse modo de uso ele fornecerá um resultado a cada 48 ciclos, que é o tempo de um ciclo de leitura e escrita em seguida.

No entando, existe uma otimização que consiste em receber 2 pontos de uma vez em vez de apenas 1, já que existe espaço nos 32 bits, porém isso exigiria uma maneira diferente de reiniciar a máquina no estado x3y3 e uma maneira de armazenar o primeiro resultado e depois calcular o segundo ou a duplicação do hardware em paralelo através da utilização de dois módulos inlier_checker. Essa modificação produziria um ganho de fator 2 nesse cálculo, fornecendo dois resultados a cada ciclo de 48 clocks, ou em média 24 clocks por resultado, que é da ordem do tempo de uma única leitura ou escrita.

No caso deste trabalho, existe uma atribuição entre a escrita no acelerador e sua leitura, nesse caso o circuito dispõe de mais tempo.

##
### [<< Voltar ao Índice](https://github.com/gsimoes00/engg57-ransac)
##