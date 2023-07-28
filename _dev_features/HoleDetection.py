import cv2
import numpy as np
import os
import time


class PostProcessing:
    def __init__(self):
        pass

    def group_rectangles(self, rec: list) -> list:
        """ Union intersecting rectangles
        :param, rec - list of rectangles in form [x, y, w, h]
        :return, list of grouped rectangles
        """
        tested = [False for i in range(len(rec))]
        final = []
        i = 0
        while i < len(rec):
            if not tested[i]:
                j = i+1
                while j < len(rec):
                    if not tested[j] and self._intersect(rec[i], rec[j]):
                        rec[i] = self._union(rec[i], rec[j])
                        tested[j] = True
                        j = i
                    j += 1
                final += [rec[i]]
            i += 1

        return final

    @staticmethod
    def _union(a: list, b: list) -> list:
        """ union of rects """
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = max(a[0] + a[2], b[0] + b[2]) - x
        h = max(a[1] + a[3], b[1] + b[3]) - y

        return [x, y, w, h]

    @staticmethod
    def _intersect(a: list, b: list) -> bool:
        """ intersection of rects """
        x = max(a[0], b[0])
        y = max(a[1], b[1])
        w = min(a[0] + a[2], b[0] + b[2]) - x
        h = min(a[1] + a[3], b[1] + b[3]) - y
        if h < 0:  # in original code :  if w<0 or h<0:
            return False

        return True

    @staticmethod
    def morphos(binary: np.array, kernel: int = 3, iterations: int = 1) -> np.array:
        """ apply morpho operations to a binary image """
        dilated_image = cv2.dilate(binary, np.ones((kernel, kernel), np.uint8), iterations=iterations)
        eroded_image = cv2.erode(binary, np.ones((kernel, kernel), np.uint8), iterations=iterations)
        merged_image = cv2.bitwise_or(dilated_image, eroded_image)

        return merged_image

    @staticmethod
    def blur_image(gray_image: np.array, kernel: int = 5) -> np.array:
        """ gaussian blur to a gray image"""
        return cv2.GaussianBlur(gray_image, (kernel, kernel), 0)

    @staticmethod
    def thresholding(gray_image: np.array, low_thres: int = 35, high_thres: int = 255) -> np.array:
        """ return a binary image out of a gray image"""
        _, binary = cv2.threshold(gray_image, low_thres, high_thres, cv2.THRESH_BINARY_INV)

        return binary

    @staticmethod
    def contours_finder(binary: np.array):
        """ return contours out of a binary image"""
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return contours


class HoleDetection:
    def __init__(self):
        self.post_pro = PostProcessing()
        self.image = None

    def process(self,
                input_image: np.array,
                blur_kernel: int = 5,
                low_thres: int = 35,
                high_thres: int = 255,
                min_contour_area: int = 500,
                min_dx_dy: float = 1.4,
                min_box_area: int = 500,
                safe_dx_dy: float = 1.7,
                safe_box_area: int = 600):
        """ input image is a gray image and return a list with boxes (rects)"""

        self.image = input_image.copy()

        gray = self.post_pro.blur_image(self.image, blur_kernel)
        binary = self.post_pro.thresholding(gray, low_thres, high_thres)
        contours = self.post_pro.contours_finder(binary)

        # First filter: remove small shits
        filtered_rects = []
        for contour in contours:
            contour_area = cv2.contourArea(contour)
            rect = cv2.boundingRect(contour)
            x, y, w, h = rect
            dx_dy_ratio = w / h
            box_area = w * h

            if contour_area > min_contour_area and dx_dy_ratio >= min_dx_dy and box_area > min_box_area:
                filtered_rects.append(rect)

        boxes = self.post_pro.group_rectangles(filtered_rects)

        # Second filter: remove big and narrow shits after merging
        filtered_boxes = []
        for box in boxes:
            x, y, w, h = box
            dx_dy_ratio = w / h
            box_area = w * h
            if dx_dy_ratio >= safe_dx_dy and box_area > safe_box_area:
                filtered_boxes.append(box)

        return filtered_boxes


def generate_image_list(folder_path: str) -> list:
    """" find the images to process """
    images_list = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".bmp"):
            file_path = os.path.join(folder_path, filename)
            file_size_kb = os.stat(file_path).st_size / 1024  # Get file size in KB
            if file_size_kb > 1024:
                images_list.append(file_path)

    return images_list


def main(images_list: list) -> None:
    hole_detector = HoleDetection()

    for src in images_list:
        mat = cv2.imread(src)
        mat_org = mat.copy()
        mat = mat[0:3000, 600:2300]  # y:y+h, x:x+w if crop needed
        gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)

        start_time = time.time()
        boxes = hole_detector.process(gray,
                                      blur_kernel=5,
                                      low_thres=35,
                                      high_thres=255,
                                      min_contour_area=500,
                                      min_dx_dy=1.4,
                                      min_box_area=500,
                                      safe_dx_dy=1.7,
                                      safe_box_area=600)

        t = round((time.time() - start_time) * 1000, 2)

        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                x, y, w, h = box
                print("Hole --- %s ms ---" % t)
                cv2.rectangle(mat, (x, y), (x + w, y + h), (0, 0, 255), 2)

        mat = cv2.rotate(mat, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow('', cv2.resize(mat, None, fx=0.60, fy=0.40))  # np.hstack((mat, mat))
        cv2.waitKey()
        cv2.destroyAllWindows()


if __name__ == '__main__':

    bmp_images_above_1024kb = generate_image_list('D:\\Projects\\00_Datasets\\Hole')
    main(bmp_images_above_1024kb)


