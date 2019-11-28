16-bit Instruction Word (IW) of ProjectCPU:

                                IW
               |----------------------------------
  bit position |15    13| 12                    0|
               |----------------------------------
    field name | opcode |           A            |
               |----------------------------------
     bit width |   3b   |          13b           |
               |----------------------------------
			   
(Every memory location and W are 16 bits)

Instruction Set of ProjectCPU:

ADD   -> unsigned Add
         opcode = 0
         W = *A + W
         write(readFromAddress(A) +W) to W
         *A = value (content of) address A = mem[A] (mem means memory)
         = means write (assign)

NAND  -> bitwise NAND
         opcode = 1
         W = ~((*A) & W)

SRL   -> Shift Right or Left
         opcode = 2
         W = ((*A) <= 16) ? (W >> (*A)) : (W << ((*A) - 16))

LT    -> Less Than
         opcode = 3
         W = W < (*A)

BZ    -> Branch on Zero
         opcode = 4
         PC = (W == 0) ? *A : (PC+1)
		 
CP2W  -> Copy to W
         opcode = 5
         W = *A

CPfW  -> Copy from W
         opcode = 6
         *A = W

MUL   -> unsigned Multiply
         opcode = 7
         W = lower16bit(W * (*A))
		 
INDIRECT ADRESSING

There are no special instructions for indirect addressing. Instead, every instruction
can operate in indirect addressing mode.

That is, if A==0, replace *A above with **4.

Every program starts like this:

0: CP2W 2
1: BZ 3
2: 0
3: 5
4: // indirection register
5: // program actually starts here