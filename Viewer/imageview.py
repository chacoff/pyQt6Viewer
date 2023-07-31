import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl, QRectF
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon, QPen
import sys
import numpy


class ImageView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        # self.scene.setBackgroundBrush(QColor(249, 251, 253, 255))
        self.setScene(self.scene)

        self.zoom_factor = 1.0
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.pixmapItem = self.scene.addPixmap(QPixmap())
        self.scene_pos = QPointF(0, 0)
        self.setZoomFactor(1.0)
        self.centerOn(QPointF(0, 0))

        self.image_cvmat = None
        self.height = None
        self.width = None
        self.channel = None
        self.brightness = 0
        self.rect_items = []

    def draw_boxes_and_labels(self, predictions, colors):
        """ draw bounding boxes around the detected defects """

        self.remove_existing_items()

        for i in range(len(predictions)):

            left = predictions[i].bbox[1]
            top = predictions[i].bbox[0]
            right = predictions[i].bbox[3]
            bottom = predictions[i].bbox[2]

            rect_item = QGraphicsRectItem(QRectF(QPointF(top, left), QPointF(bottom, right)))
            tool_tip = "{} - {:.2f}".format(predictions[i].class_name, predictions[i].confidence)
            rect_item.setToolTip(tool_tip)
            pen = QPen(colors[predictions[i].class_id])
            pen.setWidth(0)
            rect_item.setPen(pen)

            self.scene.addItem(rect_item)
            self.rect_items.append(rect_item)

    def remove_existing_items(self):
        for item in self.rect_items:
            self.scene.removeItem(item)
        self.rect_items = []

    def display_image(self, image_path):
        """" load an image and update the scene: removes all rect_items and sets a new photo """

        self.remove_existing_items()

        self.image_cvmat = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.image_cvmat = cv2.cvtColor(self.image_cvmat, cv2.COLOR_BGR2RGB)  # if RGB
        self.updateImageItem()
        self.setImageinCenter()

    def updateImageItem(self):
        """ apply brightness and convert from cvmat to QImage """

        output_cvmat = self.image_cvmat.copy()

        # Apply brightness
        hsv = cv2.cvtColor(output_cvmat, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, self.brightness)
        v[v > 255] = 255
        v[v < 0] = 0
        final_hsv = cv2.merge((h, s, v))
        output_cvmat = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

        # Convert and display from CvMAT to QImage
        self.height, self.width, self.channel = output_cvmat.shape
        bytesPerLine = 3 * self.width  # attention with the number of channels
        qImg = QImage(output_cvmat.data, self.width, self.height, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.pixmapItem.setPixmap(pixmap)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.zoom_factor *= zoom_in_factor
        else:
            self.zoom_factor *= zoom_out_factor

        self.scene_pos = event.position()  # @TODO zoom in and out according mouse pointer
        self.setZoomFactor(self.zoom_factor)

    def setZoomFactor(self, zoom_factor):
        self.resetTransform()
        self.scale(zoom_factor, zoom_factor)

    def setImageinCenter(self):
        if not self.pixmapItem.pixmap().isNull():
            self.fitInView(self.pixmapItem, Qt.AspectRatioMode.IgnoreAspectRatio)
            self.zoom_factor = 1

    def set_brightness(self, value):
        """ set the brightness of the current displayed image"""
        if self.image_cvmat is None:
            return

        if value != self.brightness:
            self.brightness = value
            self.updateImageItem()

        if value == 0:
            self.brightness = 0
            self.updateImageItem()

