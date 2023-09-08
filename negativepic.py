import numpy as np
import matplotlib.pyplot as plt
import random
import preprocess as prep


def corner_point(position):
    x1, y1, x2, y2 = position
    return int(min(x1, x2)), int(min(y1, y2))


def data_refresh(data, x_final, y_final, window_shape_value):
    data_refresh = data[y_final:y_final+window_shape_value,
                        x_final:x_final+window_shape_value]
    return data_refresh


# Save the data and asteroid position into a npz file
def save_data_negative(name, index, count, data, data_dir):
    dataPath = '{}\{}_{}'.format(data_dir, count, name)
    np.savez(dataPath, matrix1=data)
    print('Successfully save data for index:{} count:{} filename:{}'.format(
        index, count, name))


def plot_data_negative(name, count, data, pic_dir):
    plt.imshow(data, cmap='gray', vmin=0, vmax=0.01)
    plt.colorbar()
    plt.savefig('{}\{}_{}.jpg'.format(pic_dir, count, name), dpi=300)
    plt.clf()


def generate_negative_data(father_dir, pic_dir, data_dir, start_index, end_index, window_shape_value=1000):
    count = 0

    for index in range(start_index, end_index):
        path, name = prep.path_of_data(father_dir, index)
        print('Start preprocessing {}: {}'.format(index, name))
        data, position = prep.load_saved_data(path)
        data = np.nan_to_num(data)
        x_corner, y_corner = corner_point(position)
        if x_corner > window_shape_value+500 and y_corner > window_shape_value+500:
            for i in range(2):
                x_final = random.randint(0, x_corner - window_shape_value)
                y_final = random.randint(0, y_corner - window_shape_value)
                data_new = data_refresh(
                    data, x_final, y_final, window_shape_value)
                save_data_negative(name, index, count, data_new, data_dir)
                plot_data_negative(name, count, data_new, pic_dir)
                count += 1


def random_split(dir_train, dir_val):
    fileList = os.listdir(dir_train)
    for file in fileList:
        train_file = os.path.join(dir_train, file)
        val_file = os.path.join(dir_val, file)
        if random.random() < 0.2:
            shutil.move(train_file, val_file)
            print('File move from {} to {}'.format(train_file, val_file))
        else:
            print('File does not move')


if __name__ == '__main__':
    generate_negative_data('.\data',
                           '.\pic_negative',
                           '.\\preprocess\\train\\negative',
                           0, 10, 1000)
    random_split('.\\preprocess\\train\\negative',
                 '.\\preprocess\\val\\negative')
