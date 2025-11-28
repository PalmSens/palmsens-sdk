import pypalmsens as ps


def new_data_callback(new_data):
    for point in new_data:
        print(point)


script = """e
var c
var p
var e
var l
var r
var j
var o
var d
var n
set_gpio_cfg 0x0f 1
set_pgstat_chan 0
set_pgstat_mode 3
set_acquisition_frac_autoadjust 50
set_max_bandwidth 0
cell_off
set_range ba 210m
set_autoranging ba 210m 210m
set_range ab 4200m
set_autoranging ab 210m 4200m
meas_loop_ocp o 200m 1
pck_start
    pck_add o
pck_end
endloop
set_range ba 2100u
set_autoranging ba 2100n 2100u
set_range ab 4200m
set_autoranging ab 4200m 4200m
store_var d -200m ab
add_var d o
store_var n 200m ab
add_var n o
set_e d
cell_on
set_gpio 10i
meas_loop_acv p c e l r j d n 10m 200m 10m 100
pck_start
    pck_add p
    pck_add c
    pck_add e
    pck_add l
    pck_add r
    pck_add j
pck_end
endloop
on_finished:
cell_off

"""

instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    serial = manager.get_instrument_serial()
    print(serial)

    method = ps.MethodScript(script=script)

    measurement = manager.measure(method, callback=new_data_callback)

print(measurement)
