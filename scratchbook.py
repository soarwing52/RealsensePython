import pyrealsense2 as rs
import numpy as np
import cv2
import os
import multiprocessing as mp
from itertools import islice

def color_to_jpg(input_file):
    """create jpg with the input file in the folder jpg"""
    print input_file
    bagname = os.path.basename(input_file)
    bagdir = os.path.dirname(input_file)
    projectdir = os.path.dirname(bagdir)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_all_streams()
    config.enable_device_from_file(input_file, False)
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)
    align_to = rs.stream.color
    align = rs.align(align_to)
    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            var = rs.frame.get_frame_number(color_frame)
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            jpg_name = '{}/jpg/{}-{}.jpg'.format(projectdir, bagname[:-4], var)
            # print jpg_name
            exist = os.path.isfile(jpg_name)
            if exist:
                # print 'jpg exist'
                pass
            else:
                print 'compressing {}'.format(jpg_name)
                cv2.imwrite((jpg_name), color_cvt, [cv2.IMWRITE_JPEG_QUALITY,100])

    except RuntimeError:
        print 'frame covert finished for ' + input_file
        cv2.destroyAllWindows()
    finally:
        pass


def main():
    jpglist = [jpg for jpg in os.listdir(r'C:\Users\cyh\Desktop\copy/jpg')]
    with open(r'C:\Users\cyh\Desktop\copy\shp/matcher.txt','r')as matcher:
        matcher.next()
        for bags in islice(matcher,1,None):
            data = bags.strip().split(',')
            weg_num = data[0]
            frame_num = data[2]
            jpg = '{}-{}.jpg'.format(weg_num, frame_num)
            if jpg in jpglist:
                jpglist.remove(jpg)

    print jpglist


if __name__ == '__main__':
    main()