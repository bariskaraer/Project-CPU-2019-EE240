module projectCPU(
  clk,
  rst,
  wrEn,
  data_fromRAM,
  addr_toRAM,
  data_toRAM,
  pCounter
);

input clk, rst;

input [15:0] data_fromRAM;
output [15:0] data_toRAM;
output wrEn;

// 12 can be made smaller so that it fits in the FPGA
output [12:0] addr_toRAM;
output [12:0] pCounter;

// Your design goes in here

endmodule
