import os

import cv2
import mimetypes
import fitz
from paddleocr import PaddleOCR
import re
from PIL import Image
import unicodedata


NUM_PATTERN = re.compile(r'\d{3}-\d{2}-\d{5}')

def find_location(line):
    line = line[:4]
    adr1=None
    adr_1=1
    if "서" in line and ("특" in line or "별" in line):
        adr1="서울특별시"
    elif "부" in line or "무" in line:
        adr1="부산광역시"
    elif "구" in line:
        adr1="대구광역시"
    elif "전" in line:
        adr1="대전광역시"
    elif "주" in line:
        adr1="광주광역시"
    elif "울" in line or "물"  in line:
        adr1="울산광역시"
    elif "원" in line:
        adr1="강원도"
    elif "경" in line and "기" in line:
        adr1="경기도"
    elif ("충" in line or "청" in line) and "북" in line:
        adr1="충청북도"
    elif ("충" in line or "청" in line) and "남" in line:
        adr1="충청남도"
    elif ("전" in line or "라" in line) and "북" in line:
        adr1="전라북도"
    elif ("전" in line or "라" in line) and "남" in line:
        adr1="전라남도"
    elif "상" in line:
        if "북" in line:
            adr1="경상북도"
        elif "남" in line:
            adr1="경상남도"
    elif ("제" in line and ("특" in line or "주" in line)):
        adr1="제주특별자치도"
    else:
        adr_1=0
    return adr1,adr_1

def get_text_to_image(image):
    text = PaddleOCR(lang="korean + eng")
    lines = text.split("\n")
    lines = [''.join(line.split()) for line in lines]
    return lines

def find_first_special_char_index(address):
    special_chars = [',', '(', '.']
    first_char_index = -1
    for char in special_chars:
        char_index = address.find(char)
        if char_index != -1 and (first_char_index == -1 or char_index < first_char_index):
            first_char_index = char_index
    return first_char_index
 

class CertificateImage:
    num_bool, name_bool, ceo_bool, adr_1_bool = False, False, False, False

    cp_num = None
    cp_name = None
    cp_ceo = None
    cp_adr_1 = None

    path=None

    image_ori = None 

    def __int__(self,path):
        self.lines= None
        self.convert_path(path)
        self.image_ori = cv2.imread(self.path)

        self.find_data()

    def make_data_list(self):
        return [self.path, self.cp_num, self.cp_name, self.cp_ceo, self.cp_adr_1, self.lines]

    def convert_path(self,path):
        file_extension = mimetypes.guess_extension(mimetypes.guess_type(path)[0])
        if file_extension == '.pdf':
            pdf_document = fitz.open(path)
            # 첫 번째 페이지를 이미지로 변환
            first_page = pdf_document.load_page(0)
            image = first_page.get_pixmap()
            pdf_document.close()
            jpg_path = path.replace('.pdf', '.jpg')
            if not os.path.exists('./temp'):
                os.makedirs('./temp')
            new_path = './temp/' + jpg_path.split('\\')[-1]
            image.save(new_path)
            return
        elif file_extension == '.png':
            with Image.open(path) as img:
                # 새 파일 경로 생성
                jpg_path = path[:-4] + ".jpg"
                img.convert("RGB").save(jpg_path, "JPEG")
                os.remove(path)
                self.path = jpg_path
                return
        self.path = new_path    


    def binarize_old(self): 
        image=cv2.imread(self.image_ori)
        avg_brightness = int(image.mean())
        print(avg_brightness)
        image = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, None, fx=1.4, fy=1.4, interpolation=cv2.INTER_CUBIC)
        if avg_brightness>=242 and avg_brightness<=247 and avg_brightness!=245:
            ret, image = cv2.threshold(image, 230, 255, cv2.THRESH_BINARY)
        elif avg_brightness==176 or (avg_brightness>=220 and avg_brightness<239) or avg_brightness==245:
            ret, image = cv2.threshold(image, 178, 255, cv2.THRESH_BINARY)
        elif avg_brightness >158 and avg_brightness <210 and avg_brightness!=169 and avg_brightness!=170 :
            ret, image = cv2.threshold(image, 83, 255, cv2.THRESH_BINARY)
        else:
            ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if avg_brightness==172 or avg_brightness ==245:
            image = cv2.resize(image, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_CUBIC)
        print(ret)
        return image    
    

    def find_number(self, line):
        if self.num_bool:
            return

        match = NUM_PATTERN.search(line)
        if match:
            self.cp_num = match.group()
            self.num_bool = True

    def find_name(self, line):
        if self.cp_name:
            return
        if "단" in line or "체" in line or "명" in line or "상호" in line or "법" in line or "인" in line:
            normal_line=unicodedata.normalize('NFKC',line)
            
            if ":" in normal_line:
                parts=normal_line.split(":")
                if len(parts)>1:
                    self.cp_name = parts[1]
                    self.name_bool = True
            else:
                if "상" in normal_line:
                    self.cp_name = normal_line[3:]
                    self.name_bool = True

    def find_CEO(self,line):
        if self.ceo_bool:
            return
        
        if "대" in line or "자" in line or "표" in line or "성" in line or "명" in line:
            normal_line = unicodedata.normalize('NFKC', line)

            parts = normal_line.split(":")
            if len(parts) > 1:
                if "생" in parts[1]:
                    line2 = parts[1].split("생")
                    self.cp_ceo = line2[0]
                elif "법" in parts[1]:
                    line2 = parts[1].split("법")
                    self.cp_ceo = line2[0]
                elif "범" in parts[1]:
                    line2=parts[1].split("범")
                else:
                    self.cp_ceo = parts[1]
                self.ceo_bool = True
    
    def find_adr(self,line):
        if self.adr_1_bool:
            return
        if ("소" in line or "재" in line or "지" in line[:1] or "사업" in line or "광" in line) and "본" not in line[:5] :
            normal_line = unicodedata.normalize('NFKC', line)
            separate=normal_line.split(":")
            print(separate[1])
            adr_1,adr_1_bool=find_location(separate[1])
            self.cp_adr_1 = adr_1
            self.adr_1_bool = adr_1_bool

    def fine_data(self):
        image= self.binarize_old()
        cv2.waitKey(0)
        cv2.destroyWindow()

        lines = get_text_to_image(image)

        for i, line in enumerate(lines):
            self.find_number(line)
            self.find_name(line)
            self.find_CEO(line)
            self.find_adr(line)        

