import glob
import os
import pandas as pd
import cv2
from pynput import keyboard
from pynput.keyboard import Key, Controller


def display_im(root_dir, df, i, n_images):

    im_location = root_dir + '\\' + df['ImageName'][i]
    print(im_location)
    img = cv2.imread(im_location)
    scale_percent = 30  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    im = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    title = df['Label'][i] + ' - ' + df['ImageName'][i] + ' - ' + str(i+1) + '/' + str(n_images)
    cv2.putText(im, title, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

    text = "s: Seams \nn: NoSeams \nd: Doubt \nright: Next \nleft: Previous \nesc: Exit"
    for j, line in enumerate(text.split('\n')):
        y = 580 + j * 30
        cv2.putText(im, line, (800, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('', im)
    cv2.waitKey() & 0xFF


def create_df(params):
    batch_images = []
    # print(params['root_dir'])
    for filename in glob.iglob(params['root_dir'] + '\\**\\' + params['pattern'] + '**.bmp', recursive=True):
        label = '-not processed-'  # filename.split('\\')[-2]
        name = filename.split('\\')[-1]
        location = filename.split('\\')[-3:-1]
        location = f'{location[0]}\\{location[1]}'

        batch_images.append((name, label, location))

    df = pd.DataFrame(batch_images, columns=['ImageName', 'Label', 'Location'])

    return df


def main():
    # root_dir = os.path.join(os.getcwd(), 'Validation_Seams','Validation03_2022_10_26', 'ZH022')
    root_dir = f'S:\\defects\\ZH026\\2480'
    save_dir = root_dir+'\\_results'
    pattern = 'ZH026'
    params = {
        'root_dir': root_dir,
        'pattern': pattern,
        'save_dir': save_dir
    }
    return params


def on_press(key, hl):
    # print(key)
    try:
        if key.char == 's':
            # print('seams')
            hl.append('Seams')
        elif key.char == 'n':
            # print('no seams')
            hl.append('No Seams')
        elif key.char == 'd':
            # print('doubt')
            hl.append('Doubt')
        else:
            pass

    except AttributeError:
        # print('special key {0} pressed'.format(key))
        pass


def on_release(key):
    global i

    try:
        if key.char == 's':
            human_label[i] = 'Seams'
            i += 1
        elif key.char == 'n':
            human_label[i] = 'No Seams'
            i += 1
        elif key.char == 'd':
            human_label[i] = 'Doubt'
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

    display_im(params['root_dir'], df, i, n_images)


if __name__ == '__main__':

    params = main()
    df = create_df(params)
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
    # lastname = os.path.join(os.getcwd(), 'Validation_Seams', 'Validation03_2022_10_26', params['pattern']+'.csv')
    lastname = params['save_dir']+'_'+params['pattern']+'.csv'
    df.to_csv(lastname, index=False)


