import pyrealsense2 as rs
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.widgets2 import Ruler
import os


def video(bag,weg_id):
    BagFilePath = os.path.abspath(bag)
    fileDir = os.path.dirname(BagFilePath)
    ProjDir = os.path.dirname(fileDir)
    print BagFilePath,fileDir,ProjDir
    num = weg_id

    file_name = '{}\\bag\\{}.bag'.format(ProjDir, num)
    print file_name
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(file_name)
    config.enable_all_streams()
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(True)
    align_to = rs.stream.color
    align = rs.align(align_to)
    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth_color = rs.colorizer().colorize(depth_frame)
            depth_color_image = np.asanyarray(depth_color.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            img_over = cv2.addWeighted(color_cvt, 1, depth_color_image, 0.3, 0.5)
            cv2.namedWindow("Color Stream", cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Color Stream", color_cvt)

            key = cv2.waitKey(500)
            # if pressed escape exit program
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
            else:
                pass

    except RuntimeError:
        cv2.destroyAllWindows()
        print 'file ended'

    finally:
        print 'finish'
    pipeline.stop()
    return

def frame_match(bag,weg_id,color_frame_num):
    BagFilePath = os.path.abspath(bag)
    fileDir = os.path.dirname(BagFilePath)
    ProjDir = os.path.dirname(fileDir)
    print BagFilePath,fileDir,ProjDir
    num = weg_id

    file_name = '{}\\bag\\{}.bag'.format(ProjDir, num)
    print file_name
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(file_name)
    config.enable_all_streams()
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(True)
    align_to = rs.stream.color
    align = rs.align(align_to)
    frame_list = []



    with open('{}\\list\\{}_matched.txt'.format(ProjDir,num), 'r') as csvfile:
        for line in csvfile:
            frame = [elt.strip() for elt in line.split(',')]
            frame_list.append(frame)

    def search(frame_num):
        a = frame_num
        for x in frame_list:
            ans = a in x
            if ans == True:
                qq = frame_list.index(x)
                return int(qq)
            else:
                pass
    global i
    i = search(color_frame_num)
    print i
    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            vard = rs.frame.get_frame_number(depth_frame)
            if int(vard) == int(frame_list[i][2]):
                print 'match'
                try:
                    while True:
                        new_frames = pipeline.wait_for_frames()
                        color_frame = new_frames.get_color_frame()
                        var = rs.frame.get_frame_number(color_frame)
                        if int(var) == int(frame_list[i][1]):
                            depth_color = rs.colorizer().colorize(depth_frame)
                            depth_color_image = np.asanyarray(depth_color.get_data())
                            color_image = np.asanyarray(color_frame.get_data())
                            color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
                            print var, vard
                            xCoord = np.arange(0, 6, 1)
                            yCoord = [0, 1, -3, 5, -3, 0]

                            fig = plt.figure()
                            ax = fig.add_subplot(111)

                            number = '{}.frame number: c:{}/d:{}'.format(i, str(var), str(vard))
                            markerprops = dict(marker='o', markersize=5, markeredgecolor='red')
                            lineprops = dict(color='red', linewidth=2)
                            plt.imshow(color_image)
                            ax.grid(False)
                            plt.text(500, -20, number, fontsize=15)
                            figManager = plt.get_current_fig_manager().window.state('zoomed')


                            ruler = Ruler(ax=ax,
                                          depth_frame=depth_frame,
                                          color_intrin=color_intrin,
                                          useblit=True,
                                          markerprops=markerprops,
                                          lineprops=lineprops,
                                          )

                            def quit_figure(event):
                                global i
                                if event.key == 'q':
                                    i = 800
                                    print i
                                    plt.close(event.canvas.figure)
                                    return i
                                elif event.key == 'h':
                                    plt.close(event.canvas.figure)
                                    i -= 1
                                elif event.key == 'j':
                                    plt.close(event.canvas.figure)
                                    i += 1
                                elif event.key == 'u':
                                    plt.close(event.canvas.figure)
                                    frame_num = raw_input('frame numer: ')
                                    i = search(frame_num)

                            cid = plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)
                            plt.show()
                            # if pressed escape exit program
                            print i
                            if i == 800:

                                break
                            else:

                                break

                finally:
                    pass
            elif i == 800:
                break
            else:
                print 'searching'
                pass

    except IndexError:
        print 'file ended'


    finally:
        print 'return'
        pipeline.stop()
        return

def measurement(bag,weg_id):
    BagFilePath = os.path.abspath(bag)
    fileDir = os.path.dirname(BagFilePath)
    ProjDir = os.path.dirname(fileDir)
    print BagFilePath,fileDir,ProjDir
    num = weg_id

    file_name = '{}\\bag\\{}.bag'.format(ProjDir, num)
    print file_name
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(file_name)
    config.enable_all_streams()
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(True)
    align_to = rs.stream.color
    align = rs.align(align_to)
    frame_list = []

    with open('{}\\list\\{}_matched.txt'.format(ProjDir,num), 'r') as csvfile:
        for line in csvfile:
            frame = [elt.strip() for elt in line.split(',')]
            frame_list.append(frame)
    global i
    i = 1
    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            vard = rs.frame.get_frame_number(depth_frame)
            if int(vard) == int(frame_list[i][2]):
                print 'match'
                try:
                    while True:
                        new_frames = pipeline.wait_for_frames()
                        color_frame = new_frames.get_color_frame()
                        var = rs.frame.get_frame_number(color_frame)
                        if int(var) == int(frame_list[i][1]):
                            depth_color = rs.colorizer().colorize(depth_frame)
                            depth_color_image = np.asanyarray(depth_color.get_data())
                            color_image = np.asanyarray(color_frame.get_data())

                            color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

                            print var, vard

                            xCoord = np.arange(0, 6, 1)
                            yCoord = [0, 1, -3, 5, -3, 0]
                            fig = plt.figure()
                            ax = fig.add_subplot(111)

                            number = '{}.frame number: c:{}/d:{}'.format(i, str(var), str(vard))
                            markerprops = dict(marker='o', markersize=5, markeredgecolor='red')
                            lineprops = dict(color='red', linewidth=2)
                            plt.imshow(color_image)
                            ax.grid(False)
                            plt.text(500, -20, number, fontsize=15)
                            figManager = plt.get_current_fig_manager().window.state('zoomed')

                            ruler = Ruler(ax=ax,
                                          depth_frame=depth_frame,
                                          color_intrin=color_intrin,
                                          useblit=True,
                                          markerprops=markerprops,
                                          lineprops=lineprops,
                                          )

                            def search(frame_num):
                                a = frame_num
                                for x in frame_list:
                                    ans = a in x
                                    if ans == True:
                                        qq = x
                                        return int(qq[0])
                                    else:
                                        pass

                            def quit_figure(event):
                                global i
                                if event.key == 'q':
                                    plt.close(event.canvas.figure)
                                    i = 800
                                    return i
                                elif event.key == 'h':
                                    plt.close(event.canvas.figure)
                                    i -= 1
                                elif event.key == 'j':
                                    plt.close(event.canvas.figure)
                                    i += 1
                                elif event.key == 'u':
                                    plt.close(event.canvas.figure)
                                    frame_num = raw_input('frame numer: ')
                                    i = search(frame_num)

                            cid = plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)
                            plt.show()
                            # if pressed escape exit program

                            if i == 800:

                                break
                            else:

                                break

                finally:
                    pass

            else:
                print 'searching'
                pass

    except IndexError:
        print 'file ended'


    finally:
        print 'return'
        
        
    pipeline.stop()
    return
