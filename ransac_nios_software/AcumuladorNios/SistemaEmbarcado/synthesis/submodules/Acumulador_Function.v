module Acumulador_Function (clock, reset_n, enable, data_in, data_out);

input clock, reset_n, enable;
input [31:0] data_in;
output reg [31:0] data_out;

always @(negedge clock)
begin
	if (!reset_n)
		data_out <= 0;
	else
		if (enable) data_out <= data_out + data_in;
end

endmodule
