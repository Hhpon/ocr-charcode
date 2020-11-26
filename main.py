import os
import pytesseract
from PIL import Image
from queue import Queue
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


def img_crop(image):
    rows, cols = image.size
    colsPosition = []
    isXOver = False
    for row in range(rows):
        for col in range(cols):
            if image.getpixel((row, col)) == 0 and not isXOver:
                isXOver = True
                colsPosition.append(row)
            elif image.getpixel((row, col)) == 1 and isXOver:
                isXOver = False
    print(colsPosition)
    return image


def detectFgPix(image, xmax):
    '''
    搜索区域起点
    return x_fd,y_fd
    '''
    rows, cols = image.size
    for row in range(rows):
        for col in range(cols):
            if image.getpixel((row, col)) == 0:
                return row, col


def cfs(image, x_fd, y_fd):
    '''
    image: PIL图片对象
    x_fd: 本次查找过程中，x轴开始坐标
    y_fd: 本次查找过程中，y轴开始坐标
    return xmax,xmin,ymax,ymin
    本次查找过程中与该坐标连接的所有点中在x、y轴方向上的最大最小点
    '''

    xaxis = [x_fd]
    yaxis = [y_fd]
    q = Queue()
    q.put((x_fd, y_fd))
    visited = set()
    offsets = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    while not q.empty():
        x, y = q.get()

        for xoffset, yoffset in offsets:
            x_neighbor, y_neighbor = x + xoffset, y+yoffset
            if (x_neighbor, y_neighbor) not in visited and image.getpixel((x_neighbor, y_neighbor)) == 0:
                visited.add((x_neighbor, y_neighbor))
                xaxis.append(x_neighbor)
                yaxis.append(y_neighbor)
                q.put((x_neighbor, y_neighbor))
    # return max(xaxis), min(xaxis), max(yaxis), min(yaxis)
    return xaxis, yaxis, visited


def crop_image(image, x_min, x_max, y_min, y_max):
    '''
    image: PIL图像对象
    x_min: 切割区域x轴起点
    x_max: 切割区域x轴终点
    y_min: 切割区域y轴起点
    y_max: 切割区域y轴终点
    return crop
    切割之后的图像
    '''
    return crop = image.crop((x_min, y_min, x_max, y_max))

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
    out = img_crop(out)
    # crop_img = out.crop((0, 0, 10, 10))
    # crop_img.save('crop/%s' % file)
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
