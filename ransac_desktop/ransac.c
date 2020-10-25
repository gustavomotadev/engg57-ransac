#define CROSS

#ifdef LINE
#include "line_points_x4.h"
#endif
#ifdef CROSS
#include "cross_points_x4.h"
#endif
#ifdef TRIANGLE
#include "triangle_points_x4.h"
#endif
#ifdef ARROW
#include "arrow_points_x4.h"
#endif
#ifdef SQUARE
#include "square_points_x4.h"
#endif

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

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

void copyConstants(const ModelConstants * source, ModelConstants * dest)
{
    //copia estrutura para outra para evitar incluir mais bibliotecas

    dest->deltaX = source->deltaX;
    dest->deltaY = source->deltaY;
    dest->alpha = source->alpha;
    dest->beta = source->beta;
}

void computeConstants(ModelConstants * cts, unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2)
{
    //computa as constantes do modelo (reta), com base em 2 pontos

    cts->deltaX = x2 - x1;
    cts->deltaY = y2 - y1;
    cts->alpha = 1.0/((cts->deltaX*cts->deltaX) + (cts->deltaY*cts->deltaY));
    cts->beta = x2*y1 - y2*x1;
}

float distSquarePointLine(ModelConstants * cts, unsigned char x3, unsigned char y3)
{
    //computa a proximidade de um terceiro ponto em relacao a reta calculada previamente
    //https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line

    float temp = cts->deltaY*x3 - cts->deltaX*y3 + cts->beta;
    return cts->alpha * temp * temp;
}

void linearRegression(RegressionResult * res, const unsigned char * data, const unsigned char * mask)
{
    //calcular regressao linear simples pelo metodo de minimos quadrados
    //essa funcao so leva em conta os pontos marcados na mascara
    //https://en.wikipedia.org/wiki/Simple_linear_regression

    int p;
    float temp;
    int numInliers = 0;
    float mediaX = 0, mediaY = 0, sumUp = 0, sumDown = 0;

    //calcular as medias de x e de y
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

    //calculo dos parametros a e b
    res->b = sumUp/sumDown;

    res->a = mediaY - res->b*mediaX;
}

float distSquarePointPoint(unsigned char x1, unsigned char y1, unsigned char x2, unsigned char y2)
{
    float deltaX = (float) x2 - x1;
    float deltaY = (float) y2 - y1;
    return deltaX * deltaX + deltaY * deltaY;
}

void main(void)
{
    int i, j, p, point1, point2, bestP1, bestP2, inliers;
    ModelConstants model, bestModel;
    RegressionResult result;
    float currentDist, bestDist;
    int bestInliers = 0;
    //booleano
    unsigned char modelFound = 0;

    srand(time(NULL));
    
    //encontrar uma reta
    for(i = 0; i < MAX_IT; i++)
    {
        //Passo 1: Selecionar aleatoriamente 2 pontos (COM HEURISTICA)
        //HEURISTICA: Tentar ate MAX_RANDOM_TRIES vezes obter distancia minima MIN_SAMPLE_DIST
        point1 = (rand()%NUM_POINTS_)*2;
        point2 = (rand()%NUM_POINTS_)*2;
        bestP1 = point1;
        bestP2 = point2;
        currentDist = distSquarePointPoint(data_points_[X(point1)], data_points_[Y(point1)], data_points_[X(point2)], data_points_[Y(point2)]);
        bestDist = currentDist;
        if(currentDist < MIN_SAMPLE_DIST)
        {
            for(j = 0; j < MAX_RANDOM_TRIES-1; j++)
            {
                point1 = (rand()%NUM_POINTS_)*2;
                point2 = (rand()%NUM_POINTS_)*2;
                currentDist = distSquarePointPoint(data_points_[X(point1)], data_points_[Y(point1)], data_points_[X(point2)], data_points_[Y(point2)]);
                if(currentDist > bestDist)
                {
                    bestDist = currentDist;
                    bestP1 = point1;
                    bestP2 = point2;
                }
                if(currentDist >= MIN_SAMPLE_DIST) break;
            }
        }

        //Passo 2: Encontrar os parâmetros do modelo (reta)
        computeConstants(&model, data_points_[X(bestP1)], data_points_[Y(bestP1)], data_points_[X(bestP2)], data_points_[Y(bestP2)]);

        //Passo 3: Computar quantos pontos do conjunto se ajustam a reta de acordo com uma tolerancia (inliers)
        inliers = 0;
        for(p = 0; p < DATA_SIZE_; p += 2)
        {
            if(distSquarePointLine(&model, data_points_[X(p)], data_points_[Y(p)]) <= DIST_TH_SQ)
            {
                inliers++;
                inlier_mask_[MASK(p)] = 1;
            }
            else inlier_mask_[MASK(p)] = 0;
        }

        if(inliers > bestInliers)
        {
            bestInliers = inliers;
            copyConstants(&model, &bestModel);
        }

        //Passo 4: Se o numero de inliers for satisfatorio de acordo com uma tolerancia,
        //reestimar o modelo utilizando os inliers identificados e terminar o loop
        if(inliers >= INLIER_TH)
        {
            linearRegression(&result, data_points_, inlier_mask_);
            modelFound = 1;
            break;
        }

        //Passo 5: Se nao cumpriu os requisitos do passo 4, repetir o loop
    }

    //uma reta encontrada (ou nao)
    //codigo exclusivo para a plataforma PC Desktop
    if(modelFound == 0) printf("NOT OK!\nIteracoes: %i\nInliers: %i\n", i+1, bestInliers);
    else
    {
        printf("OK!\nIteracoes: %i\nInliers: %i\nEquacao: Y = %f + %fX\n", i+1, bestInliers, result.a, result.b);

        //imprimir dados na saida padrao para serem usados pela entrada padrao de script python para visualizar
        printf("@DATA_START\n");
        printf("@DATA_POINTS\n");
        for(p = 0; p < DATA_SIZE_; p += 2) printf("%i,%i,", data_points_[X(p)], data_points_[Y(p)]);
        printf("\n");
        printf("@INLIER_MASK\n");
        for(p = 0; p < NUM_POINTS_; p++) printf("%i,", inlier_mask_[p]);
        printf("\n");
        printf("@EQUATIONS\n");
        printf("%i, %f, %f\n", 1, result.a, result.b);
        printf("@DATA_END\n");
    }
}