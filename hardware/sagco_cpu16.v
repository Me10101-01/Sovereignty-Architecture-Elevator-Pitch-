// ============================================================
// SAGCO-16 CPU Core — v0.1
// INV-127: SAGCO-16 Custom 8-bit Sovereign ISA
// Inventor: Domenic Gabriel Garza | Strategickhaos DAO LLC
// EIN: 39-2900295 | 2026-03-09
// ============================================================

module sagco_cpu(
    input  wire clk,
    input  wire rst,
    output wire [7:0] pc_out,
    output wire [7:0] alu_out,
    output wire       zero_flag,
    output wire       carry_flag,
    output wire [7:0] r0,
    output wire [7:0] r1,
    output wire [7:0] r2,
    output wire [7:0] r3
);

// ── Program Counter ──────────────────────────────────────
reg [7:0] pc;
assign pc_out = pc;

// ── Register File ────────────────────────────────────────
reg [7:0] regfile [0:3];
assign r0 = regfile[0];
assign r1 = regfile[1];
assign r2 = regfile[2];
assign r3 = regfile[3];

// ── Instruction Fetch ────────────────────────────────────
wire [7:0] instr;
sagco_mem mem(
    .addr(pc),
    .data(instr)
);

// ── Instruction Decode ───────────────────────────────────
wire [3:0] opcode = instr[7:4];
wire [1:0] ra     = instr[3:2];
wire [1:0] rb     = instr[1:0];

// ── ALU Execute ──────────────────────────────────────────
sagco_alu alu(
    .a(regfile[ra]),
    .b(regfile[rb]),
    .opcode(opcode),
    .out(alu_out),
    .zero_flag(zero_flag),
    .carry_flag(carry_flag)
);

// ── Writeback + Advance PC ───────────────────────────────
always @(posedge clk or posedge rst) begin
    if (rst) begin
        pc          <= 8'h00;
        regfile[0]  <= 8'd1;
        regfile[1]  <= 8'd2;
        regfile[2]  <= 8'd3;
        regfile[3]  <= 8'd4;
    end else begin
        case(opcode)
            4'b0001,          // ADD
            4'b0010,          // MOV
            4'b0011,          // XOR
            4'b0100,          // AND
            4'b0101,          // OR
            4'b0110,          // SUB
            4'b0111:          // SHL
                regfile[ra] <= alu_out;
            default: ;        // NOP — no writeback
        endcase
        pc <= pc + 8'h01;
    end
end

endmodule
