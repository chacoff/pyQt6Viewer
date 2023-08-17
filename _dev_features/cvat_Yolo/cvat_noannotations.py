import os


folder = r'C:\Users\gomezja\PycharmProjects\00_dataset\training'

for file in os.listdir(folder):
    if file.endswith('.png'):
        print(file)
    elif file.endswith('.bmp'):
        print(file)
    elif file.endswith('.xml'):
        pass