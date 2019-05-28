import os
import multiprocessing as mp
import pyrealsense2 as rs
import numpy as np
import cv2


def color_to_png(input_file):
    print input_file
    bagname= os.path.basename(input_file)
    bagdir= os.path.dirname(input_file)
    projectdir = os.path.dirname(bagdir)
    #print bagname,bagdir,projectdir
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_all_streams()
    config.enable_device_from_file(input_file,False)
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
            #cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
            #cv2.imshow("Color Stream", color_cvt)

            png_name = '{}/png/{}.png'.format(projectdir, bagname[:-4])
            print png_name
            exist = os.path.isfile(png_name)
            if exist:
                print 'png exist'
                pass
            else:
                print 'compressing {}/png/{}.png'.format(projectdir, bagname[:-4])
                cv2.imwrite('{}/png/{}.png'.format(projectdir, bagname[:-4]), color_cvt,[cv2.IMWRITE_PNG_COMPRESSION,1])
            key = cv2.waitKey(100)
            # if pressed escape exit program
            if key == 27:
                cv2.destroyAllWindows()
                break

    except RuntimeError:
        print 'frame covert finished for '+input_file
        cv2.destroyAllWindows()
    finally:
        pass


def main():

    bag_list = []
    png_list = []

    for x in os.listdir('png'):
        png_list.append(x[:-4])

    for y in os.listdir('frameset'):
        bag_list.append(y[:-4])


    unique =[]

    for x in bag_list:
        if x not in png_list:
            print x
            x = './frameset/{}.bag'.format(x)
            unique.append(x)

    print len(unique)
    print unique
    pool = mp.Pool()

    pool.map(color_to_png,unique)
    print 'done'


if __name__ == '__main__':
    main()

