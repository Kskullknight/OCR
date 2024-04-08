from paddleocr import PaddleOCR
import cv2

import re
from PIL import Image
import unicodedata
import mimetypes
import fitz
num,name,ceo,adr_1=0,0,0,0
 
def enhance_image(path):
    image=cv2.imread(path)
    avg_brightness = int(image.mean())
    print(avg_brightness)
    image = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
    
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
 
def convert_to_image(input_path):
    file_extension = mimetypes.guess_extension(mimetypes.guess_type(input_path)[0])
    if file_extension == '.pdf':
        pdf_document = fitz.open(input_path)
        # 첫 번째 페이지를 이미지로 변환
        first_page = pdf_document.load_page(0)
        image = first_page.get_pixmap()
        pdf_document.close()
        jpg_path = input_path.replace('.pdf', '.jpg')
        image.save(jpg_path)
       
        return jpg_path
    elif file_extension == '.png':
        # PNG 파일을 JPEG로 변환
        with Image.open(input_path) as img:
            jpg_path = input_path[:-4] + ".jpg"  # ".png" 확장자를 ".jpg"로 변경
            img.convert("RGB").save(jpg_path, "JPEG")
            return jpg_path
    elif file_extension in ['.jpg', '.jpeg']:
        return input_path
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
        if "북" in line or "묵" in line:
            adr1="경상북도"
        elif "남" in line or "낭" in line:
            adr1="경상남도"
    elif ("제" in line and ("특" in line or "주" in line)):
        adr1="제주특별자치도"
    else:
        adr_1=0
    return adr1,adr_1

 
def find_first_special_char_index(address):
    special_chars = [',', '(', '.']
    first_char_index = -1
    for char in special_chars:
        char_index = address.find(char)
        if char_index != -1 and (first_char_index == -1 or char_index < first_char_index):
            first_char_index = char_index
    return first_char_index
 
 
path = "company/06c6388c9384736d476195067cae086e.jpg"
path = convert_to_image(path)
image = enhance_image(path)
text = PaddleOCR(lang="korean")
print(text)
 
lines = text.split("\n")
lines = [''.join(line.split()) for line in lines]
pattern= re.compile(r'\d{3}-\d{2}-\d{5}')
cv2.imshow('image',image)
 
for i, line in enumerate(lines):
    #----고유번호 찾기--------------------------------------
    if num==0:
        match = pattern.search(line)
        if match:
            print(f'cp_number : {match.group()}')
            num=1
    #------단체명 찾기---------------------------------------
    elif("단" in line or "체" in line or "명" in line or "상" in line or "호" in line or "법" in line or "인" in line) and name==0 and num==1:
        line=unicodedata.normalize('NFKC',line)
        if ":" in line:
            parts=line.split(":")
            if len(parts)>1:
                print(f'cp_name : {parts[1]}')
        else:
            if "상" in line:
                parts=line[3:]
                print(f'cp_name:{parts}')
        name=1
    #-------대표자 찾기----------------------------------------
    elif ("대" in line or "자" in line or "표" in line or "성" in line or "명" in line) and ceo==0 and num==1 and name==1:
        line = unicodedata.normalize('NFKC', line)
        parts = line.split(":")
        if len(parts) > 1:
            if "생" in parts[1]:
                line2=parts[1].split("생")
                print(f'cp_ceo : {line2[0]}')
 
            elif "법" in parts[1]:
                line2=parts[1].split("법")
                print(f'cp_ceo : {line2[0]}')
            elif "범" in parts[1]:
                line2=parts[1].split("범")
                print(f'cp_ceo:{line2[0]}')
            else:
                print(f'cp_ceo:{parts[1]}')
            ceo=1
    #--------주소 찾기------------------------------------------
    elif ("소" in line or "재" in line or "지" in line[:1] or "사업" in line or "광" in line) and "본" not in line[:5] and adr_1==0 and ceo==1 and num==1 and name==1:
        line = unicodedata.normalize('NFKC', line)
        separate=line.split(":")
        print(separate[1])
        adr1,adr_1=find_location(separate[1])
        
       
        break
if num!=1 or name!=1 or adr_1!=1:
    print("사진을 다시 찍어주세요. \n")
   
if adr_1==1:
    print(f'cp_address : {adr1}')

       
cv2.waitKey()
cv2.destroyAllWindows()