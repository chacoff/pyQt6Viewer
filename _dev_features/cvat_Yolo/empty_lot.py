import os


def has_image(folder_path):
    image_extensions = ['.png', '.bmp']
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            return True
    return False


def find_folders_without_images(root_path):
    folders_without_images = []
    for folder_name, _, _ in os.walk(root_path):
        if not has_image(folder_name):
            folders_without_images.append(folder_name)
    return folders_without_images


if __name__ == "__main__":
    root_directory = "C:\\Users\\gomezja\\PycharmProjects\\00_dataset\\training"
    folders_without_images = find_folders_without_images(root_directory)

    if folders_without_images:
        print("Folders without PNG or BMP images:")
        for folder in folders_without_images:
            print(folder)
    else:
        print("All folders contain PNG or BMP images.")
