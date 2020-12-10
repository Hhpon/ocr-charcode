import os
import pytesseract
from PIL import Image
from queue import Queue
from collections import defaultdict
import time


def main():
    dir = 'test'

    correct_count = 0
    total_count = 0

    for file in os.listdir(dir):
        answer = file.split('.')[0]
        # recognizition = OCR_lmj(dir, file).lower()
        image = Image.open('%s/%s' % (dir, file))
        recognizition = pytesseract.image_to_string(
            image, lang='num', config='--psm 3').strip()
        exclude_char_list = ' .:\\|\'\"?![],()~@#$%^&*_+-={};<>/¥'
        recognizition = ''.join(
            [x for x in recognizition if x not in exclude_char_list]).lower()
        if recognizition == answer:
            correct_count += 1

        total_count += 1
        print((answer, recognizition, len(recognizition), recognizition == answer))
    print('Total count: %d, correct: %d.' % (total_count, correct_count))


main()
