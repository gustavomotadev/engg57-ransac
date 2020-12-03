module Acumulador_Interface (clock, reset_n, write, writedata, read, readdata, sum_export);

input clock, reset_n, write, read;
input [31:0] writedata;
output [31:0] readdata, sum_export;

wire [31:0] data;

Acumulador_Function inst (.clock(clock), .reset_n(reset_n), .enable(write), .data_in(writedata), .data_out(data));

assign readdata = data;
assign sum_export = data;

endmodule
