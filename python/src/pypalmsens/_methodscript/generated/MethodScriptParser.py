# mypy: ignore_errors
# Generated from MethodScriptParser.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,169,301,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,
        7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,
        13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,
        20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,
        26,1,0,1,0,5,0,57,8,0,10,0,12,0,60,9,0,1,0,1,0,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,3,1,72,8,1,1,2,1,2,1,2,1,3,1,3,1,3,3,3,80,8,3,1,3,
        1,3,1,4,1,4,1,4,1,4,3,4,88,8,4,1,4,1,4,1,5,1,5,1,5,3,5,95,8,5,1,
        5,1,5,1,6,1,6,1,6,3,6,102,8,6,1,6,1,6,1,6,5,6,107,8,6,10,6,12,6,
        110,9,6,1,6,5,6,113,8,6,10,6,12,6,116,9,6,1,6,3,6,119,8,6,1,6,1,
        6,3,6,123,8,6,1,6,1,6,1,7,1,7,1,7,3,7,130,8,7,1,7,1,7,1,7,5,7,135,
        8,7,10,7,12,7,138,9,7,1,8,1,8,3,8,142,8,8,1,8,1,8,1,8,5,8,147,8,
        8,10,8,12,8,150,9,8,1,9,1,9,1,9,3,9,155,8,9,1,9,1,9,1,9,5,9,160,
        8,9,10,9,12,9,163,9,9,1,9,1,9,3,9,167,8,9,1,9,1,9,1,10,1,10,3,10,
        173,8,10,1,10,1,10,1,11,1,11,3,11,179,8,11,1,11,1,11,1,12,1,12,1,
        12,1,12,1,13,1,13,1,14,1,14,1,14,3,14,192,8,14,1,15,1,15,1,15,1,
        15,1,15,1,16,1,16,3,16,201,8,16,1,17,1,17,5,17,205,8,17,10,17,12,
        17,208,9,17,1,17,5,17,211,8,17,10,17,12,17,214,9,17,1,17,3,17,217,
        8,17,1,17,1,17,1,18,1,18,5,18,223,8,18,10,18,12,18,226,9,18,1,18,
        5,18,229,8,18,10,18,12,18,232,9,18,1,18,3,18,235,8,18,1,18,1,18,
        1,18,5,18,240,8,18,10,18,12,18,243,9,18,1,18,1,18,3,18,247,8,18,
        1,18,1,18,1,19,1,19,1,19,5,19,254,8,19,10,19,12,19,257,9,19,1,19,
        1,19,1,20,1,20,1,21,1,21,1,22,1,22,1,22,1,22,3,22,269,8,22,1,23,
        1,23,1,23,1,23,1,23,3,23,276,8,23,1,24,1,24,5,24,280,8,24,10,24,
        12,24,283,9,24,1,24,1,24,1,25,1,25,1,25,3,25,290,8,25,1,26,1,26,
        1,26,1,26,1,26,3,26,297,8,26,1,26,1,26,1,26,0,0,27,0,2,4,6,8,10,
        12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,0,
        5,2,0,152,152,155,155,1,0,137,144,1,0,11,27,7,0,28,47,49,56,58,60,
        62,74,79,98,101,129,131,136,2,0,164,164,167,167,327,0,58,1,0,0,0,
        2,71,1,0,0,0,4,73,1,0,0,0,6,76,1,0,0,0,8,83,1,0,0,0,10,91,1,0,0,
        0,12,98,1,0,0,0,14,126,1,0,0,0,16,139,1,0,0,0,18,151,1,0,0,0,20,
        170,1,0,0,0,22,176,1,0,0,0,24,182,1,0,0,0,26,186,1,0,0,0,28,191,
        1,0,0,0,30,193,1,0,0,0,32,200,1,0,0,0,34,202,1,0,0,0,36,220,1,0,
        0,0,38,250,1,0,0,0,40,260,1,0,0,0,42,262,1,0,0,0,44,268,1,0,0,0,
        46,275,1,0,0,0,48,277,1,0,0,0,50,289,1,0,0,0,52,291,1,0,0,0,54,57,
        3,2,1,0,55,57,3,4,2,0,56,54,1,0,0,0,56,55,1,0,0,0,57,60,1,0,0,0,
        58,56,1,0,0,0,58,59,1,0,0,0,59,61,1,0,0,0,60,58,1,0,0,0,61,62,5,
        0,0,1,62,1,1,0,0,0,63,72,3,6,3,0,64,72,3,8,4,0,65,72,3,10,5,0,66,
        72,3,32,16,0,67,72,3,12,6,0,68,72,3,18,9,0,69,72,3,20,10,0,70,72,
        3,22,11,0,71,63,1,0,0,0,71,64,1,0,0,0,71,65,1,0,0,0,71,66,1,0,0,
        0,71,67,1,0,0,0,71,68,1,0,0,0,71,69,1,0,0,0,71,70,1,0,0,0,72,3,1,
        0,0,0,73,74,5,156,0,0,74,75,5,158,0,0,75,5,1,0,0,0,76,77,5,1,0,0,
        77,79,5,155,0,0,78,80,5,156,0,0,79,78,1,0,0,0,79,80,1,0,0,0,80,81,
        1,0,0,0,81,82,5,158,0,0,82,7,1,0,0,0,83,84,5,2,0,0,84,85,5,155,0,
        0,85,87,7,0,0,0,86,88,5,156,0,0,87,86,1,0,0,0,87,88,1,0,0,0,88,89,
        1,0,0,0,89,90,5,158,0,0,90,9,1,0,0,0,91,92,5,130,0,0,92,94,5,155,
        0,0,93,95,5,156,0,0,94,93,1,0,0,0,94,95,1,0,0,0,95,96,1,0,0,0,96,
        97,5,158,0,0,97,11,1,0,0,0,98,99,5,3,0,0,99,101,3,24,12,0,100,102,
        5,156,0,0,101,100,1,0,0,0,101,102,1,0,0,0,102,103,1,0,0,0,103,108,
        5,158,0,0,104,107,3,2,1,0,105,107,3,4,2,0,106,104,1,0,0,0,106,105,
        1,0,0,0,107,110,1,0,0,0,108,106,1,0,0,0,108,109,1,0,0,0,109,114,
        1,0,0,0,110,108,1,0,0,0,111,113,3,14,7,0,112,111,1,0,0,0,113,116,
        1,0,0,0,114,112,1,0,0,0,114,115,1,0,0,0,115,118,1,0,0,0,116,114,
        1,0,0,0,117,119,3,16,8,0,118,117,1,0,0,0,118,119,1,0,0,0,119,120,
        1,0,0,0,120,122,5,6,0,0,121,123,5,156,0,0,122,121,1,0,0,0,122,123,
        1,0,0,0,123,124,1,0,0,0,124,125,5,158,0,0,125,13,1,0,0,0,126,127,
        5,4,0,0,127,129,3,24,12,0,128,130,5,156,0,0,129,128,1,0,0,0,129,
        130,1,0,0,0,130,131,1,0,0,0,131,136,5,158,0,0,132,135,3,2,1,0,133,
        135,3,4,2,0,134,132,1,0,0,0,134,133,1,0,0,0,135,138,1,0,0,0,136,
        134,1,0,0,0,136,137,1,0,0,0,137,15,1,0,0,0,138,136,1,0,0,0,139,141,
        5,5,0,0,140,142,5,156,0,0,141,140,1,0,0,0,141,142,1,0,0,0,142,143,
        1,0,0,0,143,148,5,158,0,0,144,147,3,2,1,0,145,147,3,4,2,0,146,144,
        1,0,0,0,146,145,1,0,0,0,147,150,1,0,0,0,148,146,1,0,0,0,148,149,
        1,0,0,0,149,17,1,0,0,0,150,148,1,0,0,0,151,152,5,7,0,0,152,154,3,
        24,12,0,153,155,5,156,0,0,154,153,1,0,0,0,154,155,1,0,0,0,155,156,
        1,0,0,0,156,161,5,158,0,0,157,160,3,2,1,0,158,160,3,4,2,0,159,157,
        1,0,0,0,159,158,1,0,0,0,160,163,1,0,0,0,161,159,1,0,0,0,161,162,
        1,0,0,0,162,164,1,0,0,0,163,161,1,0,0,0,164,166,5,8,0,0,165,167,
        5,156,0,0,166,165,1,0,0,0,166,167,1,0,0,0,167,168,1,0,0,0,168,169,
        5,158,0,0,169,19,1,0,0,0,170,172,5,9,0,0,171,173,5,156,0,0,172,171,
        1,0,0,0,172,173,1,0,0,0,173,174,1,0,0,0,174,175,5,158,0,0,175,21,
        1,0,0,0,176,178,5,10,0,0,177,179,5,156,0,0,178,177,1,0,0,0,178,179,
        1,0,0,0,179,180,1,0,0,0,180,181,5,158,0,0,181,23,1,0,0,0,182,183,
        3,28,14,0,183,184,3,26,13,0,184,185,3,28,14,0,185,25,1,0,0,0,186,
        187,7,1,0,0,187,27,1,0,0,0,188,192,5,155,0,0,189,192,3,30,15,0,190,
        192,3,46,23,0,191,188,1,0,0,0,191,189,1,0,0,0,191,190,1,0,0,0,192,
        29,1,0,0,0,193,194,5,155,0,0,194,195,5,147,0,0,195,196,7,0,0,0,196,
        197,5,148,0,0,197,31,1,0,0,0,198,201,3,34,17,0,199,201,3,36,18,0,
        200,198,1,0,0,0,200,199,1,0,0,0,201,33,1,0,0,0,202,206,3,42,21,0,
        203,205,3,44,22,0,204,203,1,0,0,0,205,208,1,0,0,0,206,204,1,0,0,
        0,206,207,1,0,0,0,207,212,1,0,0,0,208,206,1,0,0,0,209,211,3,38,19,
        0,210,209,1,0,0,0,211,214,1,0,0,0,212,210,1,0,0,0,212,213,1,0,0,
        0,213,216,1,0,0,0,214,212,1,0,0,0,215,217,5,156,0,0,216,215,1,0,
        0,0,216,217,1,0,0,0,217,218,1,0,0,0,218,219,5,158,0,0,219,35,1,0,
        0,0,220,224,3,40,20,0,221,223,3,44,22,0,222,221,1,0,0,0,223,226,
        1,0,0,0,224,222,1,0,0,0,224,225,1,0,0,0,225,230,1,0,0,0,226,224,
        1,0,0,0,227,229,3,38,19,0,228,227,1,0,0,0,229,232,1,0,0,0,230,228,
        1,0,0,0,230,231,1,0,0,0,231,234,1,0,0,0,232,230,1,0,0,0,233,235,
        5,156,0,0,234,233,1,0,0,0,234,235,1,0,0,0,235,236,1,0,0,0,236,241,
        5,158,0,0,237,240,3,2,1,0,238,240,3,4,2,0,239,237,1,0,0,0,239,238,
        1,0,0,0,240,243,1,0,0,0,241,239,1,0,0,0,241,242,1,0,0,0,242,244,
        1,0,0,0,243,241,1,0,0,0,244,246,5,8,0,0,245,247,5,156,0,0,246,245,
        1,0,0,0,246,247,1,0,0,0,247,248,1,0,0,0,248,249,5,158,0,0,249,37,
        1,0,0,0,250,251,5,155,0,0,251,255,5,145,0,0,252,254,3,44,22,0,253,
        252,1,0,0,0,254,257,1,0,0,0,255,253,1,0,0,0,255,256,1,0,0,0,256,
        258,1,0,0,0,257,255,1,0,0,0,258,259,5,146,0,0,259,39,1,0,0,0,260,
        261,7,2,0,0,261,41,1,0,0,0,262,263,7,3,0,0,263,43,1,0,0,0,264,269,
        3,46,23,0,265,269,5,155,0,0,266,269,3,30,15,0,267,269,5,154,0,0,
        268,264,1,0,0,0,268,265,1,0,0,0,268,266,1,0,0,0,268,267,1,0,0,0,
        269,45,1,0,0,0,270,276,5,152,0,0,271,276,5,153,0,0,272,276,5,150,
        0,0,273,276,3,48,24,0,274,276,5,151,0,0,275,270,1,0,0,0,275,271,
        1,0,0,0,275,272,1,0,0,0,275,273,1,0,0,0,275,274,1,0,0,0,276,47,1,
        0,0,0,277,281,5,149,0,0,278,280,3,50,25,0,279,278,1,0,0,0,280,283,
        1,0,0,0,281,279,1,0,0,0,281,282,1,0,0,0,282,284,1,0,0,0,283,281,
        1,0,0,0,284,285,5,163,0,0,285,49,1,0,0,0,286,290,5,160,0,0,287,290,
        5,161,0,0,288,290,3,52,26,0,289,286,1,0,0,0,289,287,1,0,0,0,289,
        288,1,0,0,0,290,51,1,0,0,0,291,292,5,162,0,0,292,296,5,164,0,0,293,
        294,5,165,0,0,294,295,7,4,0,0,295,297,5,166,0,0,296,293,1,0,0,0,
        296,297,1,0,0,0,297,298,1,0,0,0,298,299,5,168,0,0,299,53,1,0,0,0,
        41,56,58,71,79,87,94,101,106,108,114,118,122,129,134,136,141,146,
        148,154,159,161,166,172,178,191,200,206,212,216,224,230,234,239,
        241,246,255,268,275,281,289,296
    ]

class MethodScriptParser ( Parser ):

    grammarFileName = "MethodScriptParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'var'", "'array'", "'if'", "'elseif'", 
                     "'else'", "'endif'", "'loop'", "'endloop'", "'breakloop'", 
                     "'on_finished:'", "'meas_loop_acv'", "'meas_loop_ca'", 
                     "'meas_loop_ca_alt_mux'", "'meas_loop_cp'", "'meas_loop_cp_alt_mux'", 
                     "'meas_loop_cv'", "'meas_loop_dpv'", "'meas_loop_eis'", 
                     "'meas_loop_eis_dual'", "'meas_loop_geis'", "'meas_loop_lsp'", 
                     "'meas_loop_lsv'", "'meas_loop_npv'", "'meas_loop_ocp'", 
                     "'meas_loop_ocp_alt_mux'", "'meas_loop_pad'", "'meas_loop_swv'", 
                     "'abort'", "'add_var'", "'alter_vartype'", "'array_get'", 
                     "'array_set'", "'await_int'", "'battery_perc'", "'beep'", 
                     "'bit_and_var'", "'bit_inv_var'", "'bit_lsl_var'", 
                     "'bit_lsr_var'", "'bit_or_var'", "'bit_xor_var'", "'cell_off'", 
                     "'cell_on'", "'copy_var'", "'display_btns'", "'display_clear'", 
                     "'display_draw'", "'display_filebrowse'", "'display_icon'", 
                     "'display_inp_num'", "'display_keyboard'", "'display_progress'", 
                     "'display_scroll_add'", "'display_scroll_get'", "'display_text'", 
                     "'div_var'", "'drop_detect_loop'", "'file_close'", 
                     "'file_open'", "'float_to_int'", "'float_to_int_round'", 
                     "'get_gpio'", "'get_gpio_msk'", "'get_progress'", "'get_time'", 
                     "'hibernate'", "'i2c_config'", "'i2c_read'", "'i2c_read_byte'", 
                     "'i2c_write'", "'i2c_write_byte'", "'i2c_write_read'", 
                     "'int_to_float'", "'linear_fit'", "'load_saved_end'", 
                     "'load_saved_start'", "'load_saved_str'", "'load_saved_var'", 
                     "'log_var'", "'mean'", "'meas'", "'meas_fast_ca'", 
                     "'meas_fast_cv'", "'meas_ms_eis'", "'meas_scp'", "'mod_var'", 
                     "'mul_var'", "'mux_config'", "'mux_get_channel_count'", 
                     "'mux_set_channel'", "'notify_led'", "'pck_add'", "'pck_end'", 
                     "'pck_start'", "'peak_detect'", "'pow_var'", "'qr_scan'", 
                     "'rtc_get'", "'save_str'", "'save_var'", "'send_string'", 
                     "'set_acquisition_frac'", "'set_acquisition_frac_autoadjust'", 
                     "'set_autoranging'", "'set_bipot_mode'", "'set_bipot_potential'", 
                     "'set_channel_sync'", "'set_cr'", "'set_e'", "'set_e_aux'", 
                     "'set_gpio'", "'set_gpio_cfg'", "'set_gpio_msk'", "'set_gpio_pullup'", 
                     "'set_i'", "'set_int'", "'set_ir_comp'", "'set_max_bandwidth'", 
                     "'set_pgstat_chan'", "'set_pgstat_mode'", "'set_poly_we_mode'", 
                     "'set_pot_range'", "'set_range'", "'set_range_minmax'", 
                     "'set_scan_dir'", "'set_script_output'", "'smooth'", 
                     "'store_str'", "'store_var'", "'str'", "'sub_var'", 
                     "'subarray'", "'timer_get'", "'timer_start'", "'trim_enable'", 
                     "'wait'", "'=='", "'!='", "'>='", "'<='", "'>'", "'<'", 
                     "'&'", "'|'", "'('", "')'", "<INVALID>", "<INVALID>", 
                     "'f\"'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'{'", "'\"'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'}'" ]

    symbolicNames = [ "<INVALID>", "VAR", "ARRAY", "IF", "ELSEIF", "ELSE", 
                      "ENDIF", "LOOP", "ENDLOOP", "BREAKLOOP", "ON_FINISHED", 
                      "MEAS_LOOP_ACV", "MEAS_LOOP_CA", "MEAS_LOOP_CA_ALT_MUX", 
                      "MEAS_LOOP_CP", "MEAS_LOOP_CP_ALT_MUX", "MEAS_LOOP_CV", 
                      "MEAS_LOOP_DPV", "MEAS_LOOP_EIS", "MEAS_LOOP_EIS_DUAL", 
                      "MEAS_LOOP_GEIS", "MEAS_LOOP_LSP", "MEAS_LOOP_LSV", 
                      "MEAS_LOOP_NPV", "MEAS_LOOP_OCP", "MEAS_LOOP_OCP_ALT_MUX", 
                      "MEAS_LOOP_PAD", "MEAS_LOOP_SWV", "ABORT", "ADD_VAR", 
                      "ALTER_VARTYPE", "ARRAY_GET", "ARRAY_SET", "AWAIT_INT", 
                      "BATTERY_PERC", "BEEP", "BIT_AND_VAR", "BIT_INV_VAR", 
                      "BIT_LSL_VAR", "BIT_LSR_VAR", "BIT_OR_VAR", "BIT_XOR_VAR", 
                      "CELL_OFF", "CELL_ON", "COPY_VAR", "DISPLAY_BTNS", 
                      "DISPLAY_CLEAR", "DISPLAY_DRAW", "DISPLAY_FILEBROWSE", 
                      "DISPLAY_ICON", "DISPLAY_INP_NUM", "DISPLAY_KEYBOARD", 
                      "DISPLAY_PROGRESS", "DISPLAY_SCROLL_ADD", "DISPLAY_SCROLL_GET", 
                      "DISPLAY_TEXT", "DIV_VAR", "DROP_DETECT_LOOP", "FILE_CLOSE", 
                      "FILE_OPEN", "FLOAT_TO_INT", "FLOAT_TO_INT_ROUND", 
                      "GET_GPIO", "GET_GPIO_MSK", "GET_PROGRESS", "GET_TIME", 
                      "HIBERNATE", "I2C_CONFIG", "I2C_READ", "I2C_READ_BYTE", 
                      "I2C_WRITE", "I2C_WRITE_BYTE", "I2C_WRITE_READ", "INT_TO_FLOAT", 
                      "LINEAR_FIT", "LOAD_SAVED_END", "LOAD_SAVED_START", 
                      "LOAD_SAVED_STR", "LOAD_SAVED_VAR", "LOG_VAR", "MEAN", 
                      "MEAS", "MEAS_FAST_CA", "MEAS_FAST_CV", "MEAS_MS_EIS", 
                      "MEAS_SCP", "MOD_VAR", "MUL_VAR", "MUX_CONFIG", "MUX_GET_CHANNEL_COUNT", 
                      "MUX_SET_CHANNEL", "NOTIFY_LED", "PCK_ADD", "PCK_END", 
                      "PCK_START", "PEAK_DETECT", "POW_VAR", "QR_SCAN", 
                      "RTC_GET", "SAVE_STR", "SAVE_VAR", "SEND_STRING", 
                      "SET_ACQUISITION_FRAC", "SET_ACQUISITION_FRAC_AUTOADJUST", 
                      "SET_AUTORANGING", "SET_BIPOT_MODE", "SET_BIPOT_POTENTIAL", 
                      "SET_CHANNEL_SYNC", "SET_CR", "SET_E", "SET_E_AUX", 
                      "SET_GPIO", "SET_GPIO_CFG", "SET_GPIO_MSK", "SET_GPIO_PULLUP", 
                      "SET_I", "SET_INT", "SET_IR_COMP", "SET_MAX_BANDWIDTH", 
                      "SET_PGSTAT_CHAN", "SET_PGSTAT_MODE", "SET_POLY_WE_MODE", 
                      "SET_POT_RANGE", "SET_RANGE", "SET_RANGE_MINMAX", 
                      "SET_SCAN_DIR", "SET_SCRIPT_OUTPUT", "SMOOTH", "STORE_STR", 
                      "STORE_VAR", "STR", "SUB_VAR", "SUBARRAY", "TIMER_GET", 
                      "TIMER_START", "TRIM_ENABLE", "WAIT", "EQ", "NE", 
                      "GE", "LE", "GT", "LT", "AND", "OR", "LPAREN", "RPAREN", 
                      "LBRACK", "RBRACK", "FSTRING_START", "STRING_LITERAL", 
                      "INVALID_STRING_LITERAL", "INTEGER_LITERAL", "FLOAT_LITERAL", 
                      "INVALID_NUMERIC_LITERAL", "IDENTIFIER", "COMMENT", 
                      "WS", "NEWLINE", "UNRECOGNIZED_CHAR", "FSTRING_TEXT", 
                      "FSTRING_ESCAPE", "FSTRING_INTERP_START", "FSTRING_END", 
                      "FSTRING_IDENTIFIER", "FSTRING_LBRACK", "FSTRING_RBRACK", 
                      "FSTRING_INTEGER", "FSTRING_INTERP_END", "FSTRING_WS_INTERP" ]

    RULE_sourceFile = 0
    RULE_statement = 1
    RULE_commentLine = 2
    RULE_variableDeclaration = 3
    RULE_arrayDeclaration = 4
    RULE_stringDeclaration = 5
    RULE_ifStatement = 6
    RULE_elseifClause = 7
    RULE_elseClause = 8
    RULE_loopStatement = 9
    RULE_breakStatement = 10
    RULE_tag = 11
    RULE_conditionalExpression = 12
    RULE_operator = 13
    RULE_operand = 14
    RULE_arrayAccess = 15
    RULE_commandCall = 16
    RULE_simpleCommand = 17
    RULE_measurementLoop = 18
    RULE_optionalArgumentBlock = 19
    RULE_measurementCommand = 20
    RULE_commandName = 21
    RULE_argument = 22
    RULE_literal = 23
    RULE_fstringLiteral = 24
    RULE_fstringContent = 25
    RULE_fstringInterpolation = 26

    ruleNames =  [ "sourceFile", "statement", "commentLine", "variableDeclaration", 
                   "arrayDeclaration", "stringDeclaration", "ifStatement", 
                   "elseifClause", "elseClause", "loopStatement", "breakStatement", 
                   "tag", "conditionalExpression", "operator", "operand", 
                   "arrayAccess", "commandCall", "simpleCommand", "measurementLoop", 
                   "optionalArgumentBlock", "measurementCommand", "commandName", 
                   "argument", "literal", "fstringLiteral", "fstringContent", 
                   "fstringInterpolation" ]

    EOF = Token.EOF
    VAR=1
    ARRAY=2
    IF=3
    ELSEIF=4
    ELSE=5
    ENDIF=6
    LOOP=7
    ENDLOOP=8
    BREAKLOOP=9
    ON_FINISHED=10
    MEAS_LOOP_ACV=11
    MEAS_LOOP_CA=12
    MEAS_LOOP_CA_ALT_MUX=13
    MEAS_LOOP_CP=14
    MEAS_LOOP_CP_ALT_MUX=15
    MEAS_LOOP_CV=16
    MEAS_LOOP_DPV=17
    MEAS_LOOP_EIS=18
    MEAS_LOOP_EIS_DUAL=19
    MEAS_LOOP_GEIS=20
    MEAS_LOOP_LSP=21
    MEAS_LOOP_LSV=22
    MEAS_LOOP_NPV=23
    MEAS_LOOP_OCP=24
    MEAS_LOOP_OCP_ALT_MUX=25
    MEAS_LOOP_PAD=26
    MEAS_LOOP_SWV=27
    ABORT=28
    ADD_VAR=29
    ALTER_VARTYPE=30
    ARRAY_GET=31
    ARRAY_SET=32
    AWAIT_INT=33
    BATTERY_PERC=34
    BEEP=35
    BIT_AND_VAR=36
    BIT_INV_VAR=37
    BIT_LSL_VAR=38
    BIT_LSR_VAR=39
    BIT_OR_VAR=40
    BIT_XOR_VAR=41
    CELL_OFF=42
    CELL_ON=43
    COPY_VAR=44
    DISPLAY_BTNS=45
    DISPLAY_CLEAR=46
    DISPLAY_DRAW=47
    DISPLAY_FILEBROWSE=48
    DISPLAY_ICON=49
    DISPLAY_INP_NUM=50
    DISPLAY_KEYBOARD=51
    DISPLAY_PROGRESS=52
    DISPLAY_SCROLL_ADD=53
    DISPLAY_SCROLL_GET=54
    DISPLAY_TEXT=55
    DIV_VAR=56
    DROP_DETECT_LOOP=57
    FILE_CLOSE=58
    FILE_OPEN=59
    FLOAT_TO_INT=60
    FLOAT_TO_INT_ROUND=61
    GET_GPIO=62
    GET_GPIO_MSK=63
    GET_PROGRESS=64
    GET_TIME=65
    HIBERNATE=66
    I2C_CONFIG=67
    I2C_READ=68
    I2C_READ_BYTE=69
    I2C_WRITE=70
    I2C_WRITE_BYTE=71
    I2C_WRITE_READ=72
    INT_TO_FLOAT=73
    LINEAR_FIT=74
    LOAD_SAVED_END=75
    LOAD_SAVED_START=76
    LOAD_SAVED_STR=77
    LOAD_SAVED_VAR=78
    LOG_VAR=79
    MEAN=80
    MEAS=81
    MEAS_FAST_CA=82
    MEAS_FAST_CV=83
    MEAS_MS_EIS=84
    MEAS_SCP=85
    MOD_VAR=86
    MUL_VAR=87
    MUX_CONFIG=88
    MUX_GET_CHANNEL_COUNT=89
    MUX_SET_CHANNEL=90
    NOTIFY_LED=91
    PCK_ADD=92
    PCK_END=93
    PCK_START=94
    PEAK_DETECT=95
    POW_VAR=96
    QR_SCAN=97
    RTC_GET=98
    SAVE_STR=99
    SAVE_VAR=100
    SEND_STRING=101
    SET_ACQUISITION_FRAC=102
    SET_ACQUISITION_FRAC_AUTOADJUST=103
    SET_AUTORANGING=104
    SET_BIPOT_MODE=105
    SET_BIPOT_POTENTIAL=106
    SET_CHANNEL_SYNC=107
    SET_CR=108
    SET_E=109
    SET_E_AUX=110
    SET_GPIO=111
    SET_GPIO_CFG=112
    SET_GPIO_MSK=113
    SET_GPIO_PULLUP=114
    SET_I=115
    SET_INT=116
    SET_IR_COMP=117
    SET_MAX_BANDWIDTH=118
    SET_PGSTAT_CHAN=119
    SET_PGSTAT_MODE=120
    SET_POLY_WE_MODE=121
    SET_POT_RANGE=122
    SET_RANGE=123
    SET_RANGE_MINMAX=124
    SET_SCAN_DIR=125
    SET_SCRIPT_OUTPUT=126
    SMOOTH=127
    STORE_STR=128
    STORE_VAR=129
    STR=130
    SUB_VAR=131
    SUBARRAY=132
    TIMER_GET=133
    TIMER_START=134
    TRIM_ENABLE=135
    WAIT=136
    EQ=137
    NE=138
    GE=139
    LE=140
    GT=141
    LT=142
    AND=143
    OR=144
    LPAREN=145
    RPAREN=146
    LBRACK=147
    RBRACK=148
    FSTRING_START=149
    STRING_LITERAL=150
    INVALID_STRING_LITERAL=151
    INTEGER_LITERAL=152
    FLOAT_LITERAL=153
    INVALID_NUMERIC_LITERAL=154
    IDENTIFIER=155
    COMMENT=156
    WS=157
    NEWLINE=158
    UNRECOGNIZED_CHAR=159
    FSTRING_TEXT=160
    FSTRING_ESCAPE=161
    FSTRING_INTERP_START=162
    FSTRING_END=163
    FSTRING_IDENTIFIER=164
    FSTRING_LBRACK=165
    FSTRING_RBRACK=166
    FSTRING_INTEGER=167
    FSTRING_INTERP_END=168
    FSTRING_WS_INTERP=169

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class SourceFileContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(MethodScriptParser.EOF, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.StatementContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.StatementContext,i)


        def commentLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.CommentLineContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.CommentLineContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_sourceFile

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSourceFile" ):
                listener.enterSourceFile(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSourceFile" ):
                listener.exitSourceFile(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSourceFile" ):
                return visitor.visitSourceFile(self)
            else:
                return visitor.visitChildren(self)




    def sourceFile(self):

        localctx = MethodScriptParser.SourceFileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_sourceFile)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 58
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2450239672266260850) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -103079245825) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 268435967) != 0):
                self.state = 56
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136]:
                    self.state = 54
                    self.statement()
                    pass
                elif token in [156]:
                    self.state = 55
                    self.commentLine()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 60
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 61
            self.match(MethodScriptParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variableDeclaration(self):
            return self.getTypedRuleContext(MethodScriptParser.VariableDeclarationContext,0)


        def arrayDeclaration(self):
            return self.getTypedRuleContext(MethodScriptParser.ArrayDeclarationContext,0)


        def stringDeclaration(self):
            return self.getTypedRuleContext(MethodScriptParser.StringDeclarationContext,0)


        def commandCall(self):
            return self.getTypedRuleContext(MethodScriptParser.CommandCallContext,0)


        def ifStatement(self):
            return self.getTypedRuleContext(MethodScriptParser.IfStatementContext,0)


        def loopStatement(self):
            return self.getTypedRuleContext(MethodScriptParser.LoopStatementContext,0)


        def breakStatement(self):
            return self.getTypedRuleContext(MethodScriptParser.BreakStatementContext,0)


        def tag(self):
            return self.getTypedRuleContext(MethodScriptParser.TagContext,0)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = MethodScriptParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.state = 71
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 63
                self.variableDeclaration()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 64
                self.arrayDeclaration()
                pass
            elif token in [130]:
                self.enterOuterAlt(localctx, 3)
                self.state = 65
                self.stringDeclaration()
                pass
            elif token in [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 131, 132, 133, 134, 135, 136]:
                self.enterOuterAlt(localctx, 4)
                self.state = 66
                self.commandCall()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 5)
                self.state = 67
                self.ifStatement()
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 6)
                self.state = 68
                self.loopStatement()
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 7)
                self.state = 69
                self.breakStatement()
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 8)
                self.state = 70
                self.tag()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommentLineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_commentLine

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommentLine" ):
                listener.enterCommentLine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommentLine" ):
                listener.exitCommentLine(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommentLine" ):
                return visitor.visitCommentLine(self)
            else:
                return visitor.visitChildren(self)




    def commentLine(self):

        localctx = MethodScriptParser.CommentLineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_commentLine)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(MethodScriptParser.COMMENT)
            self.state = 74
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableDeclarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.name = None # Token

        def VAR(self):
            return self.getToken(MethodScriptParser.VAR, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def IDENTIFIER(self):
            return self.getToken(MethodScriptParser.IDENTIFIER, 0)

        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_variableDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariableDeclaration" ):
                listener.enterVariableDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariableDeclaration" ):
                listener.exitVariableDeclaration(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariableDeclaration" ):
                return visitor.visitVariableDeclaration(self)
            else:
                return visitor.visitChildren(self)




    def variableDeclaration(self):

        localctx = MethodScriptParser.VariableDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_variableDeclaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            self.match(MethodScriptParser.VAR)
            self.state = 77
            localctx.name = self.match(MethodScriptParser.IDENTIFIER)
            self.state = 79
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 78
                self.match(MethodScriptParser.COMMENT)


            self.state = 81
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayDeclarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.name = None # Token
            self.size = None # Token

        def ARRAY(self):
            return self.getToken(MethodScriptParser.ARRAY, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.IDENTIFIER)
            else:
                return self.getToken(MethodScriptParser.IDENTIFIER, i)

        def INTEGER_LITERAL(self):
            return self.getToken(MethodScriptParser.INTEGER_LITERAL, 0)

        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_arrayDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArrayDeclaration" ):
                listener.enterArrayDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArrayDeclaration" ):
                listener.exitArrayDeclaration(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArrayDeclaration" ):
                return visitor.visitArrayDeclaration(self)
            else:
                return visitor.visitChildren(self)




    def arrayDeclaration(self):

        localctx = MethodScriptParser.ArrayDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_arrayDeclaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(MethodScriptParser.ARRAY)
            self.state = 84
            localctx.name = self.match(MethodScriptParser.IDENTIFIER)
            self.state = 85
            localctx.size = self._input.LT(1)
            _la = self._input.LA(1)
            if not(_la==152 or _la==155):
                localctx.size = self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 87
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 86
                self.match(MethodScriptParser.COMMENT)


            self.state = 89
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringDeclarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.name = None # Token

        def STR(self):
            return self.getToken(MethodScriptParser.STR, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def IDENTIFIER(self):
            return self.getToken(MethodScriptParser.IDENTIFIER, 0)

        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_stringDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStringDeclaration" ):
                listener.enterStringDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStringDeclaration" ):
                listener.exitStringDeclaration(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStringDeclaration" ):
                return visitor.visitStringDeclaration(self)
            else:
                return visitor.visitChildren(self)




    def stringDeclaration(self):

        localctx = MethodScriptParser.StringDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_stringDeclaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            self.match(MethodScriptParser.STR)
            self.state = 92
            localctx.name = self.match(MethodScriptParser.IDENTIFIER)
            self.state = 94
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 93
                self.match(MethodScriptParser.COMMENT)


            self.state = 96
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IfStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.condition = None # ConditionalExpressionContext

        def IF(self):
            return self.getToken(MethodScriptParser.IF, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.NEWLINE)
            else:
                return self.getToken(MethodScriptParser.NEWLINE, i)

        def ENDIF(self):
            return self.getToken(MethodScriptParser.ENDIF, 0)

        def conditionalExpression(self):
            return self.getTypedRuleContext(MethodScriptParser.ConditionalExpressionContext,0)


        def COMMENT(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.COMMENT)
            else:
                return self.getToken(MethodScriptParser.COMMENT, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.StatementContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.StatementContext,i)


        def commentLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.CommentLineContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.CommentLineContext,i)


        def elseifClause(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.ElseifClauseContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.ElseifClauseContext,i)


        def elseClause(self):
            return self.getTypedRuleContext(MethodScriptParser.ElseClauseContext,0)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_ifStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIfStatement" ):
                listener.enterIfStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIfStatement" ):
                listener.exitIfStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfStatement" ):
                return visitor.visitIfStatement(self)
            else:
                return visitor.visitChildren(self)




    def ifStatement(self):

        localctx = MethodScriptParser.IfStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_ifStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 98
            self.match(MethodScriptParser.IF)
            self.state = 99
            localctx.condition = self.conditionalExpression()
            self.state = 101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 100
                self.match(MethodScriptParser.COMMENT)


            self.state = 103
            self.match(MethodScriptParser.NEWLINE)
            self.state = 108
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2450239672266260850) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -103079245825) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 268435967) != 0):
                self.state = 106
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136]:
                    self.state = 104
                    self.statement()
                    pass
                elif token in [156]:
                    self.state = 105
                    self.commentLine()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 110
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 114
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 111
                self.elseifClause()
                self.state = 116
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 118
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 117
                self.elseClause()


            self.state = 120
            self.match(MethodScriptParser.ENDIF)
            self.state = 122
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 121
                self.match(MethodScriptParser.COMMENT)


            self.state = 124
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElseifClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.condition = None # ConditionalExpressionContext

        def ELSEIF(self):
            return self.getToken(MethodScriptParser.ELSEIF, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def conditionalExpression(self):
            return self.getTypedRuleContext(MethodScriptParser.ConditionalExpressionContext,0)


        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.StatementContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.StatementContext,i)


        def commentLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.CommentLineContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.CommentLineContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_elseifClause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterElseifClause" ):
                listener.enterElseifClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitElseifClause" ):
                listener.exitElseifClause(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElseifClause" ):
                return visitor.visitElseifClause(self)
            else:
                return visitor.visitChildren(self)




    def elseifClause(self):

        localctx = MethodScriptParser.ElseifClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_elseifClause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 126
            self.match(MethodScriptParser.ELSEIF)
            self.state = 127
            localctx.condition = self.conditionalExpression()
            self.state = 129
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 128
                self.match(MethodScriptParser.COMMENT)


            self.state = 131
            self.match(MethodScriptParser.NEWLINE)
            self.state = 136
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2450239672266260850) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -103079245825) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 268435967) != 0):
                self.state = 134
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136]:
                    self.state = 132
                    self.statement()
                    pass
                elif token in [156]:
                    self.state = 133
                    self.commentLine()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 138
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElseClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ELSE(self):
            return self.getToken(MethodScriptParser.ELSE, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.StatementContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.StatementContext,i)


        def commentLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.CommentLineContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.CommentLineContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_elseClause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterElseClause" ):
                listener.enterElseClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitElseClause" ):
                listener.exitElseClause(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElseClause" ):
                return visitor.visitElseClause(self)
            else:
                return visitor.visitChildren(self)




    def elseClause(self):

        localctx = MethodScriptParser.ElseClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_elseClause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 139
            self.match(MethodScriptParser.ELSE)
            self.state = 141
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 140
                self.match(MethodScriptParser.COMMENT)


            self.state = 143
            self.match(MethodScriptParser.NEWLINE)
            self.state = 148
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2450239672266260850) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -103079245825) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 268435967) != 0):
                self.state = 146
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136]:
                    self.state = 144
                    self.statement()
                    pass
                elif token in [156]:
                    self.state = 145
                    self.commentLine()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 150
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.condition = None # ConditionalExpressionContext

        def LOOP(self):
            return self.getToken(MethodScriptParser.LOOP, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.NEWLINE)
            else:
                return self.getToken(MethodScriptParser.NEWLINE, i)

        def ENDLOOP(self):
            return self.getToken(MethodScriptParser.ENDLOOP, 0)

        def conditionalExpression(self):
            return self.getTypedRuleContext(MethodScriptParser.ConditionalExpressionContext,0)


        def COMMENT(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.COMMENT)
            else:
                return self.getToken(MethodScriptParser.COMMENT, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.StatementContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.StatementContext,i)


        def commentLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.CommentLineContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.CommentLineContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_loopStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLoopStatement" ):
                listener.enterLoopStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLoopStatement" ):
                listener.exitLoopStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoopStatement" ):
                return visitor.visitLoopStatement(self)
            else:
                return visitor.visitChildren(self)




    def loopStatement(self):

        localctx = MethodScriptParser.LoopStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_loopStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 151
            self.match(MethodScriptParser.LOOP)
            self.state = 152
            localctx.condition = self.conditionalExpression()
            self.state = 154
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 153
                self.match(MethodScriptParser.COMMENT)


            self.state = 156
            self.match(MethodScriptParser.NEWLINE)
            self.state = 161
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2450239672266260850) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -103079245825) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 268435967) != 0):
                self.state = 159
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136]:
                    self.state = 157
                    self.statement()
                    pass
                elif token in [156]:
                    self.state = 158
                    self.commentLine()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 163
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 164
            self.match(MethodScriptParser.ENDLOOP)
            self.state = 166
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 165
                self.match(MethodScriptParser.COMMENT)


            self.state = 168
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BreakStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BREAKLOOP(self):
            return self.getToken(MethodScriptParser.BREAKLOOP, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_breakStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBreakStatement" ):
                listener.enterBreakStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBreakStatement" ):
                listener.exitBreakStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBreakStatement" ):
                return visitor.visitBreakStatement(self)
            else:
                return visitor.visitChildren(self)




    def breakStatement(self):

        localctx = MethodScriptParser.BreakStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_breakStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 170
            self.match(MethodScriptParser.BREAKLOOP)
            self.state = 172
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 171
                self.match(MethodScriptParser.COMMENT)


            self.state = 174
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TagContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ON_FINISHED(self):
            return self.getToken(MethodScriptParser.ON_FINISHED, 0)

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_tag

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTag" ):
                listener.enterTag(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTag" ):
                listener.exitTag(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTag" ):
                return visitor.visitTag(self)
            else:
                return visitor.visitChildren(self)




    def tag(self):

        localctx = MethodScriptParser.TagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_tag)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 176
            self.match(MethodScriptParser.ON_FINISHED)
            self.state = 178
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 177
                self.match(MethodScriptParser.COMMENT)


            self.state = 180
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionalExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.left = None # OperandContext
            self.right = None # OperandContext

        def operator(self):
            return self.getTypedRuleContext(MethodScriptParser.OperatorContext,0)


        def operand(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.OperandContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.OperandContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_conditionalExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConditionalExpression" ):
                listener.enterConditionalExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConditionalExpression" ):
                listener.exitConditionalExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConditionalExpression" ):
                return visitor.visitConditionalExpression(self)
            else:
                return visitor.visitChildren(self)




    def conditionalExpression(self):

        localctx = MethodScriptParser.ConditionalExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_conditionalExpression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 182
            localctx.left = self.operand()
            self.state = 183
            self.operator()
            self.state = 184
            localctx.right = self.operand()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OperatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EQ(self):
            return self.getToken(MethodScriptParser.EQ, 0)

        def NE(self):
            return self.getToken(MethodScriptParser.NE, 0)

        def GE(self):
            return self.getToken(MethodScriptParser.GE, 0)

        def LE(self):
            return self.getToken(MethodScriptParser.LE, 0)

        def GT(self):
            return self.getToken(MethodScriptParser.GT, 0)

        def LT(self):
            return self.getToken(MethodScriptParser.LT, 0)

        def AND(self):
            return self.getToken(MethodScriptParser.AND, 0)

        def OR(self):
            return self.getToken(MethodScriptParser.OR, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_operator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperator" ):
                listener.enterOperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperator" ):
                listener.exitOperator(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOperator" ):
                return visitor.visitOperator(self)
            else:
                return visitor.visitChildren(self)




    def operator(self):

        localctx = MethodScriptParser.OperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 186
            _la = self._input.LA(1)
            if not(((((_la - 137)) & ~0x3f) == 0 and ((1 << (_la - 137)) & 255) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OperandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(MethodScriptParser.IDENTIFIER, 0)

        def arrayAccess(self):
            return self.getTypedRuleContext(MethodScriptParser.ArrayAccessContext,0)


        def literal(self):
            return self.getTypedRuleContext(MethodScriptParser.LiteralContext,0)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_operand

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperand" ):
                listener.enterOperand(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperand" ):
                listener.exitOperand(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOperand" ):
                return visitor.visitOperand(self)
            else:
                return visitor.visitChildren(self)




    def operand(self):

        localctx = MethodScriptParser.OperandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_operand)
        try:
            self.state = 191
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,24,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 188
                self.match(MethodScriptParser.IDENTIFIER)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 189
                self.arrayAccess()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 190
                self.literal()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayAccessContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.array = None # Token
            self.index = None # Token

        def LBRACK(self):
            return self.getToken(MethodScriptParser.LBRACK, 0)

        def RBRACK(self):
            return self.getToken(MethodScriptParser.RBRACK, 0)

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.IDENTIFIER)
            else:
                return self.getToken(MethodScriptParser.IDENTIFIER, i)

        def INTEGER_LITERAL(self):
            return self.getToken(MethodScriptParser.INTEGER_LITERAL, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_arrayAccess

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArrayAccess" ):
                listener.enterArrayAccess(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArrayAccess" ):
                listener.exitArrayAccess(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArrayAccess" ):
                return visitor.visitArrayAccess(self)
            else:
                return visitor.visitChildren(self)




    def arrayAccess(self):

        localctx = MethodScriptParser.ArrayAccessContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_arrayAccess)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 193
            localctx.array = self.match(MethodScriptParser.IDENTIFIER)
            self.state = 194
            self.match(MethodScriptParser.LBRACK)
            self.state = 195
            localctx.index = self._input.LT(1)
            _la = self._input.LA(1)
            if not(_la==152 or _la==155):
                localctx.index = self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 196
            self.match(MethodScriptParser.RBRACK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommandCallContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def simpleCommand(self):
            return self.getTypedRuleContext(MethodScriptParser.SimpleCommandContext,0)


        def measurementLoop(self):
            return self.getTypedRuleContext(MethodScriptParser.MeasurementLoopContext,0)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_commandCall

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommandCall" ):
                listener.enterCommandCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommandCall" ):
                listener.exitCommandCall(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommandCall" ):
                return visitor.visitCommandCall(self)
            else:
                return visitor.visitChildren(self)




    def commandCall(self):

        localctx = MethodScriptParser.CommandCallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_commandCall)
        try:
            self.state = 200
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 131, 132, 133, 134, 135, 136]:
                self.enterOuterAlt(localctx, 1)
                self.state = 198
                self.simpleCommand()
                pass
            elif token in [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]:
                self.enterOuterAlt(localctx, 2)
                self.state = 199
                self.measurementLoop()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SimpleCommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.command = None # CommandNameContext

        def NEWLINE(self):
            return self.getToken(MethodScriptParser.NEWLINE, 0)

        def commandName(self):
            return self.getTypedRuleContext(MethodScriptParser.CommandNameContext,0)


        def argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.ArgumentContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.ArgumentContext,i)


        def optionalArgumentBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.OptionalArgumentBlockContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.OptionalArgumentBlockContext,i)


        def COMMENT(self):
            return self.getToken(MethodScriptParser.COMMENT, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_simpleCommand

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSimpleCommand" ):
                listener.enterSimpleCommand(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSimpleCommand" ):
                listener.exitSimpleCommand(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSimpleCommand" ):
                return visitor.visitSimpleCommand(self)
            else:
                return visitor.visitChildren(self)




    def simpleCommand(self):

        localctx = MethodScriptParser.SimpleCommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_simpleCommand)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 202
            localctx.command = self.commandName()
            self.state = 206
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,26,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 203
                    self.argument() 
                self.state = 208
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,26,self._ctx)

            self.state = 212
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==155:
                self.state = 209
                self.optionalArgumentBlock()
                self.state = 214
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 216
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 215
                self.match(MethodScriptParser.COMMENT)


            self.state = 218
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MeasurementLoopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.command = None # MeasurementCommandContext

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.NEWLINE)
            else:
                return self.getToken(MethodScriptParser.NEWLINE, i)

        def ENDLOOP(self):
            return self.getToken(MethodScriptParser.ENDLOOP, 0)

        def measurementCommand(self):
            return self.getTypedRuleContext(MethodScriptParser.MeasurementCommandContext,0)


        def argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.ArgumentContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.ArgumentContext,i)


        def optionalArgumentBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.OptionalArgumentBlockContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.OptionalArgumentBlockContext,i)


        def COMMENT(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.COMMENT)
            else:
                return self.getToken(MethodScriptParser.COMMENT, i)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.StatementContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.StatementContext,i)


        def commentLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.CommentLineContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.CommentLineContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_measurementLoop

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMeasurementLoop" ):
                listener.enterMeasurementLoop(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMeasurementLoop" ):
                listener.exitMeasurementLoop(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMeasurementLoop" ):
                return visitor.visitMeasurementLoop(self)
            else:
                return visitor.visitChildren(self)




    def measurementLoop(self):

        localctx = MethodScriptParser.MeasurementLoopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_measurementLoop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            localctx.command = self.measurementCommand()
            self.state = 224
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,29,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 221
                    self.argument() 
                self.state = 226
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,29,self._ctx)

            self.state = 230
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==155:
                self.state = 227
                self.optionalArgumentBlock()
                self.state = 232
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 234
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 233
                self.match(MethodScriptParser.COMMENT)


            self.state = 236
            self.match(MethodScriptParser.NEWLINE)
            self.state = 241
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2450239672266260850) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -103079245825) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 268435967) != 0):
                self.state = 239
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1, 2, 3, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136]:
                    self.state = 237
                    self.statement()
                    pass
                elif token in [156]:
                    self.state = 238
                    self.commentLine()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 243
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 244
            self.match(MethodScriptParser.ENDLOOP)
            self.state = 246
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==156:
                self.state = 245
                self.match(MethodScriptParser.COMMENT)


            self.state = 248
            self.match(MethodScriptParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OptionalArgumentBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.name = None # Token

        def LPAREN(self):
            return self.getToken(MethodScriptParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(MethodScriptParser.RPAREN, 0)

        def IDENTIFIER(self):
            return self.getToken(MethodScriptParser.IDENTIFIER, 0)

        def argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.ArgumentContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.ArgumentContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_optionalArgumentBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOptionalArgumentBlock" ):
                listener.enterOptionalArgumentBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOptionalArgumentBlock" ):
                listener.exitOptionalArgumentBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOptionalArgumentBlock" ):
                return visitor.visitOptionalArgumentBlock(self)
            else:
                return visitor.visitChildren(self)




    def optionalArgumentBlock(self):

        localctx = MethodScriptParser.OptionalArgumentBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_optionalArgumentBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 250
            localctx.name = self.match(MethodScriptParser.IDENTIFIER)
            self.state = 251
            self.match(MethodScriptParser.LPAREN)
            self.state = 255
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 149)) & ~0x3f) == 0 and ((1 << (_la - 149)) & 127) != 0):
                self.state = 252
                self.argument()
                self.state = 257
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 258
            self.match(MethodScriptParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MeasurementCommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MEAS_LOOP_CA(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_CA, 0)

        def MEAS_LOOP_CA_ALT_MUX(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_CA_ALT_MUX, 0)

        def MEAS_LOOP_CV(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_CV, 0)

        def MEAS_LOOP_LSV(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_LSV, 0)

        def MEAS_LOOP_DPV(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_DPV, 0)

        def MEAS_LOOP_SWV(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_SWV, 0)

        def MEAS_LOOP_NPV(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_NPV, 0)

        def MEAS_LOOP_PAD(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_PAD, 0)

        def MEAS_LOOP_OCP(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_OCP, 0)

        def MEAS_LOOP_OCP_ALT_MUX(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_OCP_ALT_MUX, 0)

        def MEAS_LOOP_CP(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_CP, 0)

        def MEAS_LOOP_CP_ALT_MUX(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_CP_ALT_MUX, 0)

        def MEAS_LOOP_LSP(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_LSP, 0)

        def MEAS_LOOP_ACV(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_ACV, 0)

        def MEAS_LOOP_EIS(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_EIS, 0)

        def MEAS_LOOP_EIS_DUAL(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_EIS_DUAL, 0)

        def MEAS_LOOP_GEIS(self):
            return self.getToken(MethodScriptParser.MEAS_LOOP_GEIS, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_measurementCommand

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMeasurementCommand" ):
                listener.enterMeasurementCommand(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMeasurementCommand" ):
                listener.exitMeasurementCommand(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMeasurementCommand" ):
                return visitor.visitMeasurementCommand(self)
            else:
                return visitor.visitChildren(self)




    def measurementCommand(self):

        localctx = MethodScriptParser.MeasurementCommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_measurementCommand)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 260
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 268433408) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommandNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ABORT(self):
            return self.getToken(MethodScriptParser.ABORT, 0)

        def ADD_VAR(self):
            return self.getToken(MethodScriptParser.ADD_VAR, 0)

        def ALTER_VARTYPE(self):
            return self.getToken(MethodScriptParser.ALTER_VARTYPE, 0)

        def ARRAY_GET(self):
            return self.getToken(MethodScriptParser.ARRAY_GET, 0)

        def ARRAY_SET(self):
            return self.getToken(MethodScriptParser.ARRAY_SET, 0)

        def AWAIT_INT(self):
            return self.getToken(MethodScriptParser.AWAIT_INT, 0)

        def BATTERY_PERC(self):
            return self.getToken(MethodScriptParser.BATTERY_PERC, 0)

        def BEEP(self):
            return self.getToken(MethodScriptParser.BEEP, 0)

        def BIT_AND_VAR(self):
            return self.getToken(MethodScriptParser.BIT_AND_VAR, 0)

        def BIT_INV_VAR(self):
            return self.getToken(MethodScriptParser.BIT_INV_VAR, 0)

        def BIT_LSL_VAR(self):
            return self.getToken(MethodScriptParser.BIT_LSL_VAR, 0)

        def BIT_LSR_VAR(self):
            return self.getToken(MethodScriptParser.BIT_LSR_VAR, 0)

        def BIT_OR_VAR(self):
            return self.getToken(MethodScriptParser.BIT_OR_VAR, 0)

        def BIT_XOR_VAR(self):
            return self.getToken(MethodScriptParser.BIT_XOR_VAR, 0)

        def CELL_OFF(self):
            return self.getToken(MethodScriptParser.CELL_OFF, 0)

        def CELL_ON(self):
            return self.getToken(MethodScriptParser.CELL_ON, 0)

        def COPY_VAR(self):
            return self.getToken(MethodScriptParser.COPY_VAR, 0)

        def DISPLAY_BTNS(self):
            return self.getToken(MethodScriptParser.DISPLAY_BTNS, 0)

        def DISPLAY_CLEAR(self):
            return self.getToken(MethodScriptParser.DISPLAY_CLEAR, 0)

        def DISPLAY_DRAW(self):
            return self.getToken(MethodScriptParser.DISPLAY_DRAW, 0)

        def DISPLAY_ICON(self):
            return self.getToken(MethodScriptParser.DISPLAY_ICON, 0)

        def DISPLAY_INP_NUM(self):
            return self.getToken(MethodScriptParser.DISPLAY_INP_NUM, 0)

        def DISPLAY_KEYBOARD(self):
            return self.getToken(MethodScriptParser.DISPLAY_KEYBOARD, 0)

        def DISPLAY_PROGRESS(self):
            return self.getToken(MethodScriptParser.DISPLAY_PROGRESS, 0)

        def DISPLAY_SCROLL_ADD(self):
            return self.getToken(MethodScriptParser.DISPLAY_SCROLL_ADD, 0)

        def DISPLAY_SCROLL_GET(self):
            return self.getToken(MethodScriptParser.DISPLAY_SCROLL_GET, 0)

        def DISPLAY_TEXT(self):
            return self.getToken(MethodScriptParser.DISPLAY_TEXT, 0)

        def DIV_VAR(self):
            return self.getToken(MethodScriptParser.DIV_VAR, 0)

        def FILE_CLOSE(self):
            return self.getToken(MethodScriptParser.FILE_CLOSE, 0)

        def FILE_OPEN(self):
            return self.getToken(MethodScriptParser.FILE_OPEN, 0)

        def FLOAT_TO_INT(self):
            return self.getToken(MethodScriptParser.FLOAT_TO_INT, 0)

        def GET_GPIO(self):
            return self.getToken(MethodScriptParser.GET_GPIO, 0)

        def GET_GPIO_MSK(self):
            return self.getToken(MethodScriptParser.GET_GPIO_MSK, 0)

        def GET_PROGRESS(self):
            return self.getToken(MethodScriptParser.GET_PROGRESS, 0)

        def GET_TIME(self):
            return self.getToken(MethodScriptParser.GET_TIME, 0)

        def HIBERNATE(self):
            return self.getToken(MethodScriptParser.HIBERNATE, 0)

        def I2C_CONFIG(self):
            return self.getToken(MethodScriptParser.I2C_CONFIG, 0)

        def I2C_READ(self):
            return self.getToken(MethodScriptParser.I2C_READ, 0)

        def I2C_READ_BYTE(self):
            return self.getToken(MethodScriptParser.I2C_READ_BYTE, 0)

        def I2C_WRITE(self):
            return self.getToken(MethodScriptParser.I2C_WRITE, 0)

        def I2C_WRITE_BYTE(self):
            return self.getToken(MethodScriptParser.I2C_WRITE_BYTE, 0)

        def I2C_WRITE_READ(self):
            return self.getToken(MethodScriptParser.I2C_WRITE_READ, 0)

        def INT_TO_FLOAT(self):
            return self.getToken(MethodScriptParser.INT_TO_FLOAT, 0)

        def LINEAR_FIT(self):
            return self.getToken(MethodScriptParser.LINEAR_FIT, 0)

        def LOG_VAR(self):
            return self.getToken(MethodScriptParser.LOG_VAR, 0)

        def MEAN(self):
            return self.getToken(MethodScriptParser.MEAN, 0)

        def MEAS(self):
            return self.getToken(MethodScriptParser.MEAS, 0)

        def MEAS_FAST_CA(self):
            return self.getToken(MethodScriptParser.MEAS_FAST_CA, 0)

        def MEAS_FAST_CV(self):
            return self.getToken(MethodScriptParser.MEAS_FAST_CV, 0)

        def MEAS_MS_EIS(self):
            return self.getToken(MethodScriptParser.MEAS_MS_EIS, 0)

        def MEAS_SCP(self):
            return self.getToken(MethodScriptParser.MEAS_SCP, 0)

        def MOD_VAR(self):
            return self.getToken(MethodScriptParser.MOD_VAR, 0)

        def MUL_VAR(self):
            return self.getToken(MethodScriptParser.MUL_VAR, 0)

        def MUX_CONFIG(self):
            return self.getToken(MethodScriptParser.MUX_CONFIG, 0)

        def MUX_GET_CHANNEL_COUNT(self):
            return self.getToken(MethodScriptParser.MUX_GET_CHANNEL_COUNT, 0)

        def MUX_SET_CHANNEL(self):
            return self.getToken(MethodScriptParser.MUX_SET_CHANNEL, 0)

        def NOTIFY_LED(self):
            return self.getToken(MethodScriptParser.NOTIFY_LED, 0)

        def PCK_ADD(self):
            return self.getToken(MethodScriptParser.PCK_ADD, 0)

        def PCK_END(self):
            return self.getToken(MethodScriptParser.PCK_END, 0)

        def PCK_START(self):
            return self.getToken(MethodScriptParser.PCK_START, 0)

        def PEAK_DETECT(self):
            return self.getToken(MethodScriptParser.PEAK_DETECT, 0)

        def POW_VAR(self):
            return self.getToken(MethodScriptParser.POW_VAR, 0)

        def QR_SCAN(self):
            return self.getToken(MethodScriptParser.QR_SCAN, 0)

        def RTC_GET(self):
            return self.getToken(MethodScriptParser.RTC_GET, 0)

        def SEND_STRING(self):
            return self.getToken(MethodScriptParser.SEND_STRING, 0)

        def SET_ACQUISITION_FRAC(self):
            return self.getToken(MethodScriptParser.SET_ACQUISITION_FRAC, 0)

        def SET_ACQUISITION_FRAC_AUTOADJUST(self):
            return self.getToken(MethodScriptParser.SET_ACQUISITION_FRAC_AUTOADJUST, 0)

        def SET_AUTORANGING(self):
            return self.getToken(MethodScriptParser.SET_AUTORANGING, 0)

        def SET_BIPOT_MODE(self):
            return self.getToken(MethodScriptParser.SET_BIPOT_MODE, 0)

        def SET_BIPOT_POTENTIAL(self):
            return self.getToken(MethodScriptParser.SET_BIPOT_POTENTIAL, 0)

        def SET_CHANNEL_SYNC(self):
            return self.getToken(MethodScriptParser.SET_CHANNEL_SYNC, 0)

        def SET_E(self):
            return self.getToken(MethodScriptParser.SET_E, 0)

        def SET_E_AUX(self):
            return self.getToken(MethodScriptParser.SET_E_AUX, 0)

        def SET_GPIO(self):
            return self.getToken(MethodScriptParser.SET_GPIO, 0)

        def SET_GPIO_CFG(self):
            return self.getToken(MethodScriptParser.SET_GPIO_CFG, 0)

        def SET_GPIO_MSK(self):
            return self.getToken(MethodScriptParser.SET_GPIO_MSK, 0)

        def SET_GPIO_PULLUP(self):
            return self.getToken(MethodScriptParser.SET_GPIO_PULLUP, 0)

        def SET_I(self):
            return self.getToken(MethodScriptParser.SET_I, 0)

        def SET_INT(self):
            return self.getToken(MethodScriptParser.SET_INT, 0)

        def SET_IR_COMP(self):
            return self.getToken(MethodScriptParser.SET_IR_COMP, 0)

        def SET_MAX_BANDWIDTH(self):
            return self.getToken(MethodScriptParser.SET_MAX_BANDWIDTH, 0)

        def SET_PGSTAT_CHAN(self):
            return self.getToken(MethodScriptParser.SET_PGSTAT_CHAN, 0)

        def SET_PGSTAT_MODE(self):
            return self.getToken(MethodScriptParser.SET_PGSTAT_MODE, 0)

        def SET_POLY_WE_MODE(self):
            return self.getToken(MethodScriptParser.SET_POLY_WE_MODE, 0)

        def SET_POT_RANGE(self):
            return self.getToken(MethodScriptParser.SET_POT_RANGE, 0)

        def SET_RANGE(self):
            return self.getToken(MethodScriptParser.SET_RANGE, 0)

        def SET_RANGE_MINMAX(self):
            return self.getToken(MethodScriptParser.SET_RANGE_MINMAX, 0)

        def SET_SCAN_DIR(self):
            return self.getToken(MethodScriptParser.SET_SCAN_DIR, 0)

        def SET_CR(self):
            return self.getToken(MethodScriptParser.SET_CR, 0)

        def SET_SCRIPT_OUTPUT(self):
            return self.getToken(MethodScriptParser.SET_SCRIPT_OUTPUT, 0)

        def SMOOTH(self):
            return self.getToken(MethodScriptParser.SMOOTH, 0)

        def STORE_STR(self):
            return self.getToken(MethodScriptParser.STORE_STR, 0)

        def STORE_VAR(self):
            return self.getToken(MethodScriptParser.STORE_VAR, 0)

        def SUBARRAY(self):
            return self.getToken(MethodScriptParser.SUBARRAY, 0)

        def SUB_VAR(self):
            return self.getToken(MethodScriptParser.SUB_VAR, 0)

        def TIMER_GET(self):
            return self.getToken(MethodScriptParser.TIMER_GET, 0)

        def TIMER_START(self):
            return self.getToken(MethodScriptParser.TIMER_START, 0)

        def TRIM_ENABLE(self):
            return self.getToken(MethodScriptParser.TRIM_ENABLE, 0)

        def WAIT(self):
            return self.getToken(MethodScriptParser.WAIT, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_commandName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommandName" ):
                listener.enterCommandName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommandName" ):
                listener.exitCommandName(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommandName" ):
                return visitor.visitCommandName(self)
            else:
                return visitor.visitChildren(self)




    def commandName(self):

        localctx = MethodScriptParser.CommandNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_commandName)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 262
            _la = self._input.LA(1)
            if not(((((_la - 28)) & ~0x3f) == 0 and ((1 << (_la - 28)) & -2111071453184001) != 0) or ((((_la - 92)) & ~0x3f) == 0 and ((1 << (_la - 92)) & 34909494181503) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def literal(self):
            return self.getTypedRuleContext(MethodScriptParser.LiteralContext,0)


        def IDENTIFIER(self):
            return self.getToken(MethodScriptParser.IDENTIFIER, 0)

        def arrayAccess(self):
            return self.getTypedRuleContext(MethodScriptParser.ArrayAccessContext,0)


        def INVALID_NUMERIC_LITERAL(self):
            return self.getToken(MethodScriptParser.INVALID_NUMERIC_LITERAL, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_argument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArgument" ):
                listener.enterArgument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArgument" ):
                listener.exitArgument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgument" ):
                return visitor.visitArgument(self)
            else:
                return visitor.visitChildren(self)




    def argument(self):

        localctx = MethodScriptParser.ArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_argument)
        try:
            self.state = 268
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,36,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 264
                self.literal()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 265
                self.match(MethodScriptParser.IDENTIFIER)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 266
                self.arrayAccess()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 267
                self.match(MethodScriptParser.INVALID_NUMERIC_LITERAL)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INTEGER_LITERAL(self):
            return self.getToken(MethodScriptParser.INTEGER_LITERAL, 0)

        def FLOAT_LITERAL(self):
            return self.getToken(MethodScriptParser.FLOAT_LITERAL, 0)

        def STRING_LITERAL(self):
            return self.getToken(MethodScriptParser.STRING_LITERAL, 0)

        def fstringLiteral(self):
            return self.getTypedRuleContext(MethodScriptParser.FstringLiteralContext,0)


        def INVALID_STRING_LITERAL(self):
            return self.getToken(MethodScriptParser.INVALID_STRING_LITERAL, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = MethodScriptParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_literal)
        try:
            self.state = 275
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [152]:
                self.enterOuterAlt(localctx, 1)
                self.state = 270
                self.match(MethodScriptParser.INTEGER_LITERAL)
                pass
            elif token in [153]:
                self.enterOuterAlt(localctx, 2)
                self.state = 271
                self.match(MethodScriptParser.FLOAT_LITERAL)
                pass
            elif token in [150]:
                self.enterOuterAlt(localctx, 3)
                self.state = 272
                self.match(MethodScriptParser.STRING_LITERAL)
                pass
            elif token in [149]:
                self.enterOuterAlt(localctx, 4)
                self.state = 273
                self.fstringLiteral()
                pass
            elif token in [151]:
                self.enterOuterAlt(localctx, 5)
                self.state = 274
                self.match(MethodScriptParser.INVALID_STRING_LITERAL)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FstringLiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FSTRING_START(self):
            return self.getToken(MethodScriptParser.FSTRING_START, 0)

        def FSTRING_END(self):
            return self.getToken(MethodScriptParser.FSTRING_END, 0)

        def fstringContent(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MethodScriptParser.FstringContentContext)
            else:
                return self.getTypedRuleContext(MethodScriptParser.FstringContentContext,i)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_fstringLiteral

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFstringLiteral" ):
                listener.enterFstringLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFstringLiteral" ):
                listener.exitFstringLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFstringLiteral" ):
                return visitor.visitFstringLiteral(self)
            else:
                return visitor.visitChildren(self)




    def fstringLiteral(self):

        localctx = MethodScriptParser.FstringLiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_fstringLiteral)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 277
            self.match(MethodScriptParser.FSTRING_START)
            self.state = 281
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 160)) & ~0x3f) == 0 and ((1 << (_la - 160)) & 7) != 0):
                self.state = 278
                self.fstringContent()
                self.state = 283
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 284
            self.match(MethodScriptParser.FSTRING_END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FstringContentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FSTRING_TEXT(self):
            return self.getToken(MethodScriptParser.FSTRING_TEXT, 0)

        def FSTRING_ESCAPE(self):
            return self.getToken(MethodScriptParser.FSTRING_ESCAPE, 0)

        def fstringInterpolation(self):
            return self.getTypedRuleContext(MethodScriptParser.FstringInterpolationContext,0)


        def getRuleIndex(self):
            return MethodScriptParser.RULE_fstringContent

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFstringContent" ):
                listener.enterFstringContent(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFstringContent" ):
                listener.exitFstringContent(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFstringContent" ):
                return visitor.visitFstringContent(self)
            else:
                return visitor.visitChildren(self)




    def fstringContent(self):

        localctx = MethodScriptParser.FstringContentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_fstringContent)
        try:
            self.state = 289
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [160]:
                self.enterOuterAlt(localctx, 1)
                self.state = 286
                self.match(MethodScriptParser.FSTRING_TEXT)
                pass
            elif token in [161]:
                self.enterOuterAlt(localctx, 2)
                self.state = 287
                self.match(MethodScriptParser.FSTRING_ESCAPE)
                pass
            elif token in [162]:
                self.enterOuterAlt(localctx, 3)
                self.state = 288
                self.fstringInterpolation()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FstringInterpolationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FSTRING_INTERP_START(self):
            return self.getToken(MethodScriptParser.FSTRING_INTERP_START, 0)

        def FSTRING_IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(MethodScriptParser.FSTRING_IDENTIFIER)
            else:
                return self.getToken(MethodScriptParser.FSTRING_IDENTIFIER, i)

        def FSTRING_INTERP_END(self):
            return self.getToken(MethodScriptParser.FSTRING_INTERP_END, 0)

        def FSTRING_LBRACK(self):
            return self.getToken(MethodScriptParser.FSTRING_LBRACK, 0)

        def FSTRING_RBRACK(self):
            return self.getToken(MethodScriptParser.FSTRING_RBRACK, 0)

        def FSTRING_INTEGER(self):
            return self.getToken(MethodScriptParser.FSTRING_INTEGER, 0)

        def getRuleIndex(self):
            return MethodScriptParser.RULE_fstringInterpolation

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFstringInterpolation" ):
                listener.enterFstringInterpolation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFstringInterpolation" ):
                listener.exitFstringInterpolation(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFstringInterpolation" ):
                return visitor.visitFstringInterpolation(self)
            else:
                return visitor.visitChildren(self)




    def fstringInterpolation(self):

        localctx = MethodScriptParser.FstringInterpolationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_fstringInterpolation)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 291
            self.match(MethodScriptParser.FSTRING_INTERP_START)
            self.state = 292
            self.match(MethodScriptParser.FSTRING_IDENTIFIER)
            self.state = 296
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==165:
                self.state = 293
                self.match(MethodScriptParser.FSTRING_LBRACK)
                self.state = 294
                _la = self._input.LA(1)
                if not(_la==164 or _la==167):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 295
                self.match(MethodScriptParser.FSTRING_RBRACK)


            self.state = 298
            self.match(MethodScriptParser.FSTRING_INTERP_END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





