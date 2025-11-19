`default_nettype none
module user_project_wrapper #(
    parameter BITS = 32
) (
`ifdef USE_POWER_PINS
    inout vdda1, inout vdda2,
    inout vssa1, inout vssa2,
    inout vccd1, inout vccd2,
    inout vssd1, inout vssd2,
`endif

    // Wishbone
    input         wb_clk_i,
    input         wb_rst_i,
    input         wbs_stb_i,
    input         wbs_cyc_i,
    input         wbs_we_i,
    input  [3:0]  wbs_sel_i,
    input  [31:0] wbs_dat_i,
    input  [31:0] wbs_adr_i,
    output        wbs_ack_o,
    output [31:0] wbs_dat_o,

    // Logic Analyzer
    input  [127:0] la_data_in,
    output [127:0] la_data_out,
    input  [127:0] la_oenb,

    // Digital IOs
    input  [`MPRJ_IO_PADS-1:0] io_in,
    output [`MPRJ_IO_PADS-1:0] io_out,
    output [`MPRJ_IO_PADS-1:0] io_oeb,

    // Analog IOs (analog_io[k] <-> GPIO pad k+7)
    inout  [`MPRJ_IO_PADS-10:0] analog_io,

    // Extra user clock
    input   user_clock2,

    // IRQs
    output [2:0] user_irq
);

    // -------------------------------------------------------------------------
    // Wishbone Address Map and Arbitration
    // -------------------------------------------------------------------------
    localparam [31:0] NEURO_BASE   = 32'h3000_0000;  // Neuromorphic module
    localparam [31:0] MATMUL_BASE  = 32'h3100_0000;  // Matrix multiplier
    localparam [31:0] MPRJ_MASK    = 32'hFFFF_F000;  // 4KB region mask

    wire sel_neuro  = ((wbs_adr_i & MPRJ_MASK) == NEURO_BASE);
    wire sel_matmul = ((wbs_adr_i & MPRJ_MASK) == MATMUL_BASE);

    // Gate cyc/stb for each module
    wire wbs_cyc_i_neuro  = wbs_cyc_i & sel_neuro;
    wire wbs_stb_i_neuro  = wbs_stb_i & sel_neuro;

    wire wbs_cyc_i_matmul = wbs_cyc_i & sel_matmul;
    wire wbs_stb_i_matmul = wbs_stb_i & sel_matmul;

    // Return paths from each module
    wire        wbs_ack_o_neuro,  wbs_ack_o_matmul;
    wire [31:0] wbs_dat_o_neuro,  wbs_dat_o_matmul;

    // IRQ from matrix multiplier
    wire irq_matmul;

    // -------------------------------------------------------------------------
    // Neuromorphic Module Instance
    // -------------------------------------------------------------------------
    Neuromorphic_X1_wb neuro_inst (
`ifdef USE_POWER_PINS
        .VDDC (vccd1),
        .VDDA (vdda1),
        .VSS  (vssd1),
`endif

        // Clocks / resets
        .user_clk (wb_clk_i),
        .user_rst (wb_rst_i),
        .wb_clk_i (wb_clk_i),
        .wb_rst_i (wb_rst_i),

        // Wishbone (gated)
        .wbs_stb_i (wbs_stb_i_neuro),
        .wbs_cyc_i (wbs_cyc_i_neuro),
        .wbs_we_i  (wbs_we_i),
        .wbs_sel_i (wbs_sel_i),
        .wbs_dat_i (wbs_dat_i),
        .wbs_adr_i (wbs_adr_i),
        .wbs_dat_o (wbs_dat_o_neuro),
        .wbs_ack_o (wbs_ack_o_neuro),

        // Scan/Test
        // io[0:6] either reserved or unused (on powerup),
        // so place after analog pins
        .ScanInCC  (io_in[24]),
        .ScanInDL  (io_in[21]),
        .ScanInDR  (io_in[22]),
        .TM        (io_in[25]),
        .ScanOutCC (io_out[20]),

        // Analog / bias pins (drive from analog_io[] wires you already built)
        // analog_io[k] = io[k + 7], below essentially uses io[7:19]
        .Iref          (analog_io[0]),
        .Vcc_read      (analog_io[1]),
        .Vcomp         (analog_io[2]),
        .Bias_comp2    (analog_io[3]),
        .Vcc_wl_read   (analog_io[12]),
        .Vcc_wl_set    (analog_io[5]),
        .Vbias         (analog_io[6]),
        .Vcc_wl_reset  (analog_io[7]),
        .Vcc_set       (analog_io[8]),
        .Vcc_reset     (analog_io[9]),
        .Vcc_L         (analog_io[10]),
        .Vcc_Body      (analog_io[11])
    );

    // -------------------------------------------------------------------------
    // Matrix Multiplier Instance
    // -------------------------------------------------------------------------
    mat_mult_wb #(
        .BASE_ADDR(MATMUL_BASE)  // Set to 0x31000000
    ) matmul_inst (
        // Wishbone interface (gated)
        .wb_clk_i  (wb_clk_i),
        .wb_rst_i  (wb_rst_i),
        .wbs_stb_i (wbs_stb_i_matmul),
        .wbs_cyc_i (wbs_cyc_i_matmul),
        .wbs_we_i  (wbs_we_i),
        .wbs_sel_i (wbs_sel_i),
        .wbs_dat_i (wbs_dat_i),
        .wbs_adr_i (wbs_adr_i),
        .wbs_dat_o (wbs_dat_o_matmul),
        .wbs_ack_o (wbs_ack_o_matmul),

        // Interrupt output
        .irq_o     (irq_matmul)
    );

    // -------------------------------------------------------------------------
    // Wishbone Output Mux
    // -------------------------------------------------------------------------
    // Selected module drives the return bus
    assign wbs_ack_o = (sel_neuro  ? wbs_ack_o_neuro  : 1'b0)
                     | (sel_matmul ? wbs_ack_o_matmul : 1'b0);

    assign wbs_dat_o = sel_neuro  ? wbs_dat_o_neuro  :
                       sel_matmul ? wbs_dat_o_matmul :
                       32'h0000_0000;

    // -------------------------------------------------------------------------
    // IRQ and Unused Outputs
    // -------------------------------------------------------------------------
    // Connect matrix multiplier IRQ to user_irq[0]
    assign user_irq = {2'b00, irq_matmul};

    // https://chipfoundry.io/knowledge-base/connecting-gpios
    // Make sure to drive io_oeb[20] low to enable io 20 (ScanOutCC) as output
    assign io_oeb = {{(`MPRJ_IO_PADS-21){1'b1}}, 1'b0, {20{1'b1}}};

    // Tie off unused outputs
    assign la_data_out               = 128'b0;
    assign io_out[`MPRJ_IO_PADS-1:21] = {(`MPRJ_IO_PADS-21){1'b0}};
    assign io_out[19:0]               = {20{1'b0}};
    // Note: io_out[20] driven by neuro_inst.ScanOutCC

endmodule
`default_nettype wire


