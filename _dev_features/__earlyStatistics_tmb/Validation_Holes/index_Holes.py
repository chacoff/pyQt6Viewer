import glob
import os
import pandas as pd
import cv2
from pynput import keyboard
from pynput.keyboard import Key, Controller


def main():
    # root_dir = os.path.join(os.getcwd(), '00_JG-SB_Validation01_2022_02_11-28')
    root_dir = 'T:\\Defects\\'
    pattern = 'ZH026'
    params = {
        'root_dir': root_dir,
        'pattern': pattern,
        'list_of_images': 'Test_2022_08_30\\ZH026_2341_holes_checking.csv',
        'list_validated': 'Test_2022_08_30\\ZH026_SM_validated_all.csv'
    }

    return params


def display_im(root_dir, df, i, n_images, bright):

    # problem, sometimes there are bmp instead of png and sometimes the image doesnt exist at all
    def findImage():
        formats = ['png', 'bmp']
        for ft in formats:
            im_options = root_dir + '\\' + df['Location'][i] + '\\' + df['ImageName'][i].split('.')[0] + '.' + ft
            if os.path.isfile(im_options):
                break
            else:
                continue

        if os.path.isfile(im_options):
            im_locations = im_options
        else:
            im_locations = 'notAvailable.png'

        return im_locations

    img = cv2.imread(findImage())
    scale_percent = 90  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    im = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    title = df['Label'][i] + ' - ' + findImage().split('\\')[-1] + ' - ' + str(i+1) + '/' + str(n_images)
    cv2.putText(im, title, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

    text = "d: Defects \nn: NoDefects \nm: Doubt \nr: Removed \nright: Next \nleft: Previous \nesc: Exit"
    for j, line in enumerate(text.split('\n')):
        y = 650 + j * 30
        cv2.putText(im, line, (1350, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

    im = change_brightness(im, value=bright)  # + increases - decreases

    cv2.imshow('', im)
    cv2.waitKey() & 0xFF


def change_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v,value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def create_df(params):
    batch_images = []
    for filename in glob.iglob(params['root_dir'] + '\\**\\' + params['pattern'] + '**.png', recursive=True):
        label = filename.split('\\')[-2]
        name = filename.split('\\')[-1]
        location = filename.split('\\')[-3:-1]
        location = f'{location[0]}\\{location[1]}'

        batch_images.append((name, label, location))

    df = pd.DataFrame(batch_images, columns=['ImageName', 'Label', 'Location'])

    return df


def on_press(key, hl):
    # print(key)
    try:
        if key.char == 'd':
            # print('seams')
            hl.append('Defects')
        elif key.char == 'n':
            # print('no seams')
            hl.append('NoDefects')
        elif key.char == 'm':
            # print('doubt')
            hl.append('Doubt')
        elif key.char == 'r':
            hl.append('removed')
        else:
            pass

    except AttributeError:
        # print('special key {0} pressed'.format(key))
        pass


def on_release(key):
    global i

    try:
        if key.char == 'd':
            human_label[i] = 'Defects'
            i += 1
        elif key.char == 'n':
            human_label[i] = 'NoDefects'
            i += 1
        elif key.char == 'm':
            human_label[i] = 'Doubt'
            i += 1
        elif key.char == 'r':
            human_label[i] = 'Removed'
            i += 1
        else:
            pass
    except AttributeError:
        pass

    # print('{0} released'.format(key))
    if key == keyboard.Key.right:
        i += 1

    if key == keyboard.Key.left:
        i -= 1

    if key == keyboard.Key.esc:  # Stop listener
        return False

    if i >= n_images:
        i = n_images - 1
    elif i <= 0:
        i = 0
    else:
        i = i

    display_im(params['root_dir'], df, i, n_images, bright=80)


if __name__ == '__main__':

    params = main()
    # df = create_df(params)
    df = pd.read_csv(params['list_of_images'])
    n_images = df.shape[0]
    human_label = ['Doubt'] * n_images

    i = 0
    sim = Controller()
    listener = keyboard.Listener(on_release=on_release)  # on_press=lambda event: on_press(event, human_label)
    listener.start()
    sim.press(Key.left)
    sim.release(Key.left)
    listener.join()

    df.insert(2, 'NewLabel', human_label, True)
    df.index += 1
    print(df)
    df.to_csv(params['list_validated'], index=False)


