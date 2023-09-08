import numpy as np
import matplotlib.pyplot as plt
import os
import random


def path_of_data(father_dir, index):
    childDirList = os.listdir(father_dir)
    path = '{}\{}'.format(father_dir, childDirList[index])
    name = childDirList[index][:-4]
    return path, name


def load_saved_data(path):
    data = np.load(path)
    image_data = data['matrix1']
    position = data['matrix2']

    return image_data, position


def find_center(position):
    x1, y1, x2, y2 = position
    center_position = (x1 + x2)/2, (y1 + y2)/2
    return center_position


def find_boundary(image_upper_limit, center_value, random_slide, window_shape_value):
    lower_bound = min(max(0, center_value - window_shape_value /
                      2 - random_slide), image_upper_limit - window_shape_value)
    upper_bound = max(min(image_upper_limit, center_value +
                      window_shape_value/2 + random_slide), window_shape_value)
    return lower_bound, upper_bound - window_shape_value


def random_pick_xy(image_shape, center_position, random_slide, window_shape_value):
    x_center, y_center = center_position
    x_center, y_center = int(x_center), int(y_center)

    x_bound = find_boundary(
        image_shape[1], x_center, random_slide, window_shape_value)
    x_final = random.randint(int(x_bound[0]), int(x_bound[1]))

    y_bound = find_boundary(
        image_shape[0], y_center, random_slide, window_shape_value)
    y_final = random.randint(int(y_bound[0]), int(y_bound[1]))

    return x_final, y_final


def data_position_refresh(data, window_shape_value, position, window_position):
    x_final, y_final = window_position
    x1_original, y1_original, x2_original, y2_original = position
    position_refresh = x1_original - x_final, y1_original - \
        y_final, x2_original - x_final, y2_original - y_final

    data_refresh = data[y_final:y_final+window_shape_value,
                        x_final:x_final+window_shape_value]

    return data_refresh, position_refresh


def plot_data(name, data, box_position, pic_dir):
    x1, y1, x2, y2 = box_position    
    plt.imshow(data, cmap='gray', vmin=0, vmax=0.01)
    plt.plot([x1, x2], [y1, y1], 'r')
    plt.plot([x1, x2], [y2, y2], 'r')
    plt.plot([x1, x1], [y1, y2], 'r')
    plt.plot([x2, x2], [y1, y2], 'r')
    plt.colorbar()
    plt.savefig('{}\{}.jpg'.format(pic_dir, name), dpi=300)
    plt.clf()


# Save the data and asteroid position into a npz file
def save_data(name, index, data, position, data_dir):
    matrix2 = np.array(position)
    dataPath = '{}\{}'.format(data_dir, name)
    np.savez(dataPath, matrix1=data, matrix2=matrix2)
    print('Successfully save data for {}: {}'.format(index, name))


def preprocess(father_dir, pic_dir, data_dir, start_index, end_index, random_slide=300, window_shape_value=1000):
    for index in range(start_index, end_index+1):
        path, name = path_of_data(father_dir, index)
        print('Start preprocessing {}: {}'.format(index, name))
        data, position = load_saved_data(path)
        data = np.nan_to_num(data)
        image_shape = data.shape
        center_position = find_center(position)
        window_position = random_pick_xy(
            image_shape, center_position, random_slide, window_shape_value)
        data_refresh, position_refresh = data_position_refresh(
            data, window_shape_value, position, window_position)
        plot_data(name, data_refresh, position_refresh, pic_dir)
        save_data(name, index, data_refresh, position_refresh, data_dir)


if __name__ == '__main__':
    preprocess('.\data',
               '.\pic_positive',
               '.\\preprocess\\train\\positive',
               0, 10, 300, 1000)
