import os
import sys
from PIL import Image


def compressMe(file, target, verbose=False):
    filepath = os.path.join(os.getcwd()+target, file)
    picture = Image.open(filepath)
    name_compress = os.path.join(os.getcwd()+target, "compress"+file)
    picture.save(name_compress,
                 "JPEG",
                 optimize=True,
                 quality=10)
    return


def main(target):
    verbose = False
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "-v":
            verbose = True

    cwd = os.getcwd()+target
    formats = ('.jpg', '.jpeg', '.png')
    for file in os.listdir(cwd):
        if os.path.splitext(file)[1].lower() in formats:
            print('compressing', file)
            compressMe(file, target, verbose)
    print("Done")


if __name__ == "__main__":
    main(target='\\runs\\detect\\exp8')
