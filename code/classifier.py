from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import cv2
import time

model = load_model('models\\mandar_VGG16_weight8.h5') 

def toLabel(classes):
    if classes == 0:
        return 'BAD'
  
    elif classes == 1:
        return 'GOOD'
    
img_width, img_height = 150, 150  
  
def load_Img(imgName):
    img_path = 'capture\\' + str(imgName) + '.jpg'
    img = image.load_img(img_path, target_size=(img_width, img_height))
    img_tensor = image.img_to_array(img)                    
    img_tensor = np.expand_dims(img_tensor, axis=0)         
    img_tensor /= 255.
    
    return img_tensor

def show_img(imgName, mandarGrade):
    img_path = 'capture\\' + str(imgName) + '.jpg'
    imgOp = cv2.imread(img_path, cv2.IMREAD_COLOR)

    print("width: {} pixels".format(imgOp.shape[1]))
    print("height: {} pixels".format(imgOp.shape[0]))
    print("channels: {}".format(imgOp.shape[2]))
      
    cv2.namedWindow(imgName, cv2.WINDOW_NORMAL)
    if(mandarGrade == "GOOD"): 
        cv2.putText(imgOp, mandarGrade, (0, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (5, 188, 5))
    else:
        cv2.putText(imgOp, mandarGrade, (0, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255))

    cv2.imshow(imgName, imgOp)



def predictMandar(imgName):  
    img_tensor = load_Img(imgName) 
    images = np.vstack([img_tensor])
    classes = model.predict_classes(images, batch_size=10)
    pred = model.predict(img_tensor)
    mandarGrade = toLabel(classes)
     
    print("Class : " , classes)
    print("Mandarine Grade : " , mandarGrade)
    print("Probability : ", pred, '\n')

    show_img(imgName, mandarGrade)

    return mandarGrade
    
    
