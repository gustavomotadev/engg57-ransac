`timescale 1ns/1ns

module Acumulador_TB;

reg clock, reset_n, write, read;
reg [31:0] writedata;
wire [31:0] readdata, sum_export;
integer i;

Acumulador_Interface DUV (clock, reset_n, write, writedata, read, readdata, sum_export);

always #10 clock = !clock;

initial
begin
	$monitor ($time, "reset_n = %b write = %b writedata = %d read = %b readdata = %d sum_export = %d", reset_n, write, writedata, read, readdata, sum_export);
	clock = 0;
	reset_n = 0;
	write = 0;
	read = 0;
	#100 reset_n = 1;
	for (i = 0; i < 10; i = i + 1)
	begin
		@ (posedge clock);
		writedata = i;
		write = 1;
		@ (posedge clock);
		write = 0;
	end
	#100 $stop;
end


endmodule
