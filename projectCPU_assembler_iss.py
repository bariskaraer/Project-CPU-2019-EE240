#!/usr/bin/python

# CAUTION: run 'dos2unix assembler.py' if you get bad interpreter error 

# notes:
# 1. Supported instructions:
#
#    ISA v1:
#    ============================================================================================
#    Arithmetic & Logic Instructions  | Data Transfer Instructions | Program Control Instructions
#    ============================================================================================
#                    ADD              |             CP2W           |            BZ
#                    NAND             |             CPfW           |         
#                    SRL              |                            |
#                    LT               |                            |
#                    MUL              |                            |
# 2. -x only generates .coe, .mif, and .v files (other memory initialization files will be supported later)
# 3. Default MEM_SIZE is 65536. That is, 65536x16-bit.

import re
import sys, getopt
import linecache
import struct
import platform

def print_blank_line(line_count):
    for i in range(line_count):
        print ""

def print_header(char, count):
    print ""
    for i in range(count):
        print char,
    print ""

def print_footer(char, count):
    for i in range(count):
        print char,
    print ""
        
def print_usage(option=1):
    if option == 0:
        print_blank_line(1)
        print "Invalid syntax. Please run the script as follows:"
    print_blank_line(1)
    print "SYNOPSIS"
    print_blank_line(1)
    print 'assembler_iss_mem_init_gen.py -h -i <input_file> -a <isa_version> -s <sim_type> -m <mem_size> -x -v'
    print_blank_line(2)
    print "DESCRIPTION"
    print_blank_line(1)
    print "assembler_iss_mem_init_gen.py\n\tname of this script"
    print_blank_line(1)
    print "-h"
    print "\tdisplay this help"
    print_blank_line(1)
    print "-i, --ifile <input_file>"
    print"\tset assembly code that must be processed"
    print_blank_line(1)
    print "-a, --arch <isa_version>"
    print "\tset architecture\n\t1 - select isa v1\n\t2 - select isa v2"
    print_blank_line(1)
    print "-s <sim_type>\n\tsimulate code\n\t0 - simulate all\n\t1 - simulate step-by-step"
    print_blank_line(1)
    print "-m, --mem_size <mem_size>"
    print "\tset memory size"
    print_blank_line(1)
    print "-x\n\textract memory initialization files"
    print_blank_line(1)
    print "-v\n\tverbose"

# used a small trick posted on stackoverflow to find out if a string should be float or integer (see https://stackoverflow.com/questions/15357422)
def is_float(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def is_int(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

class CPUSim:

    def __init__(self, inputfile="", architecture=1, mem_size=65536, sim_type=0, verbose=False):
        self.inputfile = inputfile
        self.architecture = architecture
        self.indirection_register_index = 4
        self.wreg = 0
        if mem_size != 0:
            self.MEM_SIZE = mem_size
        else:
            self.MEM_SIZE = 65536
        self.sim_type = sim_type
        self.verbose = verbose
        
        if self.verbose:
            print "Class instance is created with following parameters:"
            print self.inputfile
            print self.architecture
            print self.MEM_SIZE
            print self.sim_type
            print self.verbose

        # memory arrays
        self.mem_array_sim = [0] * self.MEM_SIZE
        self.mem_array_coe = ["0"] * self.MEM_SIZE
        self.mem_array_mif = ["0000000000000000"] * self.MEM_SIZE
        self.mem_array_init = ["garbage"] * self.MEM_SIZE # mark unused memory locations as "garbage"

        # file names
        self.outputfile_coe = "instr_data_memory.coe"
        self.outputfile_mif = "instr_data_memory.mif"
        self.outputfile_init = "instr_data_memory.v"
        self.outputfile_final = "instr_data_memory_final.asm"

        self.program_counter = 0
        self.program_counter_prev = 0
    
        # opcode dictionaries
        self.opcodes_v1 = {"ADD" : 0, "NAND" : 1, "SRL" : 2, "LT" : 3, "BZ" : 4, "CP2W" : 5, "CPfW" : 6, "MUL" : 7}

        self.opcodes_v1_r = {0 : "ADD", 1 : "NAND", 2 : "SRL", 3 : "LT", 4 : "BZ", 5 : "CP2W", 6 : "CPfW",
7 : "MUL"}

    def print_error(self, linenum, *operand_index):
        print_header("!", 25)
        print "Error at line", (linenum + 1), ":",
        if len(operand_index) == 2:
            print "operand", operand_index[0], "and operand", operand_index[1], "must be nonnegative integers"
        else:
            print "operand", operand_index[0], "must be nonnegative integer"
        
        line = linecache.getline(self.inputfile, (linenum + 1)).rstrip()
        print line
        print_footer("!", 25)
        sys.exit(1)
    
    def is_instruction_or_data(self, instruction_or_data):
        if self.architecture == 1:
            if instruction_or_data in self.opcodes_v1:
                return 1
            else:
                return 0
        elif self.architecture == 2:
            print "UNDEFINED ARCHITECTURE"
            sys.exit(1)
        else:
            print "UNDEFINED ARCHITECTURE"
            sys.exit(1)

    def extract_memory_files(self):
        fo_coe = open(self.outputfile_coe, "w")
        fo_mif = open(self.outputfile_mif, "w")
        fo_init = open(self.outputfile_init, "w")
        fo_final = open(self.outputfile_final, "w")
        fo_coe.write("memory_initialization_radix=16;\n")
        fo_coe.write("memory_initialization_vector=\n")
        for i in range(self.MEM_SIZE):
            fo_coe.write(self.mem_array_coe[i])
            fo_mif.write(self.mem_array_mif[i])
            
            if i == (self.MEM_SIZE-1):
                fo_coe.write(";")
            else:
                fo_coe.write(",\n")
                fo_mif.write("\n")

            if self.mem_array_init[i] != "garbage":
                mem_init_line = "memory"
                mem_init_line += "["
                mem_init_line += str(i)
                mem_init_line += "]"
                mem_init_line += " "
                mem_init_line += "="
                mem_init_line += " "
                mem_init_line += "16'h"
                mem_init_line += self.mem_array_init[i]
                mem_init_line += ";"
                
                fo_init.write(mem_init_line)

                if i != (self.MEM_SIZE-1):
                    fo_init.write("\n")

                mem_final_line = str(i)
                mem_final_line += ": "
                mem_final_line += str(self.mem_array_sim[i])

                fo_final.write(mem_final_line)

                if i != (self.MEM_SIZE-1):
                    fo_final.write("\n")


        fo_coe.close()
        fo_mif.close()
        fo_init.close()
        fo_final.close()

    def parse_and_create_memory_image(self):
        linenum = 0

        if platform.system() == "Darwin":
            lineendregex = "\r\n"
        elif platform.system() == "Linux":
            lineendregex = "\n"
        else:
            lineendregex = "\r\n"
    
        with open(self.inputfile) as fi:
            for line in fi:
            
                new_line_removed = re.sub(r"%s" % lineendregex, "", line)
            
                comment_removed = re.sub(r"//.*$", "", new_line_removed)

                if comment_removed == "":
                    continue
                                    
                index = (re.search(r"(\d+)", comment_removed)).group(0)
                                
                instruction_or_data = re.sub(r"(\d+):", "", comment_removed)
                if self.verbose: print instruction_or_data

                #regex = r"(\w+|\d*\.\d+|\d+)(\ +)([\-]?\w+)(\ +)([\-]?\w+)"
                regex = r"(\w+|\d*\.\d+|\d+)(\ +)([\-]?\w+)"
                
                if self.is_instruction_or_data(re.search(r"(\w+|\d*\.\d+|\d+)", instruction_or_data).group(0)):

                    if self.architecture == 1:
                        opcode = self.opcodes_v1[re.search(regex, instruction_or_data).group(1)]
                                        
                    operand_1 = re.search(regex, instruction_or_data).group(3)
                                        
                    if int(operand_1) < 0:
                        self.print_error(int(linenum), 1)
                    
                    instruction_dec = (opcode << 13) | (int(operand_1))
                    instruction_hex = format(instruction_dec, "08x")
                    instruction_hex = instruction_hex.lstrip("0")
                    self.mem_array_sim[int(index)] = instruction_dec
                    self.mem_array_coe[int(index)] = instruction_hex
                    self.mem_array_mif[int(index)] = format(instruction_dec, "032b")
                    self.mem_array_init[int(index)] = instruction_hex
                else:
                    if is_int(instruction_or_data):
                        
                        if self.architecture == 1 and int(instruction_or_data) < 0:
                            self.print_error(int(linenum), 1)

                        data = int(instruction_or_data)
                        
                        # used a small trick posted on stackoverflow to generate hex representation of data in .coe and .mif files (see https://stackoverflow.com/questions/7822956)
                        data_hex = (int(instruction_or_data) + (1 << 32)) % (1 << 32)
                        data_bin = data_hex
                        data_hex = format(data_hex, "08x")
                        if data_hex == "00000000":
                            data_hex  = "0"
                            self.mem_array_init[int(index)] = data_hex
                        else:
                            data_hex = data_hex.lstrip("0")
                            self.mem_array_sim[int(index)] = data
                            self.mem_array_coe[int(index)] = data_hex
                            self.mem_array_mif[int(index)] = format(data_bin, "032b")
                            self.mem_array_init[int(index)] = data_hex
                    
                    elif is_float(instruction_or_data):
                        if self.architecture == 1:
                            self.print_error(int(linenum), 1)
                        
                        # used a method posted on stackoverflow to generate hex representation of float data in .coe and .mif files (see https://stackoverflow.com/questions/23624212)
                        data_hex = hex(struct.unpack('<I', struct.pack('<f', float(instruction_or_data)))[0])
                        data_hex = re.sub(r"(0x)", "", data_hex)
                        # used a method posted on stackoverflow to generate binary representation of float data in .coe and .mif files (see https://stackoverflow.com/questions/16444726)
                        data_bin = ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', float(instruction_or_data)))
                        if data_hex == "00000000":
                            data_hex  = "0"
                        else:
                            data_hex = data_hex.lstrip("0")
                        self.mem_array_sim[int(index)] = float(instruction_or_data)
                        self.mem_array_coe[int(index)] = data_hex
                        self.mem_array_mif[int(index)] = data_bin
                        self.mem_array_init[int(index)] = data_hex

                linenum = linenum + 1

    def print_memory_cell(self, opcode, operand_1):
        if self.architecture == 1:
            if opcode == self.opcodes_v1["ADD"] or \
               opcode == self.opcodes_v1["NAND"] or \
               opcode == self.opcodes_v1["SRL"] or \
               opcode == self.opcodes_v1["LT"] or \
               opcode == self.opcodes_v1["MUL"] or \
               opcode == self.opcodes_v1["CP2W"] or \
               opcode == self.opcodes_v1["BZ"] or \
               opcode == self.opcodes_v1["CPfW"]:
                print "\tW\t\t\t:", self.wreg
                if operand_1 == 0:
                    print "\tmem[", self.indirection_register_index, "]\t\t:", self.mem_array_sim[self.indirection_register_index]
                    print "\tmem[", self.mem_array_sim[self.indirection_register_index], "]\t\t:", self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]] 
                else:
                    print "\tmem[", operand_1, "]\t\t:", self.mem_array_sim[operand_1]
                                    
    def run_instruction(self, opcode, operand_1):

        if self.architecture == 1:
            if (opcode >= 0 and opcode <= 7) and (opcode != 4):
                print "\tMemory content before executing instruction"
                self.print_memory_cell(opcode, operand_1)
                                
                if opcode == self.opcodes_v1["ADD"]:
                    if operand_1 == 0:
                        temp_1 = self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]]
                    else:
                        temp_1 = self.mem_array_sim[operand_1]

                    # used a small trick posted on stackoverflow to generate 2's complement representation of data for ISA v1 if needed (see https://stackoverflow.com/questions/1604464)
                    if (temp_1 & (1 << (32 - 1))) != 0:
                        temp_1 = temp_1 - (1 << 32)
                    else:
                        temp_1 = temp_1
                    
                    self.wreg = (temp_1 + self.wreg) & 0xFFFF
                elif opcode == self.opcodes_v1["NAND"]:
                    if operand_1 == 0:
                        temp_1 = self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]]
                    else:
                        temp_1 = self.mem_array_sim[operand_1]
                    
                    self.wreg = (~(temp_1 & self.wreg)) & 0xFFFF
                elif opcode == self.opcodes_v1["SRL"]: # CAUTION: it does not handle negative shift values
                    if operand_1 == 0:
                        temp_1 = self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]]
                    else:
                        temp_1 = self.mem_array_sim[operand_1]

                    if temp_1 <= 16:
                        # used a method posted on stackoverflow to get logical shift (see https://stackoverflow.com/questions/5832982)
                        self.wreg = (self.wreg % 0x10000) >> temp_1
                    else:
                        temp_shift_amount = temp_1
                        if temp_shift_amount > 32:
                            temp_shift_amount = 32
                        self.wreg = (self.wreg % 0x10000) << (temp_shift_amount - 16)
                    self.wreg = self.wreg & 0xFFFF
                elif opcode == self.opcodes_v1["LT"]:
                    if operand_1 == 0:
                        temp_1 = self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]]
                    else:
                        temp_1 = self.mem_array_sim[operand_1]

                    if self.wreg < temp_1:
                        self.wreg = 1
                    else:
                        self.wreg = 0
                elif opcode == self.opcodes_v1["MUL"]:
                    if operand_1 == 0:
                        temp_1 = self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]]
                    else:
                        temp_1 = self.mem_array_sim[operand_1]

                    # used a small trick posted on stackoverflow to generate 2's complement representation of data for ISA v1 if needed (see https://stackoverflow.com/questions/1604464)
                    if (temp_1 & (1 << (32 - 1))) != 0:
                        temp_1 = temp_1 - (1 << 32)
                    else:
                        temp_1 = temp_1

                    self.wreg = (temp_1 * self.wreg) & 0xFFFF
                elif opcode == self.opcodes_v1["CP2W"]:
                    if operand_1 == 0:
                        temp_1 = self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]]
                    else:
                        temp_1 = self.mem_array_sim[operand_1]

                    self.wreg = temp_1
                elif opcode == self.opcodes_v1["CPfW"]:
                    if operand_1 == 0:
                        temp_1 = self.mem_array_sim[self.indirection_register_index]
                    else:
                        temp_1 = operand_1

                    self.mem_array_sim[temp_1] = self.wreg
                                
                self.program_counter = self.program_counter + 1
            
                print "\tMemory content after executing instruction"
                self.print_memory_cell(opcode, operand_1)
            elif opcode == self.opcodes_v1["BZ"]:
                if operand_1 == 0:
                    temp_1 = self.mem_array_sim[self.mem_array_sim[self.indirection_register_index]]
                else:
                    temp_1 = self.mem_array_sim[operand_1]

                if self.wreg == 0:
                    self.program_counter = temp_1
                else:
                    self.program_counter = self.program_counter + 1

                print "\tnext program counter\t:", self.program_counter 
                    
                print "\tMemory content before executing instruction"
                self.print_memory_cell(opcode, operand_1)
                                
                print "\tMemory content after executing instruction"
                self.print_memory_cell(opcode, operand_1)
                
            else:
                print "UNDEFINED INSTRUCTION"
                sys.exit(1)
        else:
            print "UNDEFINED ARCHITECTURE"
            sys.exit(1)

    def run_simulation(self):

        print_blank_line(1)
        print "Starting simulation"
        print_blank_line(1)
        
        if self.sim_type == 0:
            print "run all mode selected"
        else:
            print "step-by-step mode selected"

        print_blank_line(1)      

        # CAUTION: it is assumed that instructions are always placed starting from very beginning of memory, i.e., address zero
        # parsing bits [15-13] to catch an instruction

        sim_finished = False
        
        while(sim_finished == False):

            if self.sim_type == 1:
                raw_input("\nPress any key to continue ")

            instruction_or_data = self.mem_array_sim[self.program_counter]
            
            # if (instruction_or_data & 0xFFFF) > 0: # CAUTION: it is assumed that instructions such as 'ADD 0' is not generated by compiler

            opcode = instruction_or_data >> 13
            operand_1 = (instruction_or_data) & 0x1FFF
   
            print_header("*", 25)
            if self.architecture == 1:
                print "\tcurrent_instruction\t:", self.opcodes_v1_r[opcode], operand_1
                print "\tcurrent program counter\t:", self.program_counter
                self.program_counter_prev = self.program_counter
                self.run_instruction(opcode, operand_1)
                print_footer("*", 25)
                
            if self.program_counter_prev == self.program_counter:
                print "Finishing simulation. Instruction called itself."
                sim_finished = True
            '''
            else:
                print "ADD 0 instruction caught. Finishing simulation."
                sim_finished = True
            '''
            
def main(argv):
   
    try:
        opts, args = getopt.getopt(argv,"hi:s:a:m:vx",["ifile=", "extract_memory_files", "sim=", "arch=", "memory_size="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(1)

    inputfile = ""
    extract = False
    verbose = False
    simulate = False
    sim_type = 0
    architecture = 0
    mem_size = 0
    
    if not opts:
        print_usage()
        sys.exit(1)
        
    for opt, arg in opts:
        if opt == '-h':
            print_usage(1)
            sys.exit(1)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-a", "--arch"):
            architecture = int(arg)
        elif opt in ("-s", "--sim"):
            simulate = True
            sim_type = int(arg)
        elif opt in ("-m", "--mem_size"):
            mem_size = int(arg)
        elif opt in ("-x", "--extract_memory_files"):
            extract = True
        elif opt in ("-v"):
            verbose = True
            print "Verbosing output"

    if inputfile == "" or architecture == 0 or mem_size < 0:
        print_usage(0)
        sys.exit(1)

    MyCPUSim = CPUSim(inputfile=inputfile, architecture=architecture, mem_size=mem_size, sim_type=sim_type, verbose=verbose)
    
    MyCPUSim.parse_and_create_memory_image()

    if simulate == True:
        MyCPUSim.run_simulation()

    if extract == True:
        print "Extracting memory initialization files"
        MyCPUSim.extract_memory_files()

if __name__ == "__main__":
    main(sys.argv[1:])
