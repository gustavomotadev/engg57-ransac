import sys
import os
import re

#unsigned int name[size] = {19, 10, 8, 17, 9};

c_string_0 = r'#define NUM_POINTS_ $0'
c_string_3 = r'#define DATA_SIZE_ $5'
c_string_1 = r'const unsigned char data_points_[$1] = {$2};'
c_string_2 = r'unsigned char inlier_mask_[$3] = {$4};'

if len(sys.argv) != 2:
    print('Usage: ransac_python.py tsv_file')
    exit(2)

else:

    file_name = sys.argv[1]

    if os.path.isfile(file_name): 

        point_list = []
        with open(file_name, 'r') as tsv_file:
            tsv_lines = tsv_file.readlines()[1:]
            for line in tsv_lines:
                x, y = tuple(map(lambda x: int(x), line.rstrip().split()))
                point_list.append(x)
                point_list.append(y)

            mask_list = [0]*len(tsv_lines)

            c_string_0 = c_string_0.replace('$0', str(len(tsv_lines)))
            c_string_1 = c_string_1.replace('$1', str(len(point_list)))
            c_string_1 = c_string_1.replace('$2', str(point_list)[1:-1])
            c_string_2 = c_string_2.replace('$3', str(len(tsv_lines)))
            c_string_2 = c_string_2.replace('$4', str(mask_list)[1:-1])
            c_string_3 = c_string_3.replace('$5', str(len(point_list)))

            print(c_string_0)
            print(c_string_3)
            print(c_string_1)
            print(c_string_2)

            output = file_name.replace('tsv', 'headers', 1).replace('tsv', 'h', 1)
            with open(output, 'w') as output_file:
                output_file.write(c_string_0)
                output_file.write('\n')
                output_file.write(c_string_3)
                output_file.write('\n')
                output_file.write(c_string_1)
                output_file.write('\n')
                output_file.write(c_string_2)
                output_file.write('\n')

    else:
        print('Invalid filename.')
        exit(2)