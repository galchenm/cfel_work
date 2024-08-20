import os
import sys
import re

input_filename = sys.argv[1]
scale_factor = float(sys.argv[2])
output_filename = os.path.abspath(input_filename).split('.')[0]+'-scaled.hkl'
print(output_filename)
output = open(output_filename, 'w+')

with open(input_filename, 'r') as file:
    is_start_scaling = False
    for line in file:
        if line.startswith('   h    k    l          I    phase   sigma(I)   nmeas'):
            output.write(line)
            is_start_scaling = True
        elif line.startswith('End of reflections'):
            output.write(line)
            is_start_scaling = False            
        elif is_start_scaling:
            h, k, l, I, sigma_I, nmeas = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", line)
            sigma_I = scale_factor * float(sigma_I)
            phase = '-'
            new_line = "%4i %4i %4i %10.2f        %s %10.2f %7i\n" % (int(h), int(k), int(l), float(I), phase, sigma_I, int(nmeas))
            output.write(new_line)

        else:
            output.write(line)
            
output.close()