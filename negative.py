import numpy as np
import matplotlib.pyplot as plt
import random
import positive as pos
import os
import shutil


# Calculate the corner point of the picture
def corner_point(position):
    x1, y1, x2, y2 = position
    return int(min(x1, x2)), int(min(y1, y2)), int(max(x1, x2)), int(max(y1, y2))


# Refresh the data. Return the selected region of data
def data_refresh(data, x_final, y_final, window_shape_value):
    data_refresh = data[y_final:y_final+window_shape_value,
                        x_final:x_final+window_shape_value]
    return data_refresh


# Save the data and asteroid position into a *.npz file
def save_data_negative(name, index, count, data, data_dir):
    dataPath = '{}\{}_{}'.format(data_dir, count, name)
    np.savez(dataPath, matrix1=data)
    print('Successfully save data for index:{} count:{} filename:{}'
          .format(index, count, name))


# Plot the data and save into a *.jpg file
def plot_data_negative(name, count, data, pic_dir):
    plt.imshow(data, cmap='gray', vmin=0, vmax=0.01)
    plt.colorbar()
    plt.savefig('{}\{}_{}.jpg'.format(pic_dir, count, name), dpi=300)
    plt.clf()


# Find the posible negative pictures
def find_region(data, corner, window_shape_value, name, index, count, data_dir, pic_dir):
    x_min, y_min, x_max, y_max = corner

    x_final = []
    y_final = []

    if x_min > window_shape_value+500:
        x_final.append(random.randint(0, x_min - window_shape_value - 300))

    if (4000 - x_max) > window_shape_value+500:
        x_final.append(random.randint(x_max+300, 4000 - window_shape_value))

    if y_min > window_shape_value+500:
        y_final.append(random.randint(0, y_min - window_shape_value - 300))

    if (4000 - y_max) > window_shape_value+500:
        y_final.append(random.randint(y_max+300, 4000 - window_shape_value))

    if x_final == [] or y_final == []:
        return count

    for i in x_final:
        for j in y_final:
            data_new = data_refresh(data, i, j, window_shape_value)
            if data_new.shape != (window_shape_value, window_shape_value):
                print('Error! Count:{} Index:{} Data shape does not fit as expected')
                continue

            save_data_negative(name, index, count, data_new, data_dir)
            plot_data_negative(name, count, data_new, pic_dir)
            count += 1

    return count


# Wrap it up
def generate_negative_data(father_dir, pic_dir, data_dir, start_index, end_count, window_shape_value=1000):
    # Count the number of accepted negative picture
    index = start_index
    count = 0

    # Iterate through the data
    while count < end_count:
        # Get the path and filename of the original data file (generated by download.py)
        if index > len(os.listdir(father_dir))-2:
            break

        path, name = pos.path_of_data(father_dir, index)
        print('Start preprocessing {}: {}'.format(index, name))

        if index > 0 and index < len(os.listdir(father_dir)):
            _, name_last = pos.path_of_data(father_dir, index-1)
            _, name_next = pos.path_of_data(father_dir, index+1)
            if name_next[-9:] == name[-9:] or name_last[-9:] == name[-9:]:
                print(
                    f"Warning: {path} seems to have more than 1 asteroid trail. Skip this picture.")
                index += 1
                continue

        # Load the *.npz file, and get the position of the asteroid trail
        data, position = pos.load_saved_data(path)

        # Convert the 'nan' value to 0 in the array
        data = np.nan_to_num(data)

        # Calculate the corner of the asteroid trail
        corner = corner_point(position)

        # Check if we can use this image to generate a negative picture.
        # If so, randomly pick two pictures with no asteroid trails.
        count = find_region(data, corner, window_shape_value,
                            name, index, count, data_dir, pic_dir)
        index += 1


# Randomly split the data set to train and validation. We choose a 80/20 split.
def random_split(dir_train, dir_val, dir_test):
    fileList = os.listdir(dir_train)
    for file in fileList:
        train_file = os.path.join(dir_train, file)
        val_file = os.path.join(dir_val, file)
        test_file = os.path.join(dir_test, file)

        random_num = random.random()
        if random_num < 0.15:
            shutil.move(train_file, test_file)
            print('File move from {} to {}'.format(train_file, test_file))
        elif random_num < 0.3:
            shutil.move(train_file, val_file)
            print('File move from {} to {}'.format(train_file, val_file))
        else:
            print('File does not move')


# Main Function
if __name__ == '__main__':
    generate_negative_data('.\data',
                           '.\pic_negative',
                           '.\\preprocess\\train\\negative',
                           start_index=0, end_count=1710,
                           window_shape_value=1000)
    random_split('.\\preprocess\\train\\negative',
                 '.\\preprocess\\val\\negative',
                 '.\\preprocess\\test\\negative')