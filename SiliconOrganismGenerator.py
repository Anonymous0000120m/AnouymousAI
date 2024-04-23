import sys
import cv2
import numpy as np
import traceback
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class SiliconOrganismGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Silicon Organism Generator")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        self.btn_select_image = QPushButton("Select Image", self)
        self.btn_select_image.clicked.connect(self.select_image)
        layout.addWidget(self.btn_select_image)

        self.btn_gray_detection = QPushButton("Gray Detection", self)
        self.btn_gray_detection.clicked.connect(self.gray_detection)
        layout.addWidget(self.btn_gray_detection)

        self.btn_edge_detection = QPushButton("Edge Detection", self)
        self.btn_edge_detection.clicked.connect(self.edge_detection)
        layout.addWidget(self.btn_edge_detection)

        self.btn_rgb_processing = QPushButton("RGB Processing", self)
        self.btn_rgb_processing.clicked.connect(self.rgb_processing)
        layout.addWidget(self.btn_rgb_processing)

        self.btn_reset_image = QPushButton("Reset Image", self)
        self.btn_reset_image.clicked.connect(self.reset_image)
        layout.addWidget(self.btn_reset_image)

        self.setLayout(layout)
        self.current_image = None
        self.original_image = None

    def select_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image File", "",
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", options=options)
        if file_name:
            try:
                self.current_image = cv2.imread(file_name)
                self.original_image = self.current_image.copy()
                self.display_image(self.current_image)
            except Exception as e:
                self.create_error_log(e)

    def display_image(self, image):
        if len(image.shape) == 2:  # 如果是灰度图像
            q_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)
        else:
            h, w, ch = image.shape
            bytes_per_line = ch * w
            if ch == 3:
                q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_BGR888)
            elif ch == 4:
                q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
    
        # 显示图像
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def gray_detection(self):
        if self.current_image is None:
            return

        # 灰度处理
        gray_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.display_image(gray_image)

    def edge_detection(self):
        if self.current_image is None:
            return

        # 边缘检测
        gray_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, 100, 200)
        self.display_image(edges)

    def rgb_processing(self):
        if self.current_image is None:
            return

        # RGB处理
        rgb_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        self.display_image(rgb_image)

    def reset_image(self):
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)

    def create_error_log(self, exception):
        with open("error_log.txt", "a") as f:
            f.write("Exception occurred:\n")
            f.write(str(exception))
            f.write("\n\n")
        traceback.print_exc(file=open("error_log.txt", "a"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SiliconOrganismGenerator()
    window.show()
    sys.exit(app.exec_())

#end of SiliconOrganismGenerator.py