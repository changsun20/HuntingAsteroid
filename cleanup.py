import os


def delete_files(directory):
    # 获取目录下的所有文件和子目录
    files = os.listdir(directory)

    for file in files:
        file_path = os.path.join(directory, file)

        # 判断是否为文件
        if os.path.isfile(file_path):
            # 删除文件
            os.remove(file_path)
        elif os.path.isdir(file_path):
            # 如果是目录，则递归调用函数删除子目录中的文件
            delete_files(file_path)
            # 删除空目录
            os.rmdir(file_path)


def clean_up():
    delete_files('.\\preprocess\\train\\positive')
    delete_files('.\\preprocess\\train\\negative')
    delete_files('.\\preprocess\\val\\positive')
    delete_files('.\\preprocess\\val\\negative')
    delete_files('.\\preprocess\\test\\positive')
    delete_files('.\\preprocess\\test\\negative')
    delete_files('.\\pic_positive')
    delete_files('.\\pic_negative')


def clean_up_positive():
    delete_files('.\\preprocess\\train\\positive')
    delete_files('.\\preprocess\\val\\positive')
    delete_files('.\\preprocess\\test\\positive')
    delete_files('.\\pic_positive')


def clean_up_negative():
    delete_files('.\\preprocess\\train\\negative')
    delete_files('.\\preprocess\\val\\negative')
    delete_files('.\\preprocess\\test\\negative')
    delete_files('.\\pic_negative')


if __name__ == '__main__':
    clean_up()
