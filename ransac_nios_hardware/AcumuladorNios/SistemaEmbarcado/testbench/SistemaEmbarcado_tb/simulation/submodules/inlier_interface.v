module inlier_interface(clk, reset_n, write, writedata, read, readdata);

input wire clk, reset_n, write, read;
input signed [31:0] writedata;
output [31:0] readdata;

inlier_function inst_inlier_function(clk, reset_n, write, writedata, readdata);

endmodule