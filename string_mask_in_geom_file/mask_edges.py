#!/usr/bin/env python3
"""
python3 mask_edges.py <geometry file> <number of x pixels of edges that is necessary to mask> [-y, <number of y pixels of edges that is necessary to mask>]
if -y is skipped, it will mask the same number of pixels for all edges directions.

python3 mask_edges.py file.geom 4 -y 7

python3 mask_edges.py file.geom 5
"""


import argparse
import os
import sys


os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('geom_file', type=str, help="Input geometry file")
    parser.add_argument('x_pixel', type=int, help="Number of x pixels from edges that is necessary to mask")
    parser.add_argument('-y','--y_pixel', type=int, help="Number of y pixels from edges that is necessary to mask")

    return parser.parse_args()

def read_file(filename):
    with open(filename, encoding='utf8') as file_:
        return file_.read()

def write_to_file(filename, content):
    with open(filename, 'a+', encoding='utf8') as file_:
        return file_.write(content)


def render_template(template_path, output_path, context):
    #render_template(template_file_name, os.path.join('result',new_file_name), context)
    content = read_file(template_path)

    for key, value in context.items():
        content = content.replace('{%s}' % key, str(value))

    write_to_file(output_path, content)

def bcopy_cxi(geom_file_name):
    geom_copy_file_name = geom_file_name.split('.')[0] + '_new.geom'
    h5r = open(geom_file_name, 'rb')
    geom_copy = open(geom_copy_file_name, 'wb')
    lines = h5r.readlines()

    for line in lines:
        geom_copy.write(line)

    h5r.close()
    geom_copy.close()

    return geom_copy_file_name

if __name__ == "__main__":
    template_file_name = 'string_mask_template.geom'
    args = parse_cmdline_args()

    geom_file_name = args.geom_file
    x_pix = args.x_pixel #fs

    if args.y_pixel is None:
        y_pix = x_pix #ss
    else:
        y_pix = args.y_pixel

    def_dim = {}

    in_geom = open(geom_file_name, 'r+')
    for line in in_geom:
        if line.startswith('p') and not(line.startswith(';')) and '/' in line: # p0a0/dim3 = fs
            s = line.split(' = ') # [p0a0/min_fs; 0]    [p0a0/dim3; fs]
            l = line.split('/') #   [p0a0; min_fs = 0]  [p0a0; dim3 = fs]
            s1 = s[0].split('/') #  [p0a0; min_fs]      [p0a0; dim3]
            
            if len(s1) == 2 and s1[1] in ('dim2', 'dim3'): #('dim2', 'dim3')
                def_dim[s1[1]] = s[1].strip()
                if len(def_dim) == 2:
                    break
    in_geom.close()

    print(def_dim)
    output_path = bcopy_cxi(geom_file_name)

    for i in range(16):

        context = {
        'num_panel': i,
        'def_dim2': def_dim['dim2'],
        'def_dim3': def_dim['dim3'],
        'h1max_fs_value': x_pix,
        'h2min_fs_value': 127 - x_pix,
        'v1max_ss_value': y_pix,
        'v2min_ss_value': 63 - y_pix,
        'v2max_ss_value': 64 + y_pix,
        'v3min_ss_value': 127 - y_pix,
        'v3max_ss_value': 128 + y_pix,
        'v4min_ss_value': 191 - y_pix,
        'v4max_ss_value': 192 + y_pix,
        'v5min_ss_value': 255 - y_pix,
        'v5max_ss_value': 256 + y_pix,
        'v6min_ss_value': 319 - y_pix,
        'v6max_ss_value': 320 + y_pix,
        'v7min_ss_value': 383 - y_pix,
        'v7max_ss_value': 384 + y_pix,
        'v8min_ss_value': 447 - y_pix,
        'v8max_ss_value': 448 + y_pix,
        'v9min_ss_value': 511 - y_pix
        }

        render_template(template_file_name, output_path, context)



    

