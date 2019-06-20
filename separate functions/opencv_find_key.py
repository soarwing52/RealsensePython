import cv2
import sys

img = cv2.imread('DSCN9122.JPG')

while True:
    cv2.imshow('img',img)

    res = cv2.waitKeyEx(0)
    print 'You pressed %d (0x%x), LSB: %d (%s)' % (res, res, res % 256,
        repr(chr(res%256)) if res%256 < 128 else '?')
    if res == 'left':
        print('left')

        a = 'asd'
        a.lo