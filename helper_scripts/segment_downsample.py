import os
import re
import sys
from PIL import Image
from PIL import UnidentifiedImageError

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = 'images'
IMAGES_PATH = os.path.join(SCRIPT_PATH, IMAGES_DIR, '')
ACCEPT_PATTERN = re.compile(r'_\.(?:jpg|jpeg|bmp|png)')
FILENAME_PATTERN = re.compile(r'(.*)_\.(?:jpg|jpeg|bmp|png)')
DOWNSAMPLING_PATTERN = re.compile(r'^--x[0-9]+')

try:
    
    SAVE_IMG = False
    SHOW_IMG = False
    PROCESS_ALL = False
    DOWNSAMPLING_FACTOR = 4

    if '--save' in sys.argv:
        SAVE_IMG = True
        sys.argv.remove('--save')

    if '--show' in sys.argv:
        SHOW_IMG = True
        sys.argv.remove('--show')

    DOWNSAMPLING_STR = list(filter(lambda x: re.search(DOWNSAMPLING_PATTERN, x), sys.argv))
    for element in DOWNSAMPLING_STR:
        sys.argv.remove(element)
    if len(DOWNSAMPLING_STR) == 1:
        DOWNSAMPLING_FACTOR = int(DOWNSAMPLING_STR[0][3:])

    if '--all' in sys.argv:
        PROCESS_ALL = True
        sys.argv.remove('--all')
    elif(len(sys.argv) < 2):
        raise ValueError

except:
    print('''Usage: 
segment_downsample.py --all (--save, --show, --x2/--x4/--x8/--x[0-9]+)
OR
segment_downsample.py file0 file1 file2 ... (--save, --show, --x2/--x4/--x8/--x[0-9]+)''')
    exit(2)

if PROCESS_ALL:
    files = map(lambda x: IMAGES_PATH + x, os.listdir(IMAGES_PATH))
else:
    files = sys.argv + list(map(lambda x: IMAGES_PATH + x, sys.argv))

files = list(filter(lambda x: os.path.isfile(x) and re.search(ACCEPT_PATTERN, x), files))

#print(DOWNSAMPLING_FACTOR)

print('filename number_of_data_points')

for f in files:

    try:

        with Image.open(f) as img:

            clean_name = re.match(FILENAME_PATTERN, f)[1]
            data_points = []

            with Image.new('1', (img.size[0], img.size[1])) as threshold:

                red_filter = img.copy()

                img_data = img.load()
                red_filter_data = red_filter.load()
                threshold_data = threshold.load()
                
                num_points = 0
                for i in range(img.size[0]):    # for every col:
                    for j in range(img.size[1]):    # For every row
                        if(img_data[i,j][0] >> 7 == 1 and img_data[i,j][1] >> 6 == 0 and img_data[i,j][2] >> 6 == 0): # threshold
                            threshold_data[i,j] = 255
                            num_points += 1
                        else:
                            red_filter_data[i,j] = (0, 0, 0)

                #img.show()
                #threshold.show()

                #red_filter.save(clean_name + '_red_filter.png')
                #threshold.save(clean_name + '_threshold.png')

                with Image.new('1', (img.size[0], img.size[1])) as downsampled:
                    with Image.new('1', (img.size[0]//DOWNSAMPLING_FACTOR, img.size[1]//DOWNSAMPLING_FACTOR)) as resized:

                        downsampled_data = downsampled.load()
                        resized_data = resized.load()

                        num_samples = 0
                        for i in range(DOWNSAMPLING_FACTOR//2, img.size[0], DOWNSAMPLING_FACTOR):
                            for j in range(DOWNSAMPLING_FACTOR//2, img.size[1], DOWNSAMPLING_FACTOR):

                                try:
                                    downsampled_data[i, j] = threshold_data[i, j]
                                    resized_data[i//DOWNSAMPLING_FACTOR, j//DOWNSAMPLING_FACTOR] = threshold_data[i, j]
                                    if(threshold_data[i,j] == 255):
                                        data_points.append((i, j))
                                        num_samples += 1
                                except IndexError:
                                    pass

                        #downsampled.save(clean_name + '_samples_x' + str(DOWNSAMPLING_FACTOR) + '.png')
                        #resized.save(clean_name + '_downsampled_x' + str(DOWNSAMPLING_FACTOR) + '.png')

                print(f + ' ' + str(num_samples))

                with open(clean_name.replace('images', 'tsv') + '_points_x' + str(DOWNSAMPLING_FACTOR) + '.tsv', 'w') as tsv_file:
                    tsv_file.write('x\ty\n')
                    for point in data_points:
                        tsv_file.write(f'{point[0]}\t{point[1]}\n')

                if SHOW_IMG or SAVE_IMG:
                    grid_img = Image.new(img.mode, (img.size[0]*2, img.size[1]*2))
                    grid_img.paste(img, (0, 0))
                    grid_img.paste(red_filter, (img.size[0], 0))
                    grid_img.paste(threshold, (0, img.size[1]))
                    grid_img.paste(downsampled, (img.size[0], img.size[1]))
                    
                    if SAVE_IMG:
                        grid_img.save(clean_name + '_image_x' + str(DOWNSAMPLING_FACTOR) + '.png')

                    if SHOW_IMG:
                        grid_img.show()

    except UnidentifiedImageError:
        print(f + 'is not a valid image file')