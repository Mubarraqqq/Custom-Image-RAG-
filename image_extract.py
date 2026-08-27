import os
from PIL import Image, ImageOps
import pytesseract
from pillow_heif import register_heif_opener
register_heif_opener()

# Add this line (this is the default path for Apple Silicon Macs)
#pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
def images_list_obj(doc):
    img_list_obj = []
    for i in os.listdir(doc):
        a = os.path.join(doc,i)
        a_obj = Image.open(a)
        img_list_obj.append(a_obj)
    return img_list_obj[0:5]

def extract_text_from_img(text_folder: list) -> list:

    full_text = []
    
    for img in text_folder:
        # Preprocessing: Grayscale improves Tesseract accuracy by up to 50%
        gray_page = ImageOps.grayscale(img)
        
        # Run OCR with Page Segmentation Mode 3 (Fully automatic page segmentation)
        text = pytesseract.image_to_string(gray_page, config='--psm 3')
        full_text.append(text)
        
    return "\n\n".join(full_text)

full_document = extract_text_from_img(images_list_obj(doc=r'path to image folder'))
