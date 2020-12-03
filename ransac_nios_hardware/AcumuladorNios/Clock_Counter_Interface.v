module Clock_Counter_Interface (clk, reset_n, write, writedata, read, readdata, clk_count);

input clk, reset_n, write, read;
input [31:0] writedata;
output [31:0] clk_count, readdata;

wire [31:0] data;

Clock_Counter CC (.clk(clk), .reset_n(reset_n), .enable(write), .command(writedata), .clk_count(data));

assign readdata = data;
assign clk_count = data;

endmodule 