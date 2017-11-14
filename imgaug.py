#!usr/bin/env python
# -*-coding:utf-8-*-
import sys, os, re, traceback
from os.path import isfile

# python2:
# from multiprocessing.dummy import Pool, cpu_count
# python3:
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

from counter import Counter
from ops.rotate import Rotate
from ops.fliph import FlipH
from ops.flipv import FlipV
from ops.zoom import Zoom
from ops.blur import Blur
from ops.noise import Noise
from ops.translate import Translate
import numpy
import cv2

EXTENSIONS = ['png', 'jpg', 'jpeg', 'bmp']
WORKER_COUNT = max(cpu_count() - 1, 1)
OPERATIONS = [Rotate, FlipH, FlipV, Translate, Noise, Zoom, Blur]

'''
Augmented files will have names matching the regex below, eg
    original__rot90__crop1__flipv.jpg
'''
AUGMENTED_FILE_REGEX = re.compile('^.*(__.+)+\\.[^\\.]+$')
EXTENSION_REGEX = re.compile('|'.join(map(lambda n: '.*\\.' + n + '$', EXTENSIONS)))

thread_pool = None
counter = None
WORKING_DIR = os.getcwd() + "/"


def load_cube_img(src_path, rows, cols, size):
    img = cv2.imread(src_path, cv2.IMREAD_GRAYSCALE)
    # assert rows * size == cube_img.shape[0]
    # assert cols * size == cube_img.shape[1]
    res = numpy.zeros((rows * cols, size, size))
    img_height = size
    img_width = size
    for row in range(rows):
        for col in range(cols):
            src_y = row * img_height
            src_x = col * img_width
            res[row * cols + col] = img[src_y:src_y + img_height, src_x:src_x + img_width]

    return res


def build_augmented_file_name(original_name, ops):
    root, ext = os.path.splitext(original_name)
    result = root
    for op in ops:
        result += '__' + op.code
    return result + ext


def save_aug_cube_img(dir, file, op_lists, target_path, rows, cols):
    try:
        path = os.path.join(dir, file)
        cube_img = load_cube_img(path, 8, 8, 64)
        assert rows * cols == cube_img.shape[0]
        img_height = cube_img.shape[1]
        img_width = cube_img.shape[1]
        res_img = numpy.zeros((rows * img_height, cols * img_width), dtype=numpy.uint8)

        for op_list in op_lists:
            out_file_name = build_augmented_file_name(file, op_list)
            if isfile(os.path.join(dir, out_file_name)):
                continue
            for row in range(rows):
                for col in range(cols):
                    target_y = row * img_height
                    target_x = col * img_width
                    img = cube_img[row * cols + col]  # the single image
                    for op in op_list:
                        img = op.process(img)
                    res_img[target_y:target_y + img_height, target_x:target_x + img_width] = img

            cv2.imwrite(os.path.join(target_path, out_file_name), res_img)

        counter.processed()
    except:
        traceback.print_exc(file=sys.stdout)


def process(dir, file, op_lists, dst_dir):
    thread_pool.apply_async(save_aug_cube_img, (dir, file, op_lists, dst_dir, 8, 8))


if __name__ == '__main__':
    # image_dir = WORKING_DIR + "test_aug_image/"
    # dst_dir = WORKING_DIR + "test_aug_image_result/"
    image_dir = sys.argv[1]
    if not os.path.isdir(image_dir):
        print('Invalid image directory: {}'.format(image_dir))
        sys.exit(2)
    
    dst_dir = sys.argv[2]
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    op_codes = sys.argv[3:]
    op_lists = []
    for op_code_list in op_codes:
        op_list = []
        for op_code in op_code_list.split(','):
            op = None
            for op in OPERATIONS:
                op = op.match_code(op_code)
                if op:
                    op_list.append(op)
                    break
            if not op:
                print('Unknown operation {}'.format(op_code))
                sys.exit(3)
        op_lists.append(op_list)

    counter = Counter()
    thread_pool = Pool(WORKER_COUNT)
    print('Thread pool initialised with {} worker{}'.format(WORKER_COUNT, '' if WORKER_COUNT == 1 else 's'))

    matches = []
    for dir_info in os.walk(image_dir):
        dir_name, _, file_names = dir_info
        print('Processing {}...'.format(dir_name))
        for file_name in file_names:
            if EXTENSION_REGEX.match(file_name):
                if AUGMENTED_FILE_REGEX.match(file_name):
                    counter.skipped_augmented()
                else:
                    process(dir_name, file_name, op_lists, dst_dir)
            else:
                counter.skipped_no_match()

    print("Waiting for workers to complete...")
    thread_pool.close()
    thread_pool.join()
    print(counter.get())
