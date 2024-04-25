import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.datasets import mnist

# 加载 MNIST 数据集
(train_images, train_labels), (_, _) = mnist.load_data()
train_images = train_images / 255.0

# 构建模型
input_layer = Input(shape=(28, 28))
flatten_layer = Flatten()(input_layer)
output_layer = Dense(10, activation='softmax')(flatten_layer)
model = Model(inputs=input_layer, outputs=output_layer)

# 编译模型
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 训练模型
model.fit(train_images, train_labels, epochs=5)

# 保存模型为 .pb 文件
tf.saved_model.save(model, 'my_model')

print("Model saved as 'my_model' directory.")
