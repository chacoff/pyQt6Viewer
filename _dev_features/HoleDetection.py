import cv2
import numpy as np
import os

src = 'ZH022_3200_144850_Hole.bmp'
folder_path = 'C:\\Users\\gomezja\\PycharmProjects\\00_dataset\\Hole'  # Replace this with the path to your folder

bmp_images_above_1024kb = []

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".bmp"):
        file_path = os.path.join(folder_path, filename)
        file_size_kb = os.stat(file_path).st_size / 1024  # Get file size in KB
        if file_size_kb > 1024:
            bmp_images_above_1024kb.append(file_path)


for src in bmp_images_above_1024kb:
    mat = cv2.imread(src)
    mat_org = mat.copy()
    mat = mat[0:3000, 400:2300]  # y:y+h, x:x+w if ROI needed

    gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
    dilated_image = cv2.dilate(binary, np.ones((3, 3), np.uint8), iterations=2)
    eroded_image = cv2.erode(binary, np.ones((3, 3), np.uint8), iterations=2)
    merged_image = cv2.bitwise_or(dilated_image, eroded_image)

    # cv2.imshow('', cv2.resize(binary, None, fx=0.20, fy=0.30))
    # cv2.waitKey()

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 500:
            x, y, w, h = cv2.boundingRect(contour)
            dx_dy_ratio = w / h
            if dx_dy_ratio > 0.5:
                filtered_contours.append(contour)

    if len(filtered_contours) > 0:
        biggest_contour = max(filtered_contours, key=cv2.contourArea)
        filtered_contours = [biggest_contour]

    cv2.drawContours(mat, filtered_contours, -1, (0, 255, 0), 2)

    cv2.imshow('', cv2.resize(np.hstack((mat_org, mat)), None, fx=0.20, fy=0.30))
    cv2.waitKey()
    cv2.destroyAllWindows()
