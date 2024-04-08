from paddleocr import PaddleOCR
import cv2

import re
from PIL import Image
import unicodedata
import mimetypes
import fitz



def enhance_image(path):
    image=cv2.imread(path)
    avg_brightness = int(image.mean())
    print(avg_brightness)
    image = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
    ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    print(ret)


    cv2.imshow('Enhanced Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return image


ocr = PaddleOCR(lang='korean')
 
img_path = "company/a8392e5d554c2c735642fab3cb5555e8(((!).jpeg"
image = enhance_image(img_path)
result = ocr.ocr(image, cls=False)
 
ocr_result = result[0]
print(ocr_result)