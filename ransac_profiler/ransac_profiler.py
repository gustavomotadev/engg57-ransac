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
            print('Section ' + label + ' NOT OK!')
            data_ok = False
        else:
            data_dict[label]['time_periods'] = [data_dict[label][END][n] - data_dict[label][START][n] for n in range(len(data_dict[label][START]))]
            data_dict[label]['executions'] = len(data_dict[label]['time_periods'])
            data_dict[label]['total_time'] = reduce(lambda a,b: a + b, data_dict[label]['time_periods'])
            data_dict[label]['mean_time'] = data_dict[label]['total_time'] / data_dict[label]['executions']

            #standard deviation
            data_dict[label]['std_deviation'] = sqrt((reduce(lambda a,b: a + b, [(x - data_dict[label]['mean_time'])**2 for x in data_dict[label]['time_periods']])) / data_dict[label]['executions'])

            #order
            data_dict[label]['order'] = data_dict[label]['total_time'] + 2*data_dict[label]['std_deviation']

    labels.sort(key=lambda x: data_dict[x]['order'])

    for label in labels:

        data_dict[label]['percentage'] = (data_dict[label]['total_time'] / data_dict[ALGORYTHM]['total_time']) * 100

        print('[Section ' + label + '] Executions: ' + '{:5d}'.format(data_dict[label]['executions']) + 
            ' Time: ' + '{:9d}'.format(data_dict[label]['total_time']) + ' %: ' + '{:05.1f}'.format(round(data_dict[label]['percentage'], 1)) + 
            ' Mean: ' + '{:9d}'.format(round(data_dict[label]['mean_time'])) + ' S: ' + '{:9d}'.format(round(data_dict[label]['std_deviation'])))

    if not data_ok:

        print('Error in the data, not the same amount of starts and ends.')
        exit(2)

    else:
        pass