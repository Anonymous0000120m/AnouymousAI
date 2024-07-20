#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QFileDialog>
#include <QImage>
#include <QPixmap>
#include <QMessageBox>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <fstream>

class SiliconOrganismGenerator : public QWidget {
    Q_OBJECT
public:
    SiliconOrganismGenerator() {
        setWindowTitle("Silicon Organism Generator");
        setGeometry(100, 100, 800, 600);

        imageLabel = new QLabel(this);
        imageLabel->setAlignment(Qt::AlignCenter);

        QVBoxLayout* layout = new QVBoxLayout();
        layout->addWidget(imageLabel);

        btnSelectImage = new QPushButton("Select Image", this);
        connect(btnSelectImage, &QPushButton::clicked, this, &SiliconOrganismGenerator::selectImage);
        layout->addWidget(btnSelectImage);

        btnGrayDetection = new QPushButton("Gray Detection", this);
        connect(btnGrayDetection, &QPushButton::clicked, this, &SiliconOrganismGenerator::grayDetection);
        layout->addWidget(btnGrayDetection);

        btnEdgeDetection = new QPushButton("Edge Detection", this);
        connect(btnEdgeDetection, &QPushButton::clicked, this, &SiliconOrganismGenerator::edgeDetection);
        layout->addWidget(btnEdgeDetection);

        btnRgbProcessing = new QPushButton("RGB Processing", this);
        connect(btnRgbProcessing, &QPushButton::clicked, this, &SiliconOrganismGenerator::rgbProcessing);
        layout->addWidget(btnRgbProcessing);

        btnResetImage = new QPushButton("Reset Image", this);
        connect(btnResetImage, &QPushButton::clicked, this, &SiliconOrganismGenerator::resetImage);
        layout->addWidget(btnResetImage);

        setLayout(layout);
        currentImage = cv::Mat();
        originalImage = cv::Mat();
    }

private slots:
    void selectImage() {
        QString fileName = QFileDialog::getOpenFileName(this, "Select Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)");
        if (!fileName.isEmpty()) {
            originalImage = cv::imread(fileName.toStdString());
            currentImage = originalImage.clone();
            displayImage(currentImage);
        }
    }

    void grayDetection() {
        if (currentImage.empty()) {
            return;
        }
        cv::cvtColor(currentImage, currentImage, cv::COLOR_BGR2GRAY);
        displayImage(currentImage);
    }

    void edgeDetection() {
        if (currentImage.empty()) {
            return;
        }
        cv::Mat grayImage;
        cv::cvtColor(currentImage, grayImage, cv::COLOR_BGR2GRAY);
        cv::Canny(grayImage, currentImage, 100, 200);
        displayImage(currentImage);
    }

    void rgbProcessing() {
        if (currentImage.empty()) {
            return;
        }
        cv::cvtColor(currentImage, currentImage, cv::COLOR_BGR2RGB);
        displayImage(currentImage);
    }

    void resetImage() {
        if (!originalImage.empty()) {
            currentImage = originalImage.clone();
            displayImage(currentImage);
        }
    }

    void createErrorLog(const std::exception& e) {
        std::ofstream logFile("error_log.txt", std::ios::app);
        logFile << "Exception occurred:\n" << e.what() << "\n\n";
    }

    void displayImage(const cv::Mat& image) {
        QImage qImage(image.data, image.cols, image.rows, static_cast<int>(image.step[0]), 
                      (image.type() == CV_8UC1) ? QImage::Format_Grayscale8 : QImage::Format_BGR888);
        imageLabel->setPixmap(QPixmap::fromImage(qImage));
    }

private:
    QLabel* imageLabel;
    QPushButton* btnSelectImage;
    QPushButton* btnGrayDetection;
    QPushButton* btnEdgeDetection;
    QPushButton* btnRgbProcessing;
    QPushButton* btnResetImage;
    cv::Mat currentImage;
    cv::Mat originalImage;
};

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    SiliconOrganismGenerator window;
    window.show();
    return app.exec();
}

#include "main.moc"
