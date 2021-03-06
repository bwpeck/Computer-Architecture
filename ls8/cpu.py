"""CPU functionality."""

import sys

class CPU: # Main CPU class.

    def __init__(self): # Construct a new CPU.
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 0
        self.running = False
        self.trans_instructions = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b00000001: self.hlt,
            0b10100000: self.add,
            0b10100001: self.sub,
            0b10100010: self.mul,
            0b10100011: self.div,
            0b10100100: self.mod,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret
        }
        self.intm = 5 # Interrupt Mask
        self.ints = 6 # Interrupt Status
        self.sp = 7 # Stack Pointer
        self.reg[self.sp] = 0xF4 # Decimal 243

    def load(self):
        """Load a program into memory."""
        args = sys.argv

        address = 0
        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        if len(args) > 1:
            program = []
            with open(args[1]) as f:
                for line in f.readlines():
                    if "#" in line:
                        ind = line.index("#")
                        line = line[:ind]
                        line.strip()
                    if "\n" in line:
                        line = line.replace("\n", "")
                    if line != "" and line != "\n":
                        program.append(int(line,2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1
        # print("instructions",self.ram)

    def alu(self, op, reg_a, reg_b): # ALU operations. Arithmetic Logic Unit
        def add():
            self.reg[self.ram[reg_a]] = self.reg[self.ram[reg_a]] + self.reg[self.ram[reg_b]]
        
        def sub():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] - self.reg[self.ram[reg_b]]
        
        def mul():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] * self.reg[self.ram[reg_b]]
        
        def div():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] / self.reg[self.ram[reg_b]]
        
        def mod():
            self.reg[self.ram[reg_a]] =  self.reg[self.ram[reg_a]] % self.reg[self.ram[reg_b]]

        instructions = {
            "ADD": add,
            "SUB": sub,
            "MUL": mul,
            "DIV": div,
            "MOD": mod
        }

        try:
            func = instructions[op]
            func()
        except:
            raise Exception("Unsupported ALU Operation")
    
    def cpu_instructions(self, inst, ram_a=None, ram_b=None):
        
        def ldi():
            self.reg[self.ram[ram_a]] = self.ram[ram_b]
        
        def prn():
            print(f"{self.reg[self.ram[ram_a]]}")
        
        def hlt():
            self.running = False

        cpu_inst = {
            "LDI": ldi,
            "PRN": prn,
            "HLT": hlt
        }

        try:
            func = cpu_inst[inst]
            func()
        except:
            raise Exception("Unsupported Instruction")
    
    def ram_read(self, pc):
        return self.ram[pc]
    
    def ram_write(self, pc, instruction):
        self.ram[pc] = instruction

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def call(self):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + ((self.ir & 0b11000000) >> 6) + 1
        val = self.ram[self.pc+1]
        self.pc = self.reg[val]
    
    def ret(self):
        val = self.ram[self.reg[self.sp]]
        self.pc = val
        self.reg[self.sp] += 1

    def push(self):
        self.reg[self.sp] -= 1
        reg_num = self.ram[self.pc+1]
        reg_val = self.reg[reg_num]
        self.ram[self.reg[self.sp]] = reg_val
        self.inc_pc()
    
    def pop(self):
        val = self.ram[self.reg[self.sp]]
        reg_num = self.ram[self.pc+1]
        self.reg[reg_num] = val
        self.reg[self.sp] += 1
        self.inc_pc()

    def ldi(self):
        self.cpu_instructions("LDI", self.pc+1, self.pc+2)
        self.inc_pc()

    def prn(self):
        self.cpu_instructions("PRN", self.pc+1)
        self.inc_pc()

    def hlt(self):
        self.cpu_instructions("HLT")
        self.inc_pc()
    
    def add(self):
        self.alu("ADD", self.pc+1, self.pc+2)
        self.inc_pc()
    
    def sub(self):
        self.alu("SUB", self.pc+1, self.pc+2)
        self.inc_pc()
    
    def mul(self):
        self.alu("MUL", self.pc+1, self.pc+2)
        self.inc_pc()
    
    def div(self):
        self.alu("DIV", self.pc+1, self.pc+2)
        self.inc_pc()
    
    def mod(self):
        self.alu("MOD", self.pc+1, self.pc+2)
        self.inc_pc()

    def inc_pc(self):
        self.pc += ((self.ir & 0b11000000) >> 6) + 1

    def run(self):
        self.running = True
        count = 0

        while self.running:
            self.ir = self.ram_read(self.pc)

            try:
                func = self.trans_instructions[self.ir]
                func()
            except:
                raise Exception("Unsupported Instruction")
                sys.exit(1)

