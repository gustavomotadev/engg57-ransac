
module SistemaEmbarcado (
	acumulador_conduit_readdata,
	clk_clk,
	medidordesempenho_conduit_readdata,
	reset_reset_n);	

	output	[31:0]	acumulador_conduit_readdata;
	input		clk_clk;
	output	[31:0]	medidordesempenho_conduit_readdata;
	input		reset_reset_n;
endmodule
