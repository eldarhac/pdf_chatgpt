import os

import cv2
from pdf2image import convert_from_bytes, convert_from_path
import pytesseract
from deep_translator import GoogleTranslator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from concurrent.futures import ThreadPoolExecutor

from config import config


# Sub-task 2: Convert each PDF page to an image
def convert_pdf_to_images(input_pdf_path):
    images = []
    pages = convert_from_path(input_pdf_path, poppler_path=config["POPPLER_PATH"], thread_count=10)
    # pages = convert_from_bytes(input_pdf_bytes)
    images.extend(pages)
    return images


# Sub-task 3: Use OCR to extract Hebrew text from each image
def process_image(i, image, dir_name):
    pytesseract.pytesseract.tesseract_cmd = config["TESSERACT_PATH"]
    # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    IMAGE_PATH = os.path.join(dir_name, f'temp{i}.png')
    image.save(IMAGE_PATH, 'png')
    image = cv2.imread(IMAGE_PATH)
    (h, w) = image.shape[:2]
    img = cv2.resize(image, (w * 3, h * 3))
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(thr, lang='heb')
    text = text.replace('מייר', 'מ״ר')
    text = text.replace('עייי', 'ע״י')
    text = text.replace('שייח', 'ש״ח')
    text = text.replace('ימיס', 'ימים')
    os.remove(IMAGE_PATH)
    return text


def extract_text(images, dir_name):
    pytesseract.pytesseract.tesseract_cmd = config["TESSERACT_PATH"]
    with ThreadPoolExecutor(max_workers=10) as executor:
        texts = list(executor.map(lambda args: process_image(*args, dir_name), enumerate(images)))
    return texts


# Sub-task 4: Translate Hebrew text to English
def translate_text(i, text):
    return GoogleTranslator(source='auto', target='en').translate(text)


def translate_texts(texts):
    with ThreadPoolExecutor(max_workers=10) as executor:
        translated_texts = list(executor.map(lambda args: translate_text(*args), enumerate(texts)))
    return translated_texts


# Sub-task 5: Create a new PDF with the translated text, page by page
def create_translated_pdf(translated_texts, input_pdf_path):
    output_pdf_path = f'{input_pdf_path[:-4]}_translated.pdf'
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = 8
    style.leading = 14
    for translated_text in translated_texts:
        pars = translated_text.split("\n\n")
        for par in pars:
            if not par.isdigit():
                paragraph = Paragraph(par, style)
                story.append(paragraph)
        story.append(PageBreak())
    doc.build(story)
    return output_pdf_path


def translate_pdf(input_pdf_path, dir_name, translate=True):
    images = convert_pdf_to_images(input_pdf_path)
    texts = extract_text(images, dir_name)
    if translate:
        texts = translate_texts(texts)
    return create_translated_pdf(texts, input_pdf_path)
