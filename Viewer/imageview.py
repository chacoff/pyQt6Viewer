import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem, QGraphicsPolygonItem
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl, QRectF
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon, QPen, QPolygonF, QBrush
import sys
import numpy as np
import os


class Annotation:
    def __init__(self, points: np.array, label: str, color: QColor) -> None:
        self._points: np.array = points
        self._label: str = label
        self._color: QColor = color

    @property
    def points(self) -> np.array:
        return self._points

    @property
    def label(self) -> str:
        return self._label

    @property
    def color(self) -> QColor:
        return self._color


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
        self.polygon_items = []
        self.yolo_items = []

    def draw_annotations(self, annotations: list):
        """ draw Infoscribe CVAT annotations around the detected defects """

        self.remove_existing_items()

        for annotation in annotations:
            _points = annotation._points
            _points_array = self.points_to_points_array(_points)
            _color = annotation._color
            _r, _g, _b, _ = _color.getRgb()
            _color_alpha = QColor(_r, _g, _b, 64)

            polygon = QPolygonF()

            for p in _points_array:
                polygon.append(QPointF(*p))

            item = QGraphicsPolygonItem(polygon)
            pen = QPen(_color)
            pen.setWidth(0)
            item.setPen(pen)

            brush = QBrush(_color_alpha)
            item.setBrush(brush)

            self.scene.addItem(item)
            self.polygon_items.append(item)

    def draw_yolo_annotation(self, _folder_path: str, _current_image: str, _current_annotation: str, _colors: list):
        """ draw yolo annotations exported from infoscribe format """

        self.remove_existing_items()

        with open(os.path.join(_folder_path, _current_annotation), 'r') as file:
            for _line in file:
                line = _line.split(' ')
                _yolov = [float(x) for x in line]

                left, top, right, bottom = self.convert_yolo_to_tlbr(_yolov, self.width, self.height)

                rect_item = QGraphicsRectItem(QRectF(QPointF(top, left), QPointF(bottom, right)))
                pen = QPen(_colors[int(_yolov[0])])
                pen.setWidth(0)
                rect_item.setPen(pen)

                self.scene.addItem(rect_item)
                self.yolo_items.append(rect_item)

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

        for item in self.polygon_items:
            self.scene.removeItem(item)
        self.polygon_items = []

        for item in self.yolo_items:
            self.scene.removeItem(item)
        self.yolo_items = []

    def show_hide_items(self, _visible: bool):

        for item in self.rect_items:
            item.setVisible(_visible)

        for item in self.polygon_items:
            item.setVisible(_visible)

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

    @staticmethod
    def points_to_points_array(points) -> np.array:
        """ CVAT polygons to a numpy array """
        points_array = np.empty((len(points), 2), dtype=np.float64)

        for i, point_str in enumerate(points):
            x_str, y_str = point_str.split(',')
            x = float(x_str)
            y = float(y_str)
            points_array[i] = [x, y]

        points_array = np.array(points_array)

        return points_array

    @staticmethod
    def convert_yolo_to_tlbr(yolo_annotation: list, image_width: int, image_height: int) -> tuple:
        """ convert from YOLO format to standard BBox in order to draw it with qt"""
        class_id, x_center, y_center, width, height = yolo_annotation

        x_center = x_center * image_width
        y_center = y_center * image_height
        width = width * image_width
        height = height * image_height

        top = y_center - height / 2
        left = x_center - width / 2
        bottom = y_center + height / 2
        right = x_center + width / 2

        return top, left, bottom, right



