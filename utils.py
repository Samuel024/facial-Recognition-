import numpy as np
from PIL import Image

#preprocess scale and resize
def preprocess(file_path):
    #read in image from file path
    byte_img = tf.io.read_file(file_path)
    #load in the image
    img = tf.io.decode_jpeg(byte_img)
    
#preprocessing step resize img to 100x100x3
    img = tf.image.resize(img, (100,100))
    img = img/255.0
    return img