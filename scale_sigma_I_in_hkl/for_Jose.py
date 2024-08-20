import os
import sys
import re

input_filename = sys.argv[1]

output_filename = os.path.abspath(input_filename).split('.')[0]+'-re-formatted.hkl'
print(output_filename)
output = open(output_filename, 'w+')

with open(input_filename, 'r') as file:
    is_start_scaling = False
    for line in file:
        if line.startswith('   h    k    l          I    phase   sigma(I)   nmeas'):
            #output.write(line)
            is_start_scaling = True
        elif line.startswith('End of reflections'):
            #output.write(line)
            is_start_scaling = False            
        elif is_start_scaling:
            h, k, l, I, sigma_I, nmeas = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", line)
            
            
            new_line = "%4i%4i%4i%8.0f%8.0f \n" % (int(h), int(k), int(l), float(I), float(sigma_I))
            output.write(new_line)

        else:
            #output.write(line)
            pass
            
output.close()