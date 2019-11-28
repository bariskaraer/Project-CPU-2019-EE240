`timescale 1ns / 1ps

// This tb accompanies projectCPU_test.asm. Since that program is obtained by porting
// a VSCPU asm program to projectCPU, the memCheck functions below are based on
// VSCPU instructions.

// YOU SHOULD SUCCESSFULLY PASS:
// SIMULATION AND SYNTHESIS

module projectCPU_tb;

reg clk;
initial begin
  clk = 1;
  forever
	  #5 clk = ~clk;
end

integer ff;
reg rst;
initial begin
  ff = $fopen("outputLog.txt", "w");
  // $dumpvars;
  rst = 1;
  repeat (10) @(posedge clk);
  rst <= #1 0;
  repeat (10000) @(posedge clk);
  $fwrite(ff, "Simulation finished due to Time Limit.\nTest Count = %d\nTotal Errors = %d\n", testCount, errorCount);
  $display("Simulation finished due to Time Limit.\nTest Count = %d\nTotal Errors = %d\n", testCount, errorCount);
  $fclose(ff);
  $finish;
end

wire [12:0] addr_toRAM;
wire [15:0] data_toRAM, data_fromRAM;
wire [12:0] pCounter;

projectCPU projectCPU(
  .clk(clk),
  .rst(rst),
  .wrEn(wrEn),
  .data_fromRAM(data_fromRAM),
  .addr_toRAM(addr_toRAM),
  .data_toRAM(data_toRAM),
  .pCounter(pCounter) // PC = ProgramCounter
);

blram blram(
  .clk(clk),
  .rst(rst),
  .i_we(wrEn),
  .i_addr(addr_toRAM),
  .i_ram_data_in(data_toRAM),
  .o_ram_data_out(data_fromRAM)
);

reg [8:0] testCount = 0;
reg [8:0] errorCount = 0;

always @(pCounter) begin
	
	case(testCount -1)
		6: memCheck(201, 2, "CP");
		12: memCheck(203, 5, "CPi");
		15: memCheck(204, 8, "SRL");
		18: memCheck(206, 40, "SRL");
		25: memCheck(208, 1, "SRLi");
		32: memCheck(209, 144, "SRLi");
		35: memCheck(210, 16'hFFFF, "NAND");
		38: memCheck(210, 0, "NAND");
		41: memCheck(212, 16'hFFFD, "NAND");
		44: memCheck(212, 2, "NAND");
		51: memCheck(214, 16'hFFFF, "NANDi");
		54: memCheck(214, 0, "NAND");
		61: memCheck(215, 16'hFFFD, "NANDi");
		64: memCheck(215, 2, "NAND");
		67: memCheck(216, 1, "LT");
		70: memCheck(217, 0, "LT");
		73: memCheck(218, 0, "LT");
		80: memCheck(220, 1, "LTi");
		87: memCheck(221, 0, "LTi");
		94: memCheck(222, 0, "LTi");
		97: memCheck(223, 0, "ADD");
		104: memCheck(224, 0, "ADDi");
		107: memCheck(225, 63, "MUL");
		114: memCheck(227, 27, "MULi");
		116: pCounterCheck(123, "BZJ");
		122: memCheck(230, 2, "CPi");
		124: pCounterCheck(125, "BZJ");
		130: memCheck(233, 3, "CPi");
		139: pCounterCheck(146, "BZJi");
		145: memCheck(235, 2, "CPi");
		149: memCheck(236, 5, " CPI");
		153: memCheck(240, 5, "CPIi"); 
		158: memCheck(244, 7, "ADDi");
		163: memCheck(246, 16'hFFFF, "NANDi");
		168: memCheck(246, 0, "NANDi");
		173: memCheck(249, 8, "SRLi");
		178: memCheck(252, 40, "SRLi");
		182: pCounterCheck(189, "BZJi");
		188: memCheck(264, 2, "CPi");
		192: pCounterCheck(193, "BZJi");
		198: memCheck(268, 3, "CPi");
		304: memCheck(255, 0, "LTi");
		309: memCheck(257, 0, "LTi");
		314: memCheck(259, 1, "LTi");
		319: begin
			memCheck(270, 63, "MULi"); 
			$fwrite(ff, "Total Errors = %d", errorCount);
			$fclose(ff); 
			$finish;
		end
	endcase
	
	testCount = pCounter +1;
	
end

task memCheck;
    input [12:0] memLocation;
	input [15:0] expectedValue;
	input [47:0] instMnemonic; 
    begin
      if(blram.memory[memLocation] !== expectedValue) begin
			$fwrite(
				ff,"Error Found at testCount %d, Instruction %s, %d ns, RAM Addr %d: expected %d, received %d\n",
				testCount -1, instMnemonic, $time, memLocation, expectedValue, blram.memory[memLocation]
			);
			errorCount = errorCount +1;
		end
    end
endtask

task pCounterCheck;
    input [31:0] pCounterExpected;
	input [47:0] instMnemonic; 
    begin
		if(pCounter !== pCounterExpected) begin
			$fwrite(
				ff,"Error Found at testCount %d, Instruction %s, %d ns: expected PC=%d, observed PC=%d\n",
				testCount -1, instMnemonic, $time, pCounterExpected, pCounter
			);
			errorCount = errorCount +1;
		end
    end
endtask

endmodule
