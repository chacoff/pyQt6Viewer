from imutils import paths
import argparse
import cv2


# compute the Laplacian of the image and then return the focus measure, which is simply the variance of the Laplacian
def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def main():
    pass


if __name__ == '__main__':
    main()

    # parameters
    image_path = 'flange_ok.png'
    threshold = 1100

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    result = 'Blurry' if fm > threshold else 'Not Blurry'  # normally, with blurry images the laplacian gets smaller

    cv2.putText(image, "{}: {:.2f}".format(result, fm), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 3)
    cv2.imshow("Image", image)
    cv2.waitKey(0)