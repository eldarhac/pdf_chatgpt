import os

import cv2
from pdf2image import convert_from_bytes, convert_from_path
import pytesseract
from deep_translator import GoogleTranslator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

from config import config

PROGRESS_TEXT = 'Translating PDF...'


# Sub-task 2: Convert each PDF page to an image
def convert_pdf_to_images(pdf_file):
    images = []
    # pages = convert_from_path(input_pdf_path, poppler_path=config["POPPLER_PATH"], thread_count=10)
    with st.spinner('Uploading PDF...'):
        pages = convert_from_bytes(pdf_file.getvalue(), thread_count=4)
    images.extend(pages)
    return images


# Sub-task 3: Use OCR to extract Hebrew text from each image
def process_image(i, image, dir_name):
    pytesseract.pytesseract.tesseract_cmd = config["TESSERACT_PATH"]
    # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    os.makedirs(dir_name, exist_ok=True)
    IMAGE_PATH = os.path.join(dir_name, f'temp{i}.png')
    image.save(IMAGE_PATH, 'png')
    image = cv2.imread(IMAGE_PATH)
    (h, w) = image.shape[:2]
    img = cv2.resize(image, (w * 3, h * 3))
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # apply a distance transform which calculates the distance to the
    # closest zero pixel for each pixel in the input image
    dist = cv2.distanceTransform(thr, cv2.DIST_L2, 5)
    # normalize the distance transform such that the distances lie in
    # the range [0, 1] and then convert the distance transform back to
    # an unsigned 8-bit integer in the range [0, 255]
    dist = cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)
    dist = (dist * 255).astype("uint8")
    # threshold the distance transform using Otsu's method
    dist = cv2.threshold(dist, 0, 255,
    	cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    opening = cv2.morphologyEx(dist, cv2.MORPH_OPEN, kernel)
    text = pytesseract.image_to_string(opening, lang='heb')
    text = text.replace('מייר', 'מ״ר')
    text = text.replace('עייי', 'ע״י')
    text = text.replace('שייח', 'ש״ח')
    text = text.replace('ימיס', 'ימים')
    return text, i


def extract_text(images, dir_name, bar):
    pytesseract.pytesseract.tesseract_cmd = config["TESSERACT_PATH"]
    with ThreadPoolExecutor(max_workers=4) as executor:
        text_futures = {executor.submit(process_image, i, image, dir_name): i for i, image in enumerate(images)}
        texts = [None] * len(images)
        for idx, future in enumerate(as_completed(text_futures), start=1):
            progress = idx / (len(images) * 2)
            # update progress bar
            texts[future.result()[1]] = future.result()[0]
            bar.progress(progress, PROGRESS_TEXT)
    return texts


# Sub-task 4: Translate Hebrew text to English
def translate_text(i, text):
    return GoogleTranslator(source='auto', target='en').translate(text), i


def translate_texts(texts, bar):
    with ThreadPoolExecutor(max_workers=4) as executor:
        text_futures = {executor.submit(translate_text, i, text): i for i, text in enumerate(texts)}
        translated_texts = [None] * len(texts)
        for idx, future in enumerate(as_completed(text_futures), start=1):
            progress = (len(texts) + idx) / (len(texts) * 2)
            # update progress bar
            translated_texts[future.result()[1]] = future.result()[0]
            bar.progress(progress, PROGRESS_TEXT)
    return translated_texts


# Sub-task 5: Create a new PDF with the translated text, page by page
def create_translated_pdf(translated_texts, pdf_name):
    output_pdf_path = f'{pdf_name}_translated.pdf'
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
                par = par.replace('<', '&lt;')
                par = par.replace('>', '&gt;')
                paragraph = Paragraph(par, style)
                story.append(paragraph)
        story.append(PageBreak())
    doc.build(story)
    return output_pdf_path


def translate_pdf(pdf_file, dir_name=None, translate=True):
    pdf_name = pdf_file.name[:-4]
    if dir_name is None:
        dir_name = pdf_name
    images = convert_pdf_to_images(pdf_file)
    bar = st.progress(0, PROGRESS_TEXT)
    texts = extract_text(images, dir_name, bar)
    if translate:
        texts = translate_texts(texts, bar)
    bar.empty()
    return create_translated_pdf(texts, pdf_name)
