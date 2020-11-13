#include "header.h"

#include <stdlib.h>
#include <stdio.h>

//definicoes especificas do sistema embarcado
#define END_BASE_MEMO (int *) 0x0000
#define ACUMULADOR (int *) 0x5018
#define MEDIDOR_LEITURA (int *) 0x5014
#define MEDIDOR_ESCRITA (int *) 0x5010
#define SEED 4096
#define STOP 0xffffffff

//imprimir valores ou nao
#define DEBUG_PRINT
#ifdef DEBUG_PRINT
#define FLOAT 0xfffffffe
#define INT 0xfffffffd
#define TIME_F 0xfffffffc
#define TIME(s); {*MEDIDOR_ESCRITA = 2; pause_print_time(s); *MEDIDOR_ESCRITA = 1;}
#else
#define TIME(s);
#endif

//stamps dos tempos
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

//distancia maxima tolerada pra ser inlier
#define DIST_TH 10
#define DIST_TH_SQ (DIST_TH*DIST_TH)

//numero maximo de iteracoes sorteando pares de pontos
#define MAX_IT 25

//numero de inliers a partir do qual o algoritmo aceita e para as iteracoes
#define INLIER_TH ((int) NUM_POINTS_*0.25)

//HEURISTICA: distancia minima entre os pontos inicialmente sorteados
#define MIN_SAMPLE_DIST 90
#define MIN_SAMPLE_DIST_SQ (MIN_SAMPLE_DIST*MIN_SAMPLE_DIST)

//HEURISTICA: maximo de tentativas para atingir MIN_SAMPLE_DIST
#define MAX_RANDOM_TRIES 25

//macros para pegar em data_points_ o valor de X e Y e o indice na mascara
#define X(p) (p)
#define Y(p) (p+1)
#define MASK(p) (p>>1)

typedef struct ModelConstants
{
    //constantes do modelo (reta)

    float deltaX, deltaY, alpha, beta;

} ModelConstants;

typedef struct RegressionResult
{
    //resultado da regressao linear por minimos quadrados Y = A + B.X

    float a, b;
} RegressionResult;

#ifdef DEBUG_PRINT
void print_str(char * str)
{
	int i;
	for(i = 0; str[i] != 0; i++)
	{
		*ACUMULADOR = str[i];
	}
}

void print_int(int i)
{
	*ACUMULADOR = INT;
	*ACUMULADOR = i;
}

void print_float(float f)
{
	*ACUMULADOR = FLOAT;
	*ACUMULADOR = (int) (f*100000);
}

void pause_print_time(char * stamp)
{
	//*MEDIDOR_ESCRITA = 2;
	print_str("@T ");
	//leitura do medidor le sempre a mesma coisa por algum motivo
	//print_int(*MEDIDOR_ESCRITA);
	*ACUMULADOR = TIME_F;
	print_str(" ");
	print_str(stamp);
	print_str("\n");
	//*MEDIDOR_ESCRITA = 1;
}
#endif

void stop_simulation(void)
{
	*ACUMULADOR = STOP;
}

void copyConstants(const ModelConstants * source, ModelConstants * dest)
{
	TIME(FUN_COPY_START);

	//copia estrutura para outra para evitar incluir mais bibliotecas
    dest->deltaX = source->deltaX;
    dest->deltaY = source->deltaY;
    dest->alpha = source->alpha;
    dest->beta = source->beta;

    TIME(FUN_COPY_END);
}

void computeConstants(ModelConstants * cts, unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2)
{
	TIME(FUN_COMP_START);

    //computa as constantes do modelo (reta), com base em 2 pontos
    cts->deltaX = x2 - x1;
    cts->deltaY = y2 - y1;
    cts->alpha = 1.0/((cts->deltaX*cts->deltaX) + (cts->deltaY*cts->deltaY));
    cts->beta = x2*y1 - y2*x1;

    TIME(FUN_COMP_END);
}

float distSquarePointLine(ModelConstants * cts, unsigned char x3, unsigned char y3)
{
	TIME(FUN_DSPL_START);

    //computa a proximidade de um terceiro ponto em relacao a reta calculada previamente
    //https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line

    float temp = cts->deltaY*x3 - cts->deltaX*y3 + cts->beta;

    float temp2 = cts->alpha * temp * temp;
	
	TIME(FUN_DSPL_END);
	
    return temp2;
}

void linearRegression(RegressionResult * res, const unsigned char * data, const unsigned char * mask)
{
	TIME(FUN_LREG_START);

    //calcular regressao linear simples pelo metodo de minimos quadrados
    //essa funcao so leva em conta os pontos marcados na mascara
    //https://en.wikipedia.org/wiki/Simple_linear_regression

    int p;
    float temp;
    int numInliers = 0;
    float mediaX = 0, mediaY = 0, sumUp = 0, sumDown = 0;

    //calcular as medias de x e de y
    TIME(LREG_MED_START);
    for(p = 0; p < DATA_SIZE_; p += 2)
    {
        if(mask[MASK(p)] == 1)
        {
            mediaX += data[X(p)];
            mediaY += data[Y(p)];
            numInliers++;
        }
    }
    mediaX /= numInliers;
    mediaY /= numInliers;
    TIME(LREG_MED_END);

    TIME(LREG_SUM_START);
    //calcular dois somatorios da formula de regressao linear
    for(p = 0; p < DATA_SIZE_; p += 2)
    {
        if(mask[MASK(p)] == 1)
        {
            temp = data[X(p)] - mediaX;

            sumUp += temp * (data[Y(p)] - mediaY);
            sumDown += temp * temp;
        }
    }
    TIME(LREG_SUM_END);

    TIME(LREG_RES_START);
    //calculo dos parametros a e b
    res->b = sumUp/sumDown;

    res->a = mediaY - res->b*mediaX;
    TIME(LREG_RES_END);

    TIME(FUN_LREG_END);
}

float distSquarePointPoint(unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2)
{
	TIME(FUN_DSPP_START);

    float deltaX = (float) x2 - x1;
    float deltaY = (float) y2 - y1;

    float temp = deltaX * deltaX + deltaY * deltaY;
	
	TIME(FUN_DSPP_END);
	
    return temp;

}

int main(void)
{
    int i, j, p, point1, point2, bestP1, bestP2, inliers;
    ModelConstants model, bestModel;
    RegressionResult result;
    float currentDist, bestDist;
    int bestInliers = 0;
    //booleano
    unsigned char modelFound = 0;

    //teste
    /*
    #ifdef DEBUG_PRINT
    print_str("TESTE COM STRING\n");
    print_str("INT = ");
    print_int(25);
    print_str("\nFLOAT = ");
    print_float(25.555);
    print_str("\n");
    #endif
    */

	#ifdef DEBUG_PRINT
    //imprimir semente e semear o aleatorio
    print_str("@DATA SEED ");
    print_int(SEED);
    print_str("\n\n");
	#endif

    //resetar e iniciar contador
    *MEDIDOR_ESCRITA = 0;
    *MEDIDOR_ESCRITA = 1;
    TIME(ALG_START);

    srand(SEED);

    //encontrar uma reta
    for(i = 0; i < MAX_IT; i++)
    {
    	TIME(ITER_START);

        //Passo 1: Selecionar aleatoriamente 2 pontos (COM HEURISTICA)
        //HEURISTICA: Tentar ate MAX_RANDOM_TRIES vezes obter distancia minima MIN_SAMPLE_DIST
    	TIME(STEP_1_START);
    	TIME(SELECT_2P_START);
        point1 = (rand()%NUM_POINTS_)*2;
        point2 = (rand()%NUM_POINTS_)*2;
        bestP1 = point1;
        bestP2 = point2;
        currentDist = distSquarePointPoint(data_points_[X(point1)], data_points_[Y(point1)], data_points_[X(point2)], data_points_[Y(point2)]);
        bestDist = currentDist;
        TIME(SELECT_2P_END);
        if(currentDist < MIN_SAMPLE_DIST)
        {
            for(j = 0; j < MAX_RANDOM_TRIES-1; j++)
            {
            	TIME(SELECT_2P_START);
                point1 = (rand()%NUM_POINTS_)*2;
                point2 = (rand()%NUM_POINTS_)*2;
                currentDist = distSquarePointPoint(data_points_[X(point1)], data_points_[Y(point1)], data_points_[X(point2)], data_points_[Y(point2)]);
                if(currentDist > bestDist)
                {
                    bestDist = currentDist;
                    bestP1 = point1;
                    bestP2 = point2;
                }
                TIME(SELECT_2P_END);
                if(currentDist >= MIN_SAMPLE_DIST) break;
            }
        }

        TIME(STEP_1_END);
        //Passo 2: Encontrar os parâmetros do modelo (reta)
        TIME(STEP_2_START);
        computeConstants(&model, data_points_[X(bestP1)], data_points_[Y(bestP1)], data_points_[X(bestP2)], data_points_[Y(bestP2)]);
        TIME(STEP_2_END);

        //Passo 3: Computar quantos pontos do conjunto se ajustam a reta de acordo com uma tolerancia (inliers)
        TIME(STEP_3_START);
        inliers = 0;
        for(p = 0; p < DATA_SIZE_; p += 2)
        {
        	TIME(INLIER_CHECK_START);
            if(distSquarePointLine(&model, data_points_[X(p)], data_points_[Y(p)]) <= DIST_TH_SQ)
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

        TIME(STEP_3_END);
        //Passo 4: Se o numero de inliers for satisfatorio de acordo com uma tolerancia,
        //reestimar o modelo utilizando os inliers identificados e terminar o loop
        TIME(STEP_4_START);
        if(inliers >= INLIER_TH)
        {
            linearRegression(&result, data_points_, inlier_mask_);
            modelFound = 1;
            TIME(STEP_4_END);
			TIME(ITER_END);
            break;
        }
        TIME(STEP_4_END);

        //Passo 5: Se nao cumpriu os requisitos do passo 4, repetir o loop
        TIME(ITER_END);
    }

    TIME(ALG_END);

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

    //parar simulacao
    stop_simulation();

    //ficar travado no final
    while(1);
}
