`timescale 10ns/10ns

module AcumuladorNiosTB;

reg	CLOCK_50;
reg	[3:3] KEY;
reg	[1:0] SW;
wire	[15:0] LEDR;

AcumuladorNios DUV (CLOCK_50, KEY, SW, LEDR);

real temp;

integer fd;

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

/*
initial 
	begin
		forever
			begin
				wait (DUV.b2v_inst1.acumulador.writedata == 32'hffffffff);
				@(posedge CLOCK_50);
				$display("STOP");
				$stop;
				wait (DUV.b2v_inst1.acumulador.writedata != 32'hffffffff);
			end
	end
*/
	
initial 
	begin
	
		fd = $fopen("tb_result_file.txt", "w");
		
		if (!fd)
			begin
				$display("Erro na abertura de arquivo!");
				$stop();
			end
			
		forever
			begin
			
				@(posedge DUV.b2v_inst1.acumulador.write);
	
				case (DUV.b2v_inst1.acumulador.writedata)
				
					32'hffffffff: 
						begin
							$display("\n########## FIM DO TESTBENCH ##########\n");
							$fclose(fd);
							$stop;
						end
					32'hfffffffe:
						begin
							@(posedge DUV.b2v_inst1.acumulador.write);
							temp = DUV.b2v_inst1.acumulador.writedata;
							temp = temp / 100000;
							$write("%f", temp);
							$fwrite(fd, "%f", temp);
						end
					32'hfffffffd:
						begin
							@(posedge DUV.b2v_inst1.acumulador.write);
							$write("%d", DUV.b2v_inst1.acumulador.writedata);
							$fwrite(fd, "%d", DUV.b2v_inst1.acumulador.writedata);
						end
					32'hfffffffc:
						begin
							$write("%d", DUV.b2v_inst1.medidordesempenho.CC.clk_count);
							$fwrite(fd, "%d", DUV.b2v_inst1.medidordesempenho.CC.clk_count);
						end
					default: 
						begin
							$write("%c", DUV.b2v_inst1.acumulador.writedata[7:0]);
							$fwrite(fd, "%c", DUV.b2v_inst1.acumulador.writedata[7:0]);
						end
					
				endcase
				
				/*
				if (DUV.b2v_inst1.acumulador.writedata == 32'hffffffff)
					begin
						$stop;
					end
				else
					begin
						$write("%c", DUV.b2v_inst1.acumulador.writedata[7:0]);
					end
				*/
				
			end
	
	end


endmodule
