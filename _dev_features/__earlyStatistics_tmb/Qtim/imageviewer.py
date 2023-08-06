# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import os
import pathlib
import pandas as pd
from natsort import natsorted
from datetime import datetime
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QLabel,
                               QMainWindow, QMessageBox, QScrollArea,
                               QSizePolicy, QLineEdit, QInputDialog)
from PySide6.QtGui import (QColorSpace, QGuiApplication,
                           QImageReader, QImageWriter, QKeySequence,
                           QPalette, QPainter, QPixmap, QIcon)
from PySide6.QtCore import QDir, QStandardPaths, Qt, Slot, QSettings


ABOUT = '''<p>TMB <b>Manual Classifier</b></p>
<p>Open a folder to create a list with all images</p>
<p><b>S</b> to classify as Seams</p>
<p><b>D</b> to classify as no Seams</p>
<p>Use arrows to move around the images without classification</p>
'''


class SupportFunctions:
    def __init__(self, parent=None):
        super().__init__(parent)

    @staticmethod
    def images_list(folder_selected, suffix='.BMP'):
        for path, dirs, files in os.walk(folder_selected):
            yield from (path+'/'+file for file in files if pathlib.Path(file).suffix == suffix)

    @staticmethod
    def right_now():
        timestamp = datetime.timestamp(datetime.now())
        date_time = datetime.fromtimestamp(timestamp)
        str_date_time = date_time.strftime("%Y%m%d-%H%M")  # %d-%m-%Y-%H%M%S
        return str_date_time

    @staticmethod
    def unique_file(path):
        filename, extension = os.path.splitext(path)
        counter = 1
        while os.path.exists(path):
            path = filename + '_' + str(counter) + extension
            counter += 1
        return path

    @staticmethod
    def frame_creator(f_list):
        batch_images = []
        for filename in f_list:
            label = '-not processed-'
            human_label = '-manual-'
            name = filename.split('/')[-1]
            location = filename.split('/')[:-1]
            location[0] = location[0]+'\\'
            location = os.path.join(*location)

            batch_images.append((name, label, human_label, location))

        df = pd.DataFrame(batch_images, columns=['ImageName', 'Label', 'HumanLabel', 'Location'])
        return df


class ImageViewer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.n_image = 0
        self.suffix = '.bmp'
        self._scale_factor = 1.0
        self._first_file_dialog = True
        self._image_label = QLabel()
        self._image_label.setBackgroundRole(QPalette.Base)
        self._image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._image_label.setScaledContents(True)

        self._scroll_area = QScrollArea()
        self._scroll_area.setBackgroundRole(QPalette.Dark)
        self._scroll_area.setWidget(self._image_label)
        self._scroll_area.setVisible(False)
        self.setCentralWidget(self._scroll_area)

        self._create_actions()
        my_icon = QIcon()
        my_icon.addFile('icon.png')
        self.setWindowIcon(my_icon)
        self.setWindowTitle('ImageSorter v0.1')
        self.showMaximized()
        # self.showFullScreen()
        # self.resize(QGuiApplication.primaryScreen().availableSize() * 0.85)

    def load_file(self, fileName):
        reader = QImageReader(fileName)
        reader.setAutoTransform(True)
        new_image = reader.read()
        native_filename = QDir.toNativeSeparators(fileName)
        if new_image.isNull():
            error = reader.errorString()
            QMessageBox.information(self, QGuiApplication.applicationDisplayName(),
                                    f"Cannot load {native_filename}: {error}")
            return False
        self._set_image(new_image)
        self.setWindowFilePath(fileName)
        final_native_filename = native_filename.split('\\')[-1]
        w = self._image.width()
        h = self._image.height()
        d = self._image.depth()
        color_space = self._image.colorSpace()
        description = color_space.description() if color_space.isValid() else 'unknown'
        # message = f'{self.n_image+1}/{self.t_image} - Opened "{native_filename}", {w}x{h}, Depth: {d} ({description})'
        message = f'{self.n_image + 1}/{self.t_image} - Opened "{final_native_filename}", {w}x{h}'
        self.statusBar().showMessage(message)
        self.statusBar().setStyleSheet("font: 24px;")

        return True

    def _set_image(self, new_image):
        self._image = new_image
        if self._image.colorSpace().isValid():
            self._image.convertToColorSpace(QColorSpace.SRgb)
        self._image_label.setPixmap(QPixmap.fromImage(self._image))
        self._scale_factor = 1.0

        self._scroll_area.setVisible(True)
        self._print_act.setEnabled(True)
        self._fit_to_window_act.setEnabled(True)
        self._update_actions()

        if not self._fit_to_window_act.isChecked():
            # self._image_label.adjustSize()  # to start with original size
            self._scroll_area.setWidgetResizable(True)  # to start adjusted to the screen

    def _save_file(self, fileName):
        writer = QImageWriter(fileName)

        native_filename = QDir.toNativeSeparators(fileName)
        if not writer.write(self._image):
            error = writer.errorString()
            message = f"Cannot write {native_filename}: {error}"
            QMessageBox.information(self, QGuiApplication.applicationDisplayName(),
                                    message)
            return False
        self.statusBar().showMessage(f'Wrote "{native_filename}"')
        return True

    def _save_dataframe(self,):
        self.dataframe.to_csv(self.results_name, index=False)

    @Slot()
    def _open(self):
        # dialog = QFileDialog(self, "Open File")
        # self._initialize_image_filedialog(dialog, QFileDialog.AcceptOpen)
        # while (dialog.exec() == QDialog.Accepted
        #       and not self.load_file(dialog.selectedFiles()[0])):
        #    pass

        folder_selected = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.file_list = natsorted(list(SupportFunctions.images_list(folder_selected, self.suffix)))
        self.t_image = len(self.file_list)
        self.n_image = 0
        if self.t_image != 0:
            self.load_file(self.file_list[self.n_image])
            self.dataframe = SupportFunctions.frame_creator(self.file_list)
            self.results_name = SupportFunctions.unique_file('results.csv')
            self._save_dataframe()
            print('no mistake')
        else:
            print('mistake')

    @Slot()
    def _save_as(self):
        dialog = QFileDialog(self, "Save File As")
        self._initialize_image_filedialog(dialog, QFileDialog.AcceptSave)
        while (dialog.exec() == QDialog.Accepted
               and not self._save_file(dialog.selectedFiles()[0])):
            pass

    @Slot()
    def _print_(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.Accepted:
            with QPainter(printer) as painter:
                pixmap = self._image_label.pixmap()
                rect = painter.viewport()
                size = pixmap.size()
                size.scale(rect.size(), Qt.KeepAspectRatio)
                painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                painter.setWindow(pixmap.rect())
                painter.drawPixmap(0, 0, pixmap)

    @Slot()
    def _copy(self):
        QGuiApplication.clipboard().setImage(self._image)

    @Slot()
    def _paste(self):
        new_image = QGuiApplication.clipboard().image()
        if new_image.isNull():
            self.statusBar().showMessage("No image in clipboard")
        else:
            self._set_image(new_image)
            self.setWindowFilePath('')
            w = new_image.width()
            h = new_image.height()
            d = new_image.depth()
            message = f"Obtained image from clipboard, {w}x{h}, Depth: {d}"
            self.statusBar().showMessage(message)

    @Slot()
    def _zoom_in(self):
        self._scale_image(1.25)

    @Slot()
    def _zoom_out(self):
        self._scale_image(0.8)

    @Slot()
    def _normal_size(self):
        self._image_label.adjustSize()
        self._scale_factor = 1.0

    @Slot()
    def _fit_to_window(self):
        fit_to_window = self._fit_to_window_act.isChecked()
        self._scroll_area.setWidgetResizable(fit_to_window)
        if not fit_to_window:
            self._normal_size()
        self._update_actions()

    @Slot()
    def _about(self):
        QMessageBox.about(self, "about", ABOUT)

    @Slot()
    def _next_image(self):
        if self.n_image < self.t_image-1:
            self.n_image += 1
            self.load_file(self.file_list[self.n_image])
        else:
            QMessageBox.information(self, "info", 'This is the last image')

    @Slot()
    def _previous_image(self):
        if self.n_image > 0:
            self.n_image -= 1
            self.load_file(self.file_list[self.n_image])
        else:
            QMessageBox.information(self, 'info', 'This is the first image')

    @Slot()
    def _seams_yes(self):
        # QMessageBox.about(self, "seams", 'Seams')
        self.dataframe.iloc[self.n_image]['HumanLabel'] = 'Seams'
        self._save_dataframe()
        self._next_image()

    @Slot()
    def _seams_no(self):
        self.dataframe.iloc[self.n_image]['HumanLabel'] = 'NoSeams'
        self._save_dataframe()
        self._next_image()

    @Slot()
    def _settings(self):
        self.suffix, ok = QInputDialog.getText(self, "Choose image extension",
                                        "Enter the image extension: .bmp, .jpg, .png, etc ...:",
                                        QLineEdit.Normal, '.bmp')

    def _create_actions(self):
        file_menu = self.menuBar().addMenu("&File")

        self._open_act = file_menu.addAction('&Extension')
        self._open_act.triggered.connect(self._settings)
        self._open_act.setShortcut('Ctrl+E')

        self._open_act = file_menu.addAction("&Open folder...")
        self._open_act.triggered.connect(self._open)
        self._open_act.setShortcut(QKeySequence.Open)

        self._save_as_act = file_menu.addAction("&Save As...")
        self._save_as_act.triggered.connect(self._save_as)
        self._save_as_act.setEnabled(False)

        self._print_act = file_menu.addAction("&Print...")
        self._print_act.triggered.connect(self._print_)
        self._print_act.setShortcut(QKeySequence.Print)
        self._print_act.setEnabled(False)

        file_menu.addSeparator()

        self._exit_act = file_menu.addAction("E&xit")
        self._exit_act.triggered.connect(self.close)
        self._exit_act.setShortcut("Ctrl+Q")

        controls_menu = self.menuBar().addMenu("&Controls")

        self._open_act = controls_menu.addAction("&Seams image")
        self._open_act.triggered.connect(self._seams_yes)
        self._open_act.setShortcut('S')

        self._open_act = controls_menu.addAction("&No Seams image")
        self._open_act.triggered.connect(self._seams_no)
        self._open_act.setShortcut('D')

        self._open_act = controls_menu.addAction("&Next image")
        self._open_act.triggered.connect(self._next_image)
        self._open_act.setShortcut('RIGHT')

        self._open_act = controls_menu.addAction("&Previous image")
        self._open_act.triggered.connect(self._previous_image)
        self._open_act.setShortcut('LEFT')

        edit_menu = self.menuBar().addMenu("&Edit")

        self._copy_act = edit_menu.addAction("&Copy")
        self._copy_act.triggered.connect(self._copy)
        self._copy_act.setShortcut(QKeySequence.Copy)
        self._copy_act.setEnabled(False)

        self._paste_act = edit_menu.addAction("&Paste")
        self._paste_act.triggered.connect(self._paste)
        self._paste_act.setShortcut(QKeySequence.Paste)

        view_menu = self.menuBar().addMenu("&View")

        self._zoom_in_act = view_menu.addAction("Zoom &In (25%)")
        self._zoom_in_act.setShortcut(QKeySequence.ZoomIn)
        self._zoom_in_act.triggered.connect(self._zoom_in)
        self._zoom_in_act.setEnabled(False)

        self._zoom_out_act = view_menu.addAction("Zoom &Out (25%)")
        self._zoom_out_act.triggered.connect(self._zoom_out)
        self._zoom_out_act.setShortcut(QKeySequence.ZoomOut)
        self._zoom_out_act.setEnabled(False)

        self._normal_size_act = view_menu.addAction("&Normal Size")
        self._normal_size_act.triggered.connect(self._normal_size)
        self._normal_size_act.setShortcut("Ctrl+N")
        self._normal_size_act.setEnabled(False)

        view_menu.addSeparator()

        self._fit_to_window_act = view_menu.addAction("&Fit to Window")
        self._fit_to_window_act.triggered.connect(self._fit_to_window)
        self._fit_to_window_act.setEnabled(False)
        self._fit_to_window_act.setCheckable(True)
        self._fit_to_window_act.setShortcut("Ctrl+F")

        help_menu = self.menuBar().addMenu("&Help")

        about_act = help_menu.addAction("&About")
        about_act.triggered.connect(self._about)
        # about_qt_act = help_menu.addAction("About &Qt")
        # about_qt_act.triggered.connect(QApplication.aboutQt)

    def _update_actions(self):
        has_image = not self._image.isNull()
        self._save_as_act.setEnabled(has_image)
        self._copy_act.setEnabled(has_image)
        enable_zoom = not self._fit_to_window_act.isChecked()
        self._zoom_in_act.setEnabled(enable_zoom)
        self._zoom_out_act.setEnabled(enable_zoom)
        self._normal_size_act.setEnabled(enable_zoom)

    def _scale_image(self, factor):
        self._scale_factor *= factor
        new_size = self._scale_factor * self._image_label.pixmap().size()
        self._image_label.resize(new_size)

        self._adjust_scrollbar(self._scroll_area.horizontalScrollBar(), factor)
        self._adjust_scrollbar(self._scroll_area.verticalScrollBar(), factor)

        self._zoom_in_act.setEnabled(self._scale_factor < 3.0)
        self._zoom_out_act.setEnabled(self._scale_factor > 0.333)

    def _adjust_scrollbar(self, scrollBar, factor):
        pos = int(factor * scrollBar.value()
                  + ((factor - 1) * scrollBar.pageStep() / 2))
        scrollBar.setValue(pos)

    def _initialize_image_filedialog(self, dialog, acceptMode):
        if self._first_file_dialog:
            self._first_file_dialog = False
            locations = QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)
            directory = locations[-1] if locations else QDir.currentPath()
            dialog.setDirectory(directory)

        mime_types = [m.data().decode('utf-8') for m in QImageWriter.supportedMimeTypes()]
        mime_types.sort()

        dialog.setMimeTypeFilters(mime_types)
        dialog.selectMimeTypeFilter("image/jpeg")
        dialog.setAcceptMode(acceptMode)
        if acceptMode == QFileDialog.AcceptSave:
            dialog.setDefaultSuffix("jpg")