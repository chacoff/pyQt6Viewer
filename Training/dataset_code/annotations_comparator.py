import os
import shutil


def check_and_move_bmp_files(txt_folder: str, source_folder: str) -> None:
    txt_files = [file for file in os.listdir(txt_folder) if file.endswith(".txt")]

    i = 0
    for txt_file in txt_files:
        bmp_file = txt_file[:-4] + ".bmp"
        bmp_file_path = os.path.join(txt_folder, bmp_file)
        source_folder_path = os.path.join(source_folder, bmp_file)

        if not os.path.exists(bmp_file_path):
            if os.path.exists(source_folder_path):
                print(f"The BMP file '{bmp_file}' is missing in '{txt_folder}' but exists in '{source_folder}'.")
                shutil.move(source_folder_path, bmp_file_path)
                i += 1
    print(f'total images found: {i}')


def compare_same_name_files(folder1: str, folder2: str) -> None:
    files1 = [file for file in os.listdir(folder1) if file.endswith(".bmp")]
    files2 = [file for file in os.listdir(folder2) if file.endswith(".bmp")]

    common_files = set(files1) & set(files2)

    if len(common_files) > 0:
        print("The following files have the same name in both folders:")
        i = 0
        for file in common_files:
            os.remove(os.path.join(folder2, file))
            print(f'removed: {file}')
            i += 1
        print(f'total equal files: {i}')
    else:
        print("There are no files with the same name in both folders.")


def main(move: bool = False, compare: bool = True, params: dict = None) -> None:

    if move:
        check_and_move_bmp_files(txt_folder=params['annotations'], source_folder=params['images_set'])

    if compare:
        compare_same_name_files(folder1=params['annotations'], folder2=params['images_set'])


if __name__ == '__main__':

    parameters = {
        'annotations': 'C:/Users/gomezja/PycharmProjects/00_dataset/Seams',
        'images_set': 'C:/Users/gomezja/PycharmProjects/00_dataset/Seams_no_annotations'
    }

    main(move=False, compare=True, params=parameters)

