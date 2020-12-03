	component SistemaEmbarcado is
		port (
			acumulador_conduit_readdata        : out std_logic_vector(31 downto 0);        -- readdata
			clk_clk                            : in  std_logic                     := 'X'; -- clk
			medidordesempenho_conduit_readdata : out std_logic_vector(31 downto 0);        -- readdata
			reset_reset_n                      : in  std_logic                     := 'X'  -- reset_n
		);
	end component SistemaEmbarcado;

	u0 : component SistemaEmbarcado
		port map (
			acumulador_conduit_readdata        => CONNECTED_TO_acumulador_conduit_readdata,        --        acumulador_conduit.readdata
			clk_clk                            => CONNECTED_TO_clk_clk,                            --                       clk.clk
			medidordesempenho_conduit_readdata => CONNECTED_TO_medidordesempenho_conduit_readdata, -- medidordesempenho_conduit.readdata
			reset_reset_n                      => CONNECTED_TO_reset_reset_n                       --                     reset.reset_n
		);

