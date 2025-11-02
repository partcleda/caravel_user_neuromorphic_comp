
import os
import shutil
import argparse

parser = argparse.ArgumentParser(description="Run cocotb tests")
parser.add_argument("-extend", help="extend the command")
args = parser.parse_args()

os.environ["CARAVEL_ROOT"] = "/home/marcus/caravel_rtl_fix/caravel"
os.environ["MCW_ROOT"] = "/home/marcus/caravel_rtl_fix/mgmt_core_wrapper"

os.chdir("/home/marcus/caravel_rtl_fix/verilog/dv/cocotb")

command = "python3 /home/marcus/caravel_rtl_fix/venv-cocotb/bin/caravel_cocotb -test ram_word -tag run_02_Nov_04_40_06_64/RTL-ram_word/rerun   -sim RTL -corner nom-t  -seed 1762087209 "
if args.extend is not None:
    command += f" {args.extend}"
os.system(command)

shutil.copyfile("/home/marcus/caravel_rtl_fix/verilog/dv/cocotb/sim/run_02_Nov_04_40_06_64/RTL-ram_word/rerun.py", "/home/marcus/caravel_rtl_fix/verilog/dv/cocotb/sim/run_02_Nov_04_40_06_64/RTL-ram_word/rerun/RTL-ram_word/rerun.py")
