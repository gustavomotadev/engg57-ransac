import re
import sys
from functools import reduce
from math import sqrt

pattern = re.compile(r'@T\s+([0-9]+)\s+([a-q])\s+([01])')

START = 0
END = 1
VALUE = 0
LABEL = 1
TYPE = 2
ALGORYTHM = 'f'

def my_format(s):
    s = list(s)
    for i in range(len(s)):
        if s[i] == '0' and i+1 < len(s) and s[i+1] != '.':
            s[i] = ' '
        else:
            break
    return ''.join(s)

label_dict = {
    'a': 'FUN_COPY', 
    'b': 'FUN_COMP', 
    'c': 'FUN_DSPL', 
    'd': 'FUN_LREG', 
    'e': 'FUN_DSPP',  
    'f': 'ALG', 
    'g': 'ITER', 
    'h': 'STEP_1', 
    'i': 'SELECT_2P',  
    'j': 'STEP_2', 
    'k': 'STEP_3',  
    'l': 'INLIER_CHECK',  
    'm': 'UPDATE_BEST', 
    'n': 'STEP_4', 
    'o': 'LREG_MED', 
    'p': 'LREG_SUM', 
    'q': 'LREG_RES' 
}

if len(sys.argv) != 2:
    print('Usage: ransac_profiler.py transcript_file')
    exit(2)

else:

    data = []
    labels = set()
    data_dict = dict()

    with open(sys.argv[1], 'r') as transcript:
        for line in transcript:
            values = re.search(pattern, line)
            if values:
                data.append([int(values.group(1)), values.group(2), int(values.group(3))])
                labels.add(values.group(2))

    labels = list(labels)
    labels.sort()

    for label in labels:
        data_dict[label] = dict()
        data_dict[label][START] = []
        data_dict[label][END] = []

    for entry in data:
        data_dict[entry[LABEL]][entry[TYPE]].append(entry[VALUE])

    data_ok = True
    for label in labels:
        if len(data_dict[label][START]) != len(data_dict[label][END]):
            print('Section ' + label_dict[label] + '(' + label + ')' + ' NOT OK!')
            data_ok = False
        else:
            data_dict[label]['time_periods'] = [data_dict[label][END][n] - data_dict[label][START][n] for n in range(len(data_dict[label][START]))]
            data_dict[label]['executions'] = len(data_dict[label]['time_periods'])
            data_dict[label]['total_time'] = reduce(lambda a,b: a + b, data_dict[label]['time_periods'])
            data_dict[label]['mean_time'] = data_dict[label]['total_time'] / data_dict[label]['executions']

            #standard deviation
            data_dict[label]['std_deviation'] = sqrt((reduce(lambda a,b: a + b, [(x - data_dict[label]['mean_time'])**2 for x in data_dict[label]['time_periods']])) / data_dict[label]['executions'])

            #order
            #data_dict[label]['order'] = data_dict[label]['total_time'] + 2*data_dict[label]['std_deviation']

    if not data_ok:

        print('Error in the data, not the same amount of starts and ends.')
        exit(2)

    else:

        labels.sort(key=lambda x: data_dict[x]['total_time'])

        with open(sys.argv[1].replace('.txt', '_profile.txt'), 'w') as output:

            for label in labels:

                data_dict[label]['percentage'] = (data_dict[label]['total_time'] / data_dict[ALGORYTHM]['total_time']) * 100

                #print('| Label: ' + label + ' | ' + '{:21s}'.format('Section: ' + label_dict[label] + '') + ' | Executions: ' + '{:5d}'.format(data_dict[label]['executions']) + 
                #    ' | Time: ' + '{:9d}'.format(data_dict[label]['total_time']) + ' | %: ' + my_format('{:7.3f}'.format(round(data_dict[label]['percentage'], 6))) + 
                #    ' | Mean: ' + '{:9d}'.format(round(data_dict[label]['mean_time'])) + ' | S: ' + '{:9d}'.format(round(data_dict[label]['std_deviation'])) + ' |')

                print('| Label: ' + label + ' | ' + '{:21s}'.format('Section: ' + label_dict[label] + '') + ' | Executions: ' + '{:5d}'.format(data_dict[label]['executions']) + 
                    ' | Time: ' + '{:9d}'.format(data_dict[label]['total_time']) + ' | %: ' + my_format('{:7.3f}'.format(round(data_dict[label]['percentage'], 6))) + ' |')

                output.write('| Label: ' + label + ' | ' + '{:21s}'.format('Section: ' + label_dict[label] + '') + ' | Executions: ' + '{:5d}'.format(data_dict[label]['executions']) + 
                    ' | Time: ' + '{:9d}'.format(data_dict[label]['total_time']) + ' | %: ' + my_format('{:7.3f}'.format(round(data_dict[label]['percentage'], 6))) + ' |\n')
            