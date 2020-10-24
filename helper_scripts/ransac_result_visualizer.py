from sys import stdin
from collections import namedtuple
from matplotlib import pyplot as plt

Point = namedtuple('Point', 'x y')
Equation = namedtuple('Equation', 'index a b')

def consume_stdin():
    input_ = []
    temp = ''
    while temp != '@DATA_END':
        temp = stdin.readline().rstrip()
        input_.append(temp)
    return input_

def get_data(data, key_name):
    try:
        index = data.index(key_name)
        return list(filter(None, data[index+1].split(',')))
    except ValueError:
        return []

def colorForNumber(num, num_max):
    if(num) == 0:
        return 'darkgray'
    else:
        return tuple(map(lambda x: x*0.8, plt.cm.get_cmap('hsv', num_max*10+1)(num*10+10)))

stdin_text = consume_stdin()

data_points = get_data(stdin_text, '@DATA_POINTS')
inlier_mask = get_data(stdin_text, '@INLIER_MASK')
equations = get_data(stdin_text, '@EQUATIONS')

#print(len(data_points))
#print(len(inlier_mask))
#print(len(equations))

#[expression for item in list if conditional]
data_points = [Point(x=float(data_points[i]), y=float(data_points[i+1])) for i in range(0, len(data_points), 2)]
inlier_mask = list(map(lambda x: int(x), inlier_mask))
equations = [Equation(index=int(equations[i]), a=float(equations[i+1]), b=float(equations[i+2])) for i in range(0, len(equations), 3)]
#print(data_points)
#print(equations)

equation_points = [[data_points[i] for i in range(len(inlier_mask)) if inlier_mask[i] == k] for k in set(inlier_mask)]

for k in range(len(equation_points)):
    plt.scatter([point.x for point in equation_points[k]], [point.y for point in equation_points[k]], s=1, color=colorForNumber(k, len(equation_points)), marker='s')
    if k != 0:
        plt.plot([0, 255], [equations[k-1].a, equations[k-1].a + equations[k-1].b*255], ls='-', color=colorForNumber(k, len(equation_points)))

plt.xticks([0, 255])
plt.yticks([0, 255])
plt.xlim(0, 255)
plt.ylim(0, 255)
plt.xlabel("X")
plt.ylabel("Y")
plt.gca().invert_yaxis()
plt.show()

