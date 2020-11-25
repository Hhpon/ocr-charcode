import os
import pytesseract
from PIL import Image
from collections import defaultdict


def get_threshold(image):
    pixel_dict = defaultdict(int)
    rows, cols = image.size
    for i in range(rows):
        for j in range(cols):
            pixel = image.getpixel((i, j))
            pixel_dict[pixel] += 1

    threshold = max(pixel_dict, key=lambda x: pixel_dict[x])
    return threshold


def get_bin_table(threshold):
    table = []
    for i in range(256):
        rate = 0.25
        if threshold*(1-rate) <= i <= threshold*(1+rate):
            table.append(1)
        else:
            table.append(0)
    return table


def cut_noise(image):
    rows, cols = image.size
    change_pos = []
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            pixel_set = []
            for m in range(i-1, i+2):
                for n in range(j-1, j+2):
                    if image.getpixel((m, n)) != 1:
                        pixel_set.append(image.getpixel((m, n)))
            if len(pixel_set) <= 2:
                change_pos.append((i, j))
    for pos in change_pos:
        image.putpixel(pos, 1)
    return image


def OCR_lmj(dir, file):
    image = Image.open('%s/%s' % (dir, file))
    imgry = image.convert('L')
    imgry.save('gray/%s' % file)

    # imgry.show()

    threshold = get_threshold(imgry)
    print(threshold)
    table = get_bin_table(threshold)
    out = imgry.point(table, '1')
    out = cut_noise(out)
    out = cut_noise(out)
    out = cut_noise(out)
    out.save('out/%s' % file)

    # text = pytesseract.image_to_string(imgry).strip()
    text = pytesseract.image_to_string(out).strip()
    exclude_char_list = ' .:\\|\'\"?![],()~@#$%^&*_+-={};<>/¥'
    text = ''.join([x for x in text if x not in exclude_char_list])

    return text


def main():
    dir = 'code'

    correct_count = 0
    total_count = 0

    for file in os.listdir(dir):
        answer = file.split('.')[0]
        recognizition = OCR_lmj(dir, file).lower()
        print((answer, recognizition, len(recognizition)))
        if recognizition == answer:
            correct_count += 1

        total_count += 1
    print('Total count: %d, correct: %d.' % (total_count, correct_count))


main()
