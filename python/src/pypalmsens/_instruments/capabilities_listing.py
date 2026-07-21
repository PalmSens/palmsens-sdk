from __future__ import annotations

METHODSCRIPT_CAPABILITIES = {
    # 0: 'RESERVED',
    1: 'var',
    2: 'array',
    3: 'store_var',
    4: 'copy_var',
    5: 'add_var',
    6: 'sub_var',
    7: 'mul_var',
    8: 'div_var',
    9: 'set_e',
    10: 'set_int',
    11: 'await_int',
    12: 'wait',
    13: 'loop',
    14: 'endloop',
    15: 'breakloop',
    16: 'if',
    17: 'else',
    18: 'elseif',
    19: 'endif',
    20: 'get_time',
    21: 'meas',
    # 22: 'RESERVED',
    23: 'meas_loop_lsv',
    24: 'meas_loop_cv',
    25: 'meas_loop_dpv',
    26: 'meas_loop_swv',
    27: 'meas_loop_npv',
    28: 'meas_loop_ca',
    29: 'meas_loop_pad',
    30: 'meas_loop_ocp',
    31: 'meas_loop_eis',
    32: 'set_autoranging',
    33: 'pck_start',
    34: 'pck_add',
    35: 'pck_end',
    36: 'set_max_bandwidth',
    37: 'set_cr',
    38: 'cell_on',
    39: 'cell_off',
    40: 'set_pgstat_mode',
    41: 'send_string',
    42: 'set_pgstat_chan',
    43: 'set_gpio_cfg',
    44: 'set_gpio_pullup',
    45: 'set_gpio',
    46: 'get_gpio',
    47: 'set_pot_range',
    # 48: 'RESERVED',
    49: 'set_poly_we_mode',
    50: 'file_open',
    51: 'file_close',
    52: 'set_script_output',
    53: 'array_get',
    54: 'array_set',
    55: 'i2c_config',
    56: 'i2c_read_byte',
    57: 'i2c_write_byte',
    58: 'i2c_read',
    59: 'i2c_write',
    60: 'i2c_write_read',
    61: 'hibernate',
    62: 'abort',
    63: 'timer_start',
    64: 'timer_get',
    65: 'set_range',
    66: 'set_range_minmax',
    67: 'meas_loop_cp',
    68: 'set_i',
    69: 'meas_loop_lsp',
    70: 'meas_loop_geis',
    71: 'int_to_float',
    72: 'float_to_int',
    73: 'bit_and_var',
    74: 'bit_or_var',
    75: 'bit_xor_var',
    76: 'bit_lsl_var',
    77: 'bit_lsr_var',
    78: 'bit_inv_var',
    79: 'set_channel_sync',
    80: 'set_acquisition_frac',
    81: 'mux_config',
    82: 'mux_get_channel_count',
    83: 'mux_set_channel',
    84: 'set_gpio_msk',
    85: 'get_gpio_msk',
    86: 'set_e_aux',
    # 87: 'RESERVED',
    88: 'set_ir_comp',
    # 89: 'RESERVED',
    90: 'meas_fast_cv',
    91: 'set_acquisition_frac_autoadjust',
    92: 'alter_vartype',
    93: 'meas_loop_acv',
    94: 'meas_ms_eis',
    95: 'meas_fast_ca',
    96: 'mod_var',
    97: 'notify_led',
    98: 'set_scan_dir',
    99: 'meas_loop_ca_alt_mux',
    100: 'meas_loop_cp_alt_mux',
    101: 'meas_loop_ocp_alt_mux',
    102: 'smooth',
    103: 'peak_detect',
    104: 'set_bipot_mode',
    105: 'set_bipot_potential',
    106: 'meas_loop_eis_dual',
    107: 'rtc_get',
    # 108: 'RESERVED',
    109: 'beep',
    110: 'battery_perc',
    111: 'get_progress',
    112: 'pow_var',
    113: 'subarray',
    114: 'log_var',
    115: 'linear_fit',
    116: 'mean',
    117: 'trim_enable',
    118: 'meas_scp',
    119: 'display_text',
    120: 'display_btns',
    121: 'display_clear',
    122: 'display_progress',
    123: 'display_icon',
    124: 'display_draw',
    125: 'display_inp_num',
    126: 'display_scroll_add',
    127: 'display_scroll_get',
    128: 'display_keyboard',
    129: 'qr_scan',
    130: 'str',
    131: 'store_str',
    132: 'load_saved_start',
    133: 'load_saved_end',
    134: 'load_saved_var',
    135: 'load_saved_str',
    136: 'save_var',
    137: 'save_str',
    138: 'float_to_int_round',
    139: 'display_filebrowse',
    140: 'droplet_detect_loop',
    141: 'str_find',
    142: 'str_length',
    143: 'str_parse_float',
    144: 'str_parse_int',
}

COMMUNICATION_CAPABILITIES = {
    # 0: 'RESERVED',
    1: 't',  # Get firmware version
    # 2 - 31: 'RESERVED',
    32: 'CC',  # Get runtime capabilities
    33: 'CM',  # Get MethodSCRIPT capabilities
    34: 'S',  # Set register
    35: 'G',  # Get register
    36: 'l',  # Load MethodSCRIPT
    37: 'r',  # Run loaded MethodSCRIPT
    38: 'e',  # Execute (= load and run) MethodSCRIPT
    39: 'dlfw',  # Enter bootloader
    # 40 - 42: 'RESERVED',
    43: 'Fmscr',  # Store loaded MethodSCRIPT to NVM
    44: 'Lmscr',  # Load MethodSCRIPT from NVM
    # 45 - 47: 'RESERVED',
    48: 'i',  # Get serial number
    49: 'v',  # Get MethodSCRIPT version
    # 50: 'RESERVED',
    51: 'fs_dir',  # Get directory listing
    52: 'fs_get',  # Read file
    53: 'fs_put',  # Write file
    54: 'fs_del',  # Delete file or directory
    55: 'fs_info',  # Get file system information
    56: 'fs_format',  # Format storage device
    57: 'fs_mount',  # Mount file system
    58: 'fs_unmount',  # Unmount file system
    59: 'fs_clear',  # Clear file system
    60: 'm',  # Get multi-channel serial number
    61: 'RESERVED',
    62: 'l_fs',  # Load MethodSCRIPT from file
    63: 'e_fs',  # Execute (= load and run) MethodSCRIPT from file
    64: 'sfs_put',  # Write file with cryptographic verification
    65: 'sfs_del',  # Delete file with cryptographic verification
    66: 'sfs_format',  # Format filesystem with cryptographic verification
    67: 'sfs_clear',  # Clear filesystem with cryptographic verification
    68: 'comm_lock',  # Comm Lock
    69: 'comm_unlock',  # Comm Unlock
    # 70 - 95: 'RESERVED',
    96: 'h',  # Halt script execution
    97: 'H',  # Resume script execution
    98: 'Z',  # Abort script execution
    99: 'Y',  # Abort measurement loop
    # 100: 'RESERVED',
    101: 'R',  # Reverse CV sweep
}
