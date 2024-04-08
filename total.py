from paddleocr import PaddleOCR
import cv2

import re
from PIL import Image
import unicodedata
import mimetypes
import fitz


ocr = PaddleOCR(lang='korean')
 
img_path = "company/2a328cb43f59d4b5261682d48a3c1b63.jpg"
result = ocr.ocr(img_path, cls=False)
 
ocr_result = result[0]
print(ocr_result)