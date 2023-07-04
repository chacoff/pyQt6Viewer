import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl, QRectF, QEvent, QPoint
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon, QPen, \
    QMouseEvent, QPainterPath
import sys
import numpy


class ImageView(QGraphicsView):

    leftMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    middleMouseButtonPressed = pyqtSignal(float, float)
    middleMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)

    viewChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        # self.scene.setBackgroundBrush(QColor(249, 251, 253, 255))
        self.setScene(self.scene)

        self.zoom_factor = 1.25
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.pixmapItem = self.scene.addPixmap(QPixmap())
        self.scene_pos = QPointF(300, 600)
        self.setZoomFactor(1.0)
        self.centerOn(QPointF(700, 800))

        self.image_cvmat = None
        self.height = None
        self.width = None
        self.channel = None
        self.brightness = 0
        self.rect_items = []

        self.regionZoomButton = Qt.MouseButton.LeftButton  # Drag a zoom box.
        self.zoomOutButton = Qt.MouseButton.RightButton  # Pop end of zoom stack (double click clears zoom stack).
        self.panButton = Qt.MouseButton.MiddleButton  # Drag to pan.
        self.aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio

        self._pixelPosition = QPoint()
        self._scenePosition = QPointF()

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
            pen.setWidth(3)
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

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if len(self.rect_items):
            self.fitInView(self.rect_items[-1], self.aspectRatioMode)  # Show zoomed rect.
        else:
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image.

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        # Ignore dummy events. e.g., Faking pan with left button ScrollHandDrag.
        dummyModifiers = Qt.KeyboardModifier(Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier
                                             | Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.MetaModifier)
        if event.modifiers() == dummyModifiers:
            QGraphicsView.mousePressEvent(self, event)
            event.accept()
            return

        # Start dragging a region zoom box?
        if (self.regionZoomButton is not None) and (event.button() == self.regionZoomButton):
            self._pixelPosition = event.pos()  # store pixel position
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            QGraphicsView.mousePressEvent(self, event)
            event.accept()
            return

        if (self.zoomOutButton is not None) and (event.button() == self.zoomOutButton):
            if len(self.rect_items):
                self.rect_items.pop()
            event.accept()
            return

        # Start dragging to pan?
        if (self.panButton is not None) and (event.button() == self.panButton):
            self._pixelPosition = event.pos()  # store pixel position
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if self.panButton == Qt.MouseButton.LeftButton:
                QGraphicsView.mousePressEvent(self, event)
            else:
                # ScrollHandDrag ONLY works with LeftButton, so fake it.
                # Use a bunch of dummy modifiers to notify that event should NOT be handled as usual.
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                dummyModifiers = Qt.KeyboardModifier(Qt.KeyboardModifier.ShiftModifier
                                                     | Qt.KeyboardModifier.ControlModifier
                                                     | Qt.KeyboardModifier.AltModifier
                                                     | Qt.KeyboardModifier.MetaModifier)
                dummyEvent = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(event.pos()), Qt.MouseButton.LeftButton,
                                         event.buttons(), dummyModifiers)
                self.mousePressEvent(dummyEvent)
            sceneViewport = self.mapToScene(self.viewport().rect()).boundingRect().intersected(self.sceneRect())
            self._scenePosition = sceneViewport.topLeft()
            event.accept()
            self._isPanning = True
            return

        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        # Ignore dummy events. e.g., Faking pan with left button ScrollHandDrag.
        dummyModifiers = Qt.KeyboardModifier(Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier
                                             | Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.MetaModifier)
        if event.modifiers() == dummyModifiers:
            QGraphicsView.mouseReleaseEvent(self, event)
            event.accept()
            return

        # Finish dragging a region zoom box?
        if (self.regionZoomButton is not None) and (event.button() == self.regionZoomButton):
            QGraphicsView.mouseReleaseEvent(self, event)
            zoomRect = self.scene.selectionArea().boundingRect().intersected(self.sceneRect())
            # Clear current selection area (i.e. rubberband rect).
            self.scene.setSelectionArea(QPainterPath())
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            # If zoom box is 3x3 screen pixels or smaller, do not zoom and proceed to process as a click release.
            zoomPixelWidth = abs(event.pos().x() - self._pixelPosition.x())
            zoomPixelHeight = abs(event.pos().y() - self._pixelPosition.y())
            if zoomPixelWidth > 3 and zoomPixelHeight > 3:
                if zoomRect.isValid() and (zoomRect != self.sceneRect()):
                    self.rect_items.append(zoomRect)
                    self.updateViewer()
                    self.viewChanged.emit()
                    event.accept()
                    return

        # Finish panning?
        if (self.panButton is not None) and (event.button() == self.panButton):
            if self.panButton == Qt.MouseButton.LeftButton:
                QGraphicsView.mouseReleaseEvent(self, event)
            else:
                # ScrollHandDrag ONLY works with LeftButton, so fake it.
                # Use a bunch of dummy modifiers to notify that event should NOT be handled as usual.
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                dummyModifiers = Qt.KeyboardModifier(Qt.KeyboardModifier.ShiftModifier
                                                     | Qt.KeyboardModifier.ControlModifier
                                                     | Qt.KeyboardModifier.AltModifier
                                                     | Qt.KeyboardModifier.MetaModifier)
                dummyEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(event.pos()),
                                         Qt.MouseButton.LeftButton, event.buttons(), dummyModifiers)
                self.mouseReleaseEvent(dummyEvent)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            if len(self.rect_items) > 0:
                sceneViewport = self.mapToScene(self.viewport().rect()).boundingRect().intersected(self.sceneRect())
                delta = sceneViewport.topLeft() - self._scenePosition
                self.rect_items[-1].translate(delta)
                self.rect_items[-1] = self.rect_items[-1].intersected(self.sceneRect())
                self.viewChanged.emit()
            event.accept()
            self._isPanning = False
            return

        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

        QGraphicsView.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        # zoom_in_factor = 1.15
        # zoom_out_factor = 1 / zoom_in_factor
        #
        # if event.angleDelta().y() > 0:
        #     self.zoom_factor *= zoom_in_factor
        # else:
        #     self.zoom_factor *= zoom_out_factor
        # self.scene_pos = event.position() # @TODO zoom in and out according mouse pointer
        # print(self.zoom_factor)
        # self.setZoomFactor(self.zoom_factor)

        if self.zoom_factor is not None:
            if self.zoom_factor == 1:
                return
            if event.angleDelta().y() > 0:
                # zoom in
                if len(self.rect_items) == 0:
                    self.rect_items.append(self.sceneRect())
                elif len(self.rect_items) > 1:
                    del self.rect_items[:-1]
                zoomRect = self.rect_items[-1]
                center = zoomRect.center()
                zoomRect.setWidth(zoomRect.width() / self.zoom_factor)
                zoomRect.setHeight(zoomRect.height() / self.zoom_factor)
                zoomRect.moveCenter(center)
                self.rect_items[-1] = zoomRect.intersected(self.sceneRect())
                self.updateViewer()
                self.viewChanged.emit()
            else:
                # zoom out
                if len(self.rect_items) == 0:
                    return
                if len(self.rect_items) > 1:
                    del self.rect_items[:-1]
                zoomRect = self.rect_items[-1]
                center = zoomRect.center()
                zoomRect.setWidth(zoomRect.width() * self.zoom_factor)
                zoomRect.setHeight(zoomRect.height() * self.zoom_factor)
                zoomRect.moveCenter(center)
                self.rect_items[-1] = zoomRect.intersected(self.sceneRect())
                if self.rect_items[-1] == self.sceneRect():
                    self.rect_items = []
                self.updateViewer()
                self.viewChanged.emit()
            event.accept()
            return

        QGraphicsView.wheelEvent(self, event)

    def setZoomFactor(self, zoom_factor):
        self.resetTransform()
        self.scale(zoom_factor, zoom_factor)

    def setImageinCenter(self):
        if not self.pixmapItem.pixmap().isNull():
            self.fitInView(self.pixmapItem, Qt.AspectRatioMode.IgnoreAspectRatio)
            self.zoom_factor = 1.25

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

