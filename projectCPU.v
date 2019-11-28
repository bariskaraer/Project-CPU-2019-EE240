`timescale 1ns / 1ps
module projectCPU(clk, rst, data_fromRAM, wrEn, addr_toRAM, data_toRAM, pCounter);
 
parameter SIZE = 13;

input clk;
input rst;
input wire [15:0] data_fromRAM;
output reg wrEn;
output reg [SIZE-1:0] addr_toRAM;
output reg [15:0] data_toRAM;
output reg [SIZE-1:0] pCounter;


reg [15:0] star4;
reg [15:0] star4Next;
// Node <star4_13> of sequential type is unconnected in block <SimpleCPU>. 
// We can try changing the bits of star4 and star4Next to 12:0 this will solve the synthesize warning.
// reg [12:0] star4;
// reg [12:0] star4Next;

reg [15:0] starstar4;
reg [15:0] starstar4Next;





reg [2:0] opCode;
reg [2:0] opCodeNxt;

reg [12:0] operand;
reg [12:0] operandNext; // A
reg [SIZE-1:0] pCounterNext;

reg [2:0] state;
reg [2:0] stateNext;
reg [15:0] starA;
reg [15:0] starANxt;

always @(posedge clk)begin
   star4    <= #1 star4Next;
	starstar4    <= #1 starstar4Next;
	state    <= #1 stateNext;
	pCounter <= #1 pCounterNext;
	opCode   <= #1 opCodeNxt;
	operand  <= #1 operandNext;
	starA  <= #1 starANxt;
end

always @*begin
   starstar4Next= starstar4;
	star4Next= star4;
   starANxt=starA;
	stateNext    = state;
	pCounterNext = pCounter;
	opCodeNxt   = opCode;
	operandNext  = operand;
	addr_toRAM   = 0;
	wrEn         = 0;
	data_toRAM   = 0;
if(rst)
	begin
	star4Next=0;
	starstar4Next=0;
	starANxt=0;
	stateNext    = 0;
	pCounterNext = 0;
	opCodeNxt   = 0;
	operandNext  = 0;
	addr_toRAM   = 0;
	wrEn         = 0;
	data_toRAM   = 0;
	end
else 
	case(state)                       
		0: begin	// take instruction
			pCounterNext = pCounter;
			opCodeNxt   = opCode;
			operandNext  = 0;
			addr_toRAM   = pCounter;
			wrEn         = 0;
			data_toRAM   = 0;
			stateNext    = 1;
         star4Next=0;
         starstar4Next=0;
		end 
		1:begin // We take *A here
			pCounterNext = pCounter;
			opCodeNxt   = {data_fromRAM[15:13]}; // Opcode of the instruction
			operandNext  = data_fromRAM[12:0];    // A
			addr_toRAM   = data_fromRAM[12:0];    // get *A in next state	
			
			if (operandNext == 0) begin 
				// 4 indir reg addrr
				addr_toRAM   = 4;    // get *A in next state	
				stateNext = 4;
			end else begin
				stateNext=2;
			end
		end
		2: begin		// All instructions are here1\☺
			// data from ram = starA
			if (operandNext == 0) begin 
				starANxt = starstar4Next;
				operandNext = star4Next;
			end else begin
				starANxt=data_fromRAM;
			end
			
			addr_toRAM = 500; // get starW
			
			stateNext = 3;
		end
		3: begin  // get starW
			// data from ram = starW
			
			
			addr_toRAM = 500;
			pCounterNext=pCounter + 1;
			wrEn = 1;
			
			if(opCodeNxt == 3'b000)	// AD
				data_toRAM = starA + data_fromRAM;
			else if(opCodeNxt == 3'b001)	// NAND
				data_toRAM = ~(starA & data_fromRAM);
			else if(opCodeNxt == 3'b010)	// SRL
				data_toRAM = (starA <= 16) ? (data_fromRAM >> starA) : (data_fromRAM << (starA - 16));
			else if(opCodeNxt == 3'b011)	// LT
				data_toRAM = (data_fromRAM< starA) ? 1 : 0;
			else if(opCodeNxt == 3'b100) begin	// BZ 
				pCounterNext = (data_fromRAM == 0) ? starA : (pCounter + 1);
				wrEn = 0;
				end 
			else if(opCodeNxt == 3'b101)	// CP2W
				data_toRAM = starA;
			else if(opCodeNxt == 6)begin	// CPfW
			   addr_toRAM = operand;
				data_toRAM = data_fromRAM;
				end
			else if(opCodeNxt == 3'b111)	// MUL
				data_toRAM = starA * data_fromRAM;
				
			stateNext = 0;
		end
		4: begin
			// get star4
			star4Next = data_fromRAM;
			
			addr_toRAM = star4Next;
			stateNext = 5;
		end
		5: begin
			starstar4Next = data_fromRAM;
			
			stateNext = 2;
		end
	endcase

end

endmodule
