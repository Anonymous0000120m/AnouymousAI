import cv2
import pytesseract
import numpy as np
import mysql.connector
from mysql.connector import Error
from PIL import Image
import io

# 配置 Tesseract 可执行文件路径（如果需要）
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class LicensePlateRecognizer:
    def __init__(self, db_config):
        """初始化数据库连接"""
        self.db_config = db_config
        self.connection = None
        
    def connect_to_database(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                print("成功连接到数据库")
                return True
        except Error as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def disconnect_from_database(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
    
    def preprocess_image(self, image):
        """图像预处理"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 降噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 直方图均衡化增强对比度
        equalized = cv2.equalizeHist(blurred)
        
        return equalized
    
    def detect_license_plate(self, image):
        """检测车牌位置"""
        # 预处理图像
        processed = self.preprocess_image(image)
        
        # 使用边缘检测
        edges = cv2.Canny(processed, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # 按面积排序轮廓
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        # 寻找可能的车牌轮廓
        plate_contour = None
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # 车牌通常是四边形
            if len(approx) == 4:
                plate_contour = approx
                break
        
        if plate_contour is not None:
            # 获取车牌区域
            x, y, w, h = cv2.boundingRect(plate_contour)
            
            # 确保宽高比符合车牌特征
            aspect_ratio = w / h
            if 2.5 < aspect_ratio < 5:
                return (x, y, w, h)
        
        return None
    
    def recognize_plate_text(self, plate_image):
        """识别车牌文字"""
        # 进一步处理车牌图像
        gray_plate = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        _, binary_plate = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 使用Tesseract OCR识别
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(binary_plate, config=custom_config)
        
        # 清理识别结果
        cleaned_text = ''.join(e for e in text if e.isalnum())
        return cleaned_text
    
    def process_images_from_database(self, table_name='license_plates'):
        """从数据库读取并处理车牌图片"""
        if not self.connect_to_database():
            return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 查询数据库获取车牌图片和相关信息
            query = f"SELECT id, plate_image, plate_number FROM {table_name}"
            cursor.execute(query)
            
            results = []
            
            for record in cursor:
                try:
                    # 从数据库读取图片数据
                    image_data = record['plate_image']
                    
                    # 将二进制数据转换为OpenCV图像格式
                    image = Image.open(io.BytesIO(image_data))
                    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # 检测车牌位置
                    plate_location = self.detect_license_plate(opencv_image)
                    
                    if plate_location:
                        x, y, w, h = plate_location
                        plate_img = opencv_image[y:y+h, x:x+w]
                        
                        # 识别车牌文字
                        recognized_text = self.recognize_plate_text(plate_img)
                        
                        # 获取实际车牌号（如果有）
                        actual_text = record.get('plate_number', 'N/A')
                        
                        # 保存结果
                        result = {
                            'id': record['id'],
                            'actual_plate': actual_text,
                            'recognized_plate': recognized_text,
                            'match': actual_text.upper() == recognized_text.upper(),
                            'image_size': opencv_image.shape,
                            'plate_location': plate_location
                        }
                        
                        results.append(result)
                    else:
                        results.append({
                            'id': record['id'],
                            'status': 'No plate detected',
                            'image_size': opencv_image.shape
                        })
                
                except Exception as e:
                    print(f"处理记录ID {record.get('id', 'unknown')} 时出错: {e}")
                    continue
            
            return results
        
        finally:
            cursor.close()
            self.disconnect_from_database()
    
    def save_results_to_database(self, results, result_table='recognition_results'):
        """将识别结果保存回数据库"""
        if not self.connect_to_database():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # 创建结果表（如果不存在）
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {result_table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                plate_id INT NOT NULL,
                recognized_plate VARCHAR(20),
                is_correct BOOLEAN,
                processing_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plate_id) REFERENCES license_plates(id)
            )
            """
            cursor.execute(create_table_query)
            
            # 插入结果数据
            insert_query = f"""
            INSERT INTO {result_table} (plate_id, recognized_plate, is_correct)
            VALUES (%s, %s, %s)
            """
            
            for result in results:
                if 'recognized_plate' in result:
                    data = (
                        result['id'],
                        result['recognized_plate'],
                        result.get('match', False)
                    )
                    cursor.execute(insert_query, data)
            
            self.connection.commit()
            return True
        
        except Error as e:
            print(f"保存结果到数据库时出错: {e}")
            self.connection.rollback()
            return False
        
        finally:
            cursor.close()
            self.disconnect_from_database()


if __name__ == "__main__":
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'user': 'your_username',
        'password': 'your_password',
        'database': 'license_plate_db',
        'port': 3306
    }
    
    # 创建识别器实例
    recognizer = LicensePlateRecognizer(db_config)
    
    # 处理数据库中的车牌图片
    results = recognizer.process_images_from_database()
    
    # 打印结果
    print("\n识别结果:")
    for result in results:
        if 'recognized_plate' in result:
            print(f"ID: {result['id']} | 实际车牌: {result['actual_plate']} | 识别结果: {result['recognized_plate']} | 匹配: {'是' if result['match'] else '否'}")
        else:
            print(f"ID: {result['id']} | 状态: {result['status']}")
    
    # 将结果保存回数据库
    if recognizer.save_results_to_database(results):
        print("\n结果已成功保存到数据库")
    else:
        print("\n保存结果到数据库失败")