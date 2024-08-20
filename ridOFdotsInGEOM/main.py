import os
import sys

geom_input = sys.argv[1]
geom_output = geom_input.split('.')[0] +'_v1.geom'

ss_fs = ["min_ss","min_fs","max_ss", "max_fs"]
out_geom = open(geom_output, 'w')
with open(geom_input, 'r') as inp:
    for line in inp:
        st = line.split(' = ')
        s = st[0].split('/')
        if len(s) == 2 and s[1] in ss_fs and not line.startswith(";"):
            val = st[1]
            newline = s[0] + "/"+s[1] + " = {}\n".format(int(float(val)))
            out_geom.write(newline)
        else:
            out_geom.write(line)
