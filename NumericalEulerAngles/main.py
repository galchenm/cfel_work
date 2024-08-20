import os
import sys
import numpy as np
from collections import defaultdict
import numpy.linalg as ln
from scipy.spatial.transform import Rotation as R
import math

def create_mat_cur(astar, bstar, cstar):
    mat_cur = []
    mat_cur.append(astar)
    mat_cur.append(bstar)
    mat_cur.append(cstar)
    mat_cur = np.array(mat_cur)
    mat_cur = mat_cur.T
    return mat_cur

def cell_crystallographic_to_cartesian(cell_param):  # cell_param.append([float(a),float(b),float(c),float(alfa),float(betta),float(gamma)])
    mat_id = []

    alfa = cell_param[1][0] * math.pi / 180.0
    betta = cell_param[1][1] * math.pi / 180.0
    gamma = cell_param[1][2] * math.pi / 180.0

    astar_x = cell_param[0][0]
    astar_y = 0.0
    astar_z = 0.0

    bstar_x = cell_param[0][1] * math.cos(gamma)
    bstar_y = cell_param[0][1] * math.sin(gamma)
    bstar_z = 0.0

    tmp = math.cos(alfa) * math.cos(alfa) + math.cos(betta) * math.cos(betta) + math.cos(gamma) * math.cos(
        gamma) - 2.0 * math.cos(alfa) * math.cos(betta) * math.cos(gamma)
    V = cell_param[0][0] * cell_param[0][1] * cell_param[0][2] * math.sqrt(1.0 - tmp)

    cosalphastar = math.cos(betta) * math.cos(gamma) - math.cos(alfa)
    cosalphastar /= math.sin(betta) * math.sin(gamma)

    cstar = (cell_param[0][0] * cell_param[0][1] * math.sin(gamma)) / V

    cstar_x = cell_param[0][2] * math.cos(betta)
    cstar_y = -cell_param[0][2] * math.sin(betta) * cosalphastar
    cstar_z = 1.0 / cstar

    mat_id.append([astar_x, astar_y, astar_z])
    mat_id.append([bstar_x, bstar_y, bstar_z])
    mat_id.append([cstar_x, cstar_y, cstar_z])

    mat_id = np.array(mat_id)

    return mat_id

# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R) :
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype = R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n #< 1e-6

# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):

    #assert(isRotationMatrix(R))
    print(isRotationMatrix(R))
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])

    singular = sy < 1e-6

    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0

    return np.array([x, y, z])


def processing2(i):
    filename = i[0]
    event = i[1]
    cell_param = i[2]
    mat_cur = create_mat_cur(i[3], i[4], i[5])
    
    mat_id = cell_crystallographic_to_cartesian(cell_param)

    transform_matrix = mat_cur.dot(mat_id)
    transform_matrix = ln.inv(transform_matrix)
    
    euler_angles = rotationMatrixToEulerAngles(transform_matrix)
    #print(f'{filename}; {event}; {euler_angles[0]}; {euler_angles[1]}; {euler_angles[2]}')
    

def processing(i):
    filename = i[0]
    event = i[1]
    cell_param = i[2]
    mat_cur = create_mat_cur(i[3], i[4], i[5])
    
    mat_id = cell_crystallographic_to_cartesian(cell_param)

    transform_matrix = mat_cur.dot(mat_id)
    transform_matrix = ln.inv(transform_matrix)
    
    
    r = R.from_matrix(transform_matrix)
    euler_angles = r.as_euler('xyz', degrees=False)
    print(f'{filename}; {event}; {euler_angles[0]}; {euler_angles[1]}; {euler_angles[2]}')
    
    


def get_opt_patterns(lines):
    metadata = []

    name_of_file = None
    event = None
    cell = None
    astar = None
    bstar = None
    cstar = None

    for line in lines:
        if 'Image filename:' in line:
            name_of_file = line.split()[2]
        
        elif line.startswith('Event:'):
        
            event = line.strip().split('//')[-1]

        elif 'Cell parameters' in line:
            pref3, pref4, a, b, c, size1, alfa, betta, gamma, size_deg = line.split(' ')
            cell = np.array([[float(a) * 1e-9,
                              float(b) * 1e-9,
                              float(c) * 1e-9],
                             [float(alfa),
                              float(betta),
                              float(gamma)]],
                            dtype=float)


        elif 'astar =' in line:
            pref5, sig1, astar1, astar2, astar3, s1 = line.split(' ')
            astar = np.array([float(astar1),
                              float(astar2),
                              float(astar3)],
                             dtype=float) * 1e9

        elif 'bstar = ' in line:
            pref5, sig1, bstar1, bstar2, bstar3, s2 = line.split(' ')
            bstar = np.array([float(bstar1),
                              float(bstar2),
                              float(bstar3)],
                             dtype=float) * 1e9


        elif 'cstar =' in line:
            pref5, sig1, cstar1, cstar2, cstar3, s2 = line.split(' ')
            cstar = np.array([float(cstar1),
                              float(cstar2),
                              float(cstar3)],
                             dtype=float) * 1e9

        if (name_of_file is not None) and (event is not None) and (
            cell is not None) and (astar is not None) and (bstar is not None) and (cstar is not None):
            metadata.append([name_of_file, event, cell, astar, bstar, cstar])
            name_of_file = None
            event = None
            cell = None
            astar = None
            bstar = None
            cstar = None

    return metadata

if __name__ == "__main__":
    stream_file = sys.argv[1]
    #output_txt = sys.argv[2]
    
    with open(stream_file, 'r') as stream:
        lines = stream.readlines()
        output_array = get_opt_patterns(lines)
        #image_filename - 0, event - 1, [a-0, b-1, c-2, alpha-3, betta-4, gamma-5] - 2, astar-3, bstar-4, cstar-5
    
    
    print(f'filename; event; phi; theta; psi')
    for i in output_array:
        processing2(i)