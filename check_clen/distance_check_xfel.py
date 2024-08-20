import os
import h5py as h5
import sys
import numpy as np
import re

files = open('files.lst', 'r')
clen = "/CONTROL/SPB_IRU_AGIPD1M/MOTOR/Z_STEPPER/actualPosition/value"
encoded_clen = "/CONTROL/SPB_IRU_AGIPD1M/MOTOR/Z_STEPPER/encoderPosition/value"

file_to_write = open('result.txt', 'w+')
line_to_write = "RUN\tactualPosition begin\tactualPosition end\tencoderPosition begin\tencoderPosition end\n"
file_to_write.write(line_to_write)

for h5Filename in files:
    h5Filename = h5Filename.strip()
    run_name = re.search(r"R\d+[_\d+]*", os.path.basename(h5Filename)).group()
    print("run_name is {}".format(run_name))
    check = h5Filename + clen
    myCmd = os.popen('h5ls ' + check).read()

    encoded_check = h5Filename + encoded_clen
    encoded_myCmd = os.popen('h5ls ' + encoded_check).read()    

    if "NOT" in myCmd:
        print('Error: no clen from .h5 file')
        clen_v_begin = " "
        clen_v_last = " "  
    else:
        f = h5.File(h5Filename, 'r')
        clen_v = f[clen][()]
        clen_v = clen_v[clen_v!=0.]
        clen_v_begin = str(clen_v[0])
        clen_v_last = str(clen_v[len(clen_v) - 1])
        f.close()

    if "NOT" in encoded_myCmd:
        print('Error: no clen from .h5 file')
        encoded_clen_v_begin = " "
        encoded_clen_v_last = " "
    else:
        f = h5.File(h5Filename, 'r')
        encoded_clen_v = f[encoded_clen][()]
        encoded_clen_v = encoded_clen_v[encoded_clen_v!=0.]
        encoded_clen_v_begin = str(encoded_clen_v[0])
        encoded_clen_v_last = str(encoded_clen_v[len(encoded_clen_v)-1])
        f.close()
    
    if len(clen_v_begin) == 0:
        pass
    else:
        line_to_write = "{}\t{}\t{}\t{}\t{}\n".format(run_name,clen_v_begin, clen_v_last, encoded_clen_v_begin, encoded_clen_v_last)
        #line_to_write = "{}\t{}\t{}\n".format(run_name,clen_v_begin, encoded_clen_v_begin)
        print(line_to_write)
        file_to_write.write(line_to_write)

file_to_write.close()
files.close()
