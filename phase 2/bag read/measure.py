import pyrealsense2 as rs
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets2 import Ruler
import os



num = raw_input('Wegenummer:\n')
absFilePath = os.path.abspath(__file__)
#print(absFilePath)
fileDir = os.path.dirname(os.path.abspath(__file__))
#print(fileDir)

file_name = '{}\\bag\\{}.bag'.format(fileDir,num)
pipeline = rs.pipeline()
config = rs.config()
config.enable_device_from_file(file_name)
config.enable_all_streams()
profile = pipeline.start(config)
device = profile.get_device()
playback = device.as_playback()
playback.set_real_time(False)
align_to = rs.stream.color
align = rs.align(align_to)
frame_list = []

with open('C:\Users\cyh\Documents\phase2\\list\\'+num+'_matched.txt','r') as csvfile:
    for line in csvfile:
        frame = [elt.strip() for elt in line.split(',')]
        frame_list.append(frame)
i=0
try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        vard = rs.frame.get_frame_number(depth_frame)
        if int(vard) == int(frame_list[i][2]) :
            print 'match'
            try:
                while True:
                    new_frames = pipeline.wait_for_frames()
                    color_frame = new_frames.get_color_frame()
                    var = rs.frame.get_frame_number(color_frame)
                    if int(var) ==int(frame_list[i][1]):
                        depth_color = rs.colorizer().colorize(depth_frame)
                        depth_color_image = np.asanyarray(depth_color.get_data())
                        color_image = np.asanyarray(color_frame.get_data())

                        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

                        print var, vard

                        xCoord = np.arange(0, 6, 1)
                        yCoord = [0, 1, -3, 5, -3, 0]
                        fig = plt.figure()
                        ax = fig.add_subplot(111)

                        number = '{}.frame number: c:{}/d:{}'.format(i,str(var),str(vard))
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
                                i -=1
                            elif event.key == 'j':
                                plt.close(event.canvas.figure)
                                i +=1
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
    pipeline.stop()
    print 'finish'


