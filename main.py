from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction
import sys


class ImageView(QGraphicsView):
    image_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Set up initial zoom level and position
        self.zoom_factor = 1.0
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def display_image(self, image_path):

        image = QImage(image_path)

        # Create a pixmap from the image
        pixmap = QPixmap.fromImage(image)

        # Set the pixmap on the scene
        self.scene.clear()
        self.scene.addPixmap(pixmap)

        # Set the initial zoom level and position
        self.setZoomFactor(1.0)
        self.setCenter(QPointF(0, 0))

    def wheelEvent(self, event):
        # Zoom in or out based on the mouse wheel event
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.zoom_factor *= zoom_in_factor
        else:
            self.zoom_factor *= zoom_out_factor

        self.setZoomFactor(self.zoom_factor)

    def setZoomFactor(self, zoom_factor):
        # Set the zoom factor and update the view
        self.resetTransform()
        self.scale(zoom_factor, zoom_factor)

    def setCenter(self, pos):
        # Set the center position of the view
        self.centerOn(pos)

    def keyPressEvent(self, event):
        # Handle key press events
        if event.key() == Qt.Key.Key_Left:
            self.show_previous_image()
        elif event.key() == Qt.Key.Key_Right:
            self.show_next_image()
        else:
            super().keyPressEvent(event)

    def show_previous_image(self):
        # Show the previous image in the folder
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_image(self.image_files[self.current_image_index])

    def show_next_image(self):
        # Show the next image in the folder
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.display_image(self.image_files[self.current_image_index])


class ImageInfo(QWidget):

    def __init__(self):
        super().__init__()

        self.image_name_label = QLabel('image name')
        self.image_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_name_label.setStyleSheet("font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.image_name_label)

        self.setLayout(layout)

    def update_image_name(self, image_name):
        self.image_name_label.setText(image_name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # List of image files in the folder
        self.image_files = []
        self.current_image_index = 0

        toolbar = self.addToolBar('File')
        browse_action = QAction("Browse", self)
        browse_action.triggered.connect(self.browse_folder)
        process_action = QAction("Process", self)
        previous_action = QAction("<< Previous", self)
        next_action = QAction("Next >>", self)
        toolbar.addAction(browse_action)
        toolbar.addAction(process_action)
        toolbar.addAction(previous_action)
        toolbar.addAction(next_action)

        self.panel_view = ImageView()
        self.panel_info = ImageInfo()

        layout = QHBoxLayout()
        layout.addWidget(self.panel_view, 3)
        layout.addWidget(self.panel_info, 1)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

    def browse_folder(self):

        folder_path = QFileDialog.getExistingDirectory(self, "Choose Folder")

        if not folder_path:
            return

        dir = QDir(folder_path)
        dir.setNameFilters(['*.bmp', '*.png'])
        dir.setSorting(QDir.SortFlag.Name)

        self.image_files = [dir.absoluteFilePath(file_name) for file_name in dir.entryList()]

        if self.image_files:
            # Display the first image in the folder
            filename = self.image_files[self.current_image_index]
            self.panel_view.display_image(filename)
            self.panel_info.update_image_name(QFileInfo(filename).baseName())


if __name__ == '__main__':

    app = QApplication(sys.argv)

    image_window = MainWindow()

    #palette = image_window.palette()
    #palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
    #image_window.setPalette(palette)

    image_window.show()
    image_window.resize(QSize(800, 600))
    sys.exit(app.exec())
