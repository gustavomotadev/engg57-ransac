#define END_BASE_MEMO (int *) 0x0000
#define ACUMULADOR (int *) 0x5018
#define MEDIDOR_LEITURA (int *) 0x5014
#define MEDIDOR_ESCRITA (int *) 0x5010

int main()
{
	int i;
	contador = 0;
	int * ponteiro = END_BASE_MEMO;
	
	while(1)
	{
		*MEDIDOR_ESCRITA = 0;
		*MEDIDOR_ESCRITA = 1;
		for (i = 0; i < 16384; i++)
		{
		  *ACUMULADOR = ponteiro[i];
		}
		*MEDIDOR_ESCRITA = 2;

		return 0;
	}
}
