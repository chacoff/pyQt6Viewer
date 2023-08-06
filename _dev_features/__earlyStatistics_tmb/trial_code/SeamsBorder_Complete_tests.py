import cv2
import numpy as np
import matplotlib.pyplot as plt


def BorderDetectionCanny(source_channel, kern=3, low_thresh=30, high_thresh=230):

    median = cv2.medianBlur(source_channel.copy(), kern)  # Filters to denoise the image
    denoise = cv2.GaussianBlur(median, (kern, kern), 0)

    canny = cv2.Canny(denoise, low_thresh, high_thresh)  # for border detection

    # [0] instead of using hierarchy for findContours()
    contours = cv2.findContours(canny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

    return contours


def img_is_color(img):

    try:
        if len(img.shape) == 3:
            # Check the color channels to see if they're all the same.
            c1, c2, c3 = img[:, :, 0], img[:, :, 1], img[:, :, 2]
            if (c1 == c2).all() and (c2 == c3).all():
                return True
    except:
        pass

    return False


def show_image_list(list_images, list_titles=None, list_cmaps=None, grid=True, num_cols=2, figsize=(14, 7),
                    title_fontsize=12):
    '''
    Shows a grid of images, where each image is a Numpy array. The images can be either
    RGB or grayscale.

    Parameters:
    ----------
    images: list
        List of the images to be displayed.
    list_titles: list or None
        Optional list of titles to be shown for each image.
    list_cmaps: list or None
        Optional list of cmap values for each image. If None, then cmap will be
        automatically inferred.
    grid: boolean
        If True, show a grid over each image
    num_cols: int
        Number of columns to show.
    figsize: tuple of width, height
        Value to be passed to pyplot.figure()
    title_fontsize: int
        Value to be passed to set_title().
    '''

    assert isinstance(list_images, list)
    assert len(list_images) > 0
    assert isinstance(list_images[0], np.ndarray)

    if list_titles is not None:
        assert isinstance(list_titles, list)
        assert len(list_images) == len(list_titles), '%d imgs != %d titles' % (len(list_images), len(list_titles))

    if list_cmaps is not None:
        assert isinstance(list_cmaps, list)
        assert len(list_images) == len(list_cmaps), '%d imgs != %d cmaps' % (len(list_images), len(list_cmaps))

    num_images = len(list_images)
    num_cols = min(num_images, num_cols)
    num_rows = int(num_images / num_cols) + (1 if num_images % num_cols != 0 else 0)

    # Create a grid of subplots.
    fig, axes = plt.subplots(num_rows, num_cols, figsize=figsize)

    # Create list of axes for easy iteration.
    if isinstance(axes, np.ndarray):
        list_axes = list(axes.flat)
    else:
        list_axes = [axes]

    for i in range(num_images):
        img = list_images[i]

        try:
            if len(img.shape) == 3:  # it means it has 3 channels
                bl, gr, re = cv2.split(img)  # get b,g,r
                img = cv2.merge([re, gr, bl])  # switch it to rgb
        except:
            img = img

        title = list_titles[i] if list_titles is not None else 'Image %d' % (i)
        cmap = list_cmaps[i] if list_cmaps is not None else (None if img_is_color(img) else 'gray')
        list_axes[i].imshow(img, cmap=cmap)

        list_axes[i].set_title(title, fontsize=title_fontsize)
        list_axes[i].grid(grid)

    for i in range(num_images, len(list_axes)):
        list_axes[i].set_visible(False)

    fig.tight_layout()
    _ = plt.show()


def main():
    pass


if __name__ == '__main__':

    main()

    source = cv2.imread('ZH012_2041_089000_TX000008.bmp', 0)  # read already in 8bit

    try:
        r, g, b = cv2.split(source)[:3]  # splitting in RGB channels
    except ValueError as e:
        print(f'{e}: Using the source image as input channel')
    finally:
        r = source.copy()

    height, width = r.shape

    scale_percent = 100  # percent of original size
    new_width = int(r.shape[1] * scale_percent / 100)
    new_height = int(r.shape[0] * scale_percent / 100)

    r_resized = cv2.resize(r, (new_width, new_height), interpolation=cv2.INTER_AREA)

    median = cv2.medianBlur(r_resized.copy(), 7)  # Filters to denoise the image
    r_denoise = cv2.GaussianBlur(median, (7, 7), 0)

    gx, gy = np.gradient(r_denoise)
    gr = abs(np.gradient(gy[50]))
    gr = np.where(gr <= 2.0, 0, gr)
    gr_x = np.arange(0, len(gr)) * 1 + 1

    fig = plt.figure()

    fig.add_subplot(2, 2, 1)
    plt.imshow(r_resized, cmap='gray', aspect="auto")
    plt.axis('off')
    plt.title('Original')

    fig.add_subplot(2, 2, 2)
    plt.imshow(r_denoise, cmap='gray', aspect="auto")
    plt.axis('off')
    plt.title('Denoise')

    fig.add_subplot(2, 2, 3)
    plt.imshow(gy, cmap='gray', aspect="auto")
    plt.axis('off')
    plt.title('gradient on Y')

    fig.add_subplot(2, 2, 4)
    plt.plot(gr_x, gr)
    # plt.axis('off')
    plt.title('plot of gradient on Y')

    plt.show()

    '''
    Imgs2Plot = [r_resized, r_denoise, gy]
    ImgsTitle = ['Original', 'Denoise', 'gradient on Y']

    show_image_list(list_images=Imgs2Plot,
                    list_titles=ImgsTitle,
                    # list_cmaps=['gray', 'viridis', 'viridis'],
                    figsize=(10, 8),
                    grid=False,
                    title_fontsize=12)
    '''

    '''
    # saturated pixels to black
    source[np.all(source >= (180, 180, 180), axis=-1)] = (200, 200, 200)

    r, g, b = cv2.split(source)[:3]  # splitting in RGB channels

    height, width, channels = source.shape
    scale_percent = 30  # percent of original size
    new_width = int(r.shape[1] * scale_percent / 100)
    new_height = int(r.shape[0] * scale_percent / 100)
    r_resized = cv2.resize(r, (new_width, new_height), interpolation=cv2.INTER_AREA)

    blank_image = np.zeros((new_height, new_width, channels), np.uint8)  # canvas2draw

    # contours = BorderDetectionCanny(r, kern=3, low_thresh=30, high_thresh=230)

    ret, thresh = cv2.threshold(r_resized, 137, 255, 0)
    # thresh = cv2.adaptiveThreshold(r_resized, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    contours, hierarchy = cv2.findContours(thresh, 1, 3)

    for i in range(len(contours)):
        cnt = contours[i]

        # M = cv2.moments(cnt)
        # print(M)
        # cx = int(M['m10'] / M['m00'])
        # cy = int(M['m01'] / M['m00'])

        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if (area >= 5.0) and (perimeter >= 5.0):
            epsilon = 0.2 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # cv2.drawContours(blank_image, approx, -1, (255, 255, 255), 2)  # [contours] to draw
            x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(blank_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('', blank_image)
    cv2.waitKey()
    '''
