import os
import pyrealsense2 as rs
import numpy as np
import cv2

def color_to_png(input_file):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
    config.enable_device_from_file('./bag/'+input_file,False)
    profile = pipeline.start(config)
    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            var = rs.frame.get_frame_number(color_frame)
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Color Stream", color_cvt)
            cv2.imwrite('./png/{}_c_{}.png'.format(input_file[:-4],str(var)), color_cvt,[cv2.IMWRITE_PNG_COMPRESSION,9])
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

def color_match_list(input_file):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file('./bag/'+input_file, False)
    config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
    profile = pipeline.start(config)
    align_to = rs.stream.color
    align = rs.align(align_to)
    fold = open('./list/'+input_file[:-4] +'_colorlist.txt', 'w')
    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            num_c = rs.frame.get_frame_number(color_frame)
            time_c = rs.frame.get_timestamp(color_frame)
            fold.write('{},{}\n'.format(str(num_c),str(time_c)))

    except RuntimeError:
        print 'color frame list ended'
    finally:
        fold.close()
        pipeline.stop()

def depth_match_list(input_file):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file('./bag/'+input_file, False)
    config.enable_all_streams()
    profile = pipeline.start(config)
    align_to = rs.stream.color
    align = rs.align(align_to)
    fold = open('./list/'+input_file[:-4] +'_depthlist.txt', 'w')
    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            num_d = rs.frame.get_frame_number(depth_frame)
            time_d = rs.frame.get_timestamp(depth_frame)
            fold.write('{},{}\n'.format(str(num_d), str(time_d)))

    except RuntimeError:
        print 'depth frame list ended'
    finally:
        fold.close()
        pipeline.stop()

def match_frame_list(input_file):
    depth_frame_list = []
    color_frame_list = []
    with open('./list/'+input_file[:-4]+'_colorlist.txt', 'r') as csvfile:
        for line in csvfile:
            frame = [elt.strip() for elt in line.split(',')]
            color_frame_list.append(frame)

    with open('./list/'+input_file[:-4]+'_depthlist.txt', 'r') as depcsv:
        for dline in depcsv:
            frame_d = [dd.strip() for dd in dline.split(',')]
            depth_frame_list.append(frame_d)

    csvfile.close()
    depcsv.close()
    f_list = []
    for t_c in color_frame_list:
        for t_d in depth_frame_list:
            gap = float(t_c[1]) - float(t_d[1])
            gap = abs(gap)
            if gap < 25:
                f_list.append(str(t_c[0]) + ',' + str(t_d[0]) + '\n')
    unique_list = []
    for elem in f_list:
        if elem not in unique_list:
            unique_list.append(elem)

    i = 1
    with open('./list/' + input_file[:-4] + '_matched.txt', 'w') as matched:
        for x in unique_list:
            x = '{},{}'.format(i, x)
            matched.write(x)
            i += 1
    matched.close()
    print 'finished match list '+input_file


dir_name = 'bag'
if not os.path.exists('png'):
    try:
        os.makedirs('png', 0o700)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

if not os.path.exists('list'):
    try:
        os.makedirs('list', 0o700)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


for filename in os.listdir(dir_name):
    print filename
    #color_to_png(filename)
    color_match_list(filename)
    depth_match_list(filename)
    match_frame_list(filename)
print 'all done, perfect!'
