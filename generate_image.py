import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# 加载模型
generator = load_model('generator_model.h5')

# 生成新图像
def generate_images(generator, noise_dim, num_images):
    noise = np.random.normal(0, 1, (num_images, noise_dim))
    generated_images = generator.predict(noise)
    return generated_images

# 显示生成的图像
def display_images(images):
    plt.figure(figsize=(10, 10))
    for i in range(len(images)):
        plt.subplot(5, 5, i + 1)
        plt.imshow(images[i, :, :, 0], cmap='gray')
        plt.axis('off')
    plt.show()

if __name__ == "__main__":
    images = generate_images(generator, z_dim=100, num_images=25)
    display_images(images)
