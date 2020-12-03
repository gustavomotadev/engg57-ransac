module Clock_Counter (clk, reset_n, enable, command, clk_count);

input clk, reset_n, enable;
input [31:0] command; // command = 0 (reset) / command = 1 (start/resume) / command = 2 (pause)
output reg [31:0] clk_count;

reg flag;

always@(negedge clk)
begin
	if (!reset_n)
	begin
		clk_count <= 0;
		flag <= 0;
	end
	else
	begin
		if (flag) clk_count <= clk_count + 1;
		if (enable && (command == 0)) 
		begin
			clk_count <= 0;
			flag <= 0;
		end
		if (enable && (command == 1)) flag <= 1;
		if (enable && (command == 2)) flag <= 0;
	end
end

endmodule 