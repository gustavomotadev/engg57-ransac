import os
import sys
from collections import namedtuple
import numpy as np
from matplotlib import pyplot as plt
from sklearn import linear_model

Point = namedtuple('Point', 'x y')

#MAGIC CONSTANTS:
RESIDUAL_THRESHOLD = 8
MIN_POINTS_FOR_LINE = 64

def xAndYFromPoints(points):

    x = []
    y = []
    for point in points:
        x.append(point.x)
        y.append(point.y)
    return x, y

def colorForNumber(num, num_max):
    return tuple(map(lambda x: x*0.8, plt.cm.get_cmap('hsv', num_max*10+1)(num*10+10)))

def plot_ransac(x, y, num_tries):

    #RansacLine = namedtuple('RansacLine', 'inliers_x inliers_y outliers_x outliers_y line_x line_y')

    x = np.array(x)
    y = np.array(y)

    #ransac_lines = []

    line_width = 2

    for z in range(num_tries):

        if len(x) < MIN_POINTS_FOR_LINE or len(y) < MIN_POINTS_FOR_LINE:
            print('Number of tries too high for this data, not enough points left.')
            break

        # Robustly fit linear model with RANSAC algorithm
        ransac = linear_model.RANSACRegressor(residual_threshold=RESIDUAL_THRESHOLD)
        ransac.fit(x.reshape(-1, 1), y)
        inlier_mask = ransac.inlier_mask_
        outlier_mask = np.logical_not(inlier_mask)

        # Predict data of estimated models
        line_x = np.arange(x.min(), x.max())[:, np.newaxis]
        line_y_ransac = ransac.predict(line_x)

        # Compare estimated coefficients
        print('Coefficients estimated using RANSAC:')
        print('Inliers: ' + str(len(inlier_mask)))
        print('Equation: Y = ' + '{0:.6f}'.format(ransac.estimator_.intercept_) + ' + ' + '{0:.6f}'.format(ransac.estimator_.coef_[0]) + 'X')

        #ransac_lines.append(RansacLine(inliers_x=x[inlier_mask], inliers_y=y[inlier_mask], outliers_x=x[outlier_mask], outliers_y=y[outlier_mask], line_x=line_x, line_y=line_y_ransac))

        plt.scatter(x[inlier_mask], y[inlier_mask], s=1, color=colorForNumber(z, num_tries), marker='s')
        plt.scatter(x[outlier_mask], y[outlier_mask], s=1, color='darkgray', marker='s')
        plt.plot(line_x, line_y_ransac, color=colorForNumber(z, num_tries), linewidth=line_width)

        x = x[outlier_mask]
        y = y[outlier_mask]

        #print(len(x))

        #print(line_x)
        #print(line_y_ransac)

    #plt.legend(loc='lower right')
    plt.xticks([0, 255])
    plt.yticks([0, 255])
    plt.xlim(0, 255)
    plt.ylim(0, 255)
    plt.xlabel("X")
    plt.ylabel("Y")
    #plt.scatter(x, y, marker='s')
    plt.gca().invert_yaxis()
    plt.show()


if len(sys.argv) != 3:
    print('Usage: ransac_python.py tsv_file num_tries')
    exit(2)
else:

    file_name = sys.argv[1]
    try:
        num_tries = int(sys.argv[2])
    except ValueError:
        print('Invalid number of tries.')

    if os.path.isfile(file_name): 

        point_list = []
        with open(file_name, 'r') as tsv_file:
            tsv_lines = tsv_file.readlines()[1:]
            for line in tsv_lines:
                x, y = tuple(line.rstrip().split())
                point_list.append(Point(x=int(x), y=int(y)))

        #print(point_list)

            plot_ransac(*xAndYFromPoints(point_list), num_tries)

    else:
        print('Invalid filename.')
        exit(2)