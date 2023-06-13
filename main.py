from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices
import sys


class ImageView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.zoom_factor = 1.0
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def display_image(self, image_path):

        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image)

        self.scene.clear()
        scaled_pixmap = pixmap.scaledToHeight(pixmap.height())
        self.scene.addPixmap(scaled_pixmap)
        # self.setZoomFactor(1.0)
        self.setCenter(QPointF(0, 0))

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.zoom_factor *= zoom_in_factor
        else:
            self.zoom_factor *= zoom_out_factor

        self.setZoomFactor(self.zoom_factor)

    def setZoomFactor(self, zoom_factor):
        self.resetTransform()
        self.scale(zoom_factor, zoom_factor)

    def setCenter(self, pos):
        self.centerOn(pos)


class ImageInfo(QWidget):

    def __init__(self):
        super().__init__()

        self.model_name = QLabel('model: *.onnx')
        self.image_name_label = QLabel('image name')

        layout = QVBoxLayout()
        layout.addWidget(self.model_name)
        layout.addWidget(self.image_name_label)

        self.setLayout(layout)

    def update_image_name(self, image_name):
        self.image_name_label.setText(image_name)

    def update_model_name(self, model_name):
        self.model_name.setText(model_name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_files = []
        self.current_image_index = 0

        toolbar = self.addToolBar('File')
        browse_action = QAction("Browse", self)
        browse_action.triggered.connect(self.browse_folder)
        browse_action.setShortcut('o')
        process_action = QAction("Process", self)
        process_action.setShortcut('p')
        model_action = QAction("Model", self)
        model_action.triggered.connect(self.browse_model)
        model_action.setShortcut('m')
        previous_action = QAction("< Previous", self)
        previous_action.triggered.connect(self.show_previous_image)
        previous_action.setShortcut('a')
        next_action = QAction("Next >", self)
        next_action.triggered.connect(self.show_next_image)
        next_action.setShortcut('d')
        toolbar.addAction(browse_action)
        toolbar.addAction(process_action)
        toolbar.addAction(model_action)
        toolbar.addAction(previous_action)
        toolbar.addAction(next_action)

        toolbar.setStyleSheet('''
            QToolBar {
                background-color: #f2f2f2;
                border: 1px;
                spacing: 6px;
                margin-top: 6px;
                padding-top: 4px;
            }

            QToolBar QToolButton {
                background-color: #d3d3d3;
                padding: 6px;
                border: none;
                border-radius: 4px;
                color: #333333;
            }

            QToolBar QToolButton:hover {
                background-color: #c0c0c0;
            }

            QToolBar QToolButton:pressed {
                background-color: #a8a8a8;
            }
        ''')

        self.panel_view = ImageView()
        self.panel_info = ImageInfo()
        self.setWindowTitle('Seams Viewer')

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
            self.panel_view.display_image(self.filename())
            self.panel_info.update_image_name(QFileInfo(self.filename()).baseName())

    def browse_model(self):
        model_path = QFileDialog.getOpenFileName(self, 'Choose Onnx Model', '', 'Onnx files (*.onnx)')

        if not model_path:
            return

        model_name = QFileInfo(model_path[0]).baseName()
        self.panel_info.update_model_name(f'model: {model_name}')

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.panel_view.display_image(self.filename())
            self.panel_info.update_image_name(QFileInfo(self.filename()).baseName())

    def show_next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.panel_view.display_image(self.filename())
            self.panel_info.update_image_name(QFileInfo(self.filename()).baseName())

    def filename(self):
        return self.image_files[self.current_image_index]


if __name__ == '__main__':

    app = QApplication(sys.argv)

    image_window = MainWindow()

    #palette = image_window.palette()
    #palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
    #image_window.setPalette(palette)

    image_window.show()
    image_window.resize(QSize(800, 600))
    sys.exit(app.exec())
