"""
Phase 2: Control Unit
Symbolic instruction dispatch
"""

class ControlUnit:
    """Control flow management with symbolic dispatch."""
    
    def __init__(self):
        self.instruction_pointer = 0
        self.instructions = []
    
    def load_program(self, instructions):
        """Load instruction sequence."""
        self.instructions = instructions
        self.instruction_pointer = 0
    
    def fetch(self):
        """Fetch current instruction."""
        if self.instruction_pointer < len(self.instructions):
            return self.instructions[self.instruction_pointer]
        return None
    
    def execute(self, instruction):
        """Execute instruction."""
        print(f"Executing: {instruction}")
        self.instruction_pointer += 1
    
    def run(self):
        """Run program."""
        while self.instruction_pointer < len(self.instructions):
            instr = self.fetch()
            if instr:
                self.execute(instr)


if __name__ == '__main__':
    cu = ControlUnit()
    cu.load_program(['ADD', 'MUL', 'STORE', 'HALT'])
    cu.run()
    print("Control Unit: Program execution complete")
