import pyrealsense2 as rs
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.widgets2 import Ruler
import os

class Arc_Real:
    def __init__(self,path,weg_id):
        self.path = path
        self.weg_id = weg_id
        self.BagFilePath = os.path.abspath(path)
        self.file_dir = os.path.dirname(self.BagFilePath)
        self.Pro_Dir = os.path.dirname(self.file_dir)
        self.file_name = '{}\\bag\\{}.bag'.format(self.Pro_Dir,self.weg_id)

    def video(self):
        try:
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_device_from_file(self.file_name)
            config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
            profile = pipeline.start(config)
            device = profile.get_device()
            playback = device.as_playback()
            playback.set_real_time(False)

            while True:
                pause = False
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                if not color_frame:
                    continue
                c_frame_num = rs.frame.get_frame_number(color_frame)
                color_image = np.asanyarray(color_frame.get_data())
                color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                color_cvt = cv2.resize(color_cvt, (1680, 1050))
                cv2.rectangle(color_cvt, (540, 20), (640, 60), (255, 255, 255), -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = (550, 50)
                fontScale = 1
                fontColor = (0, 0, 0)
                lineType = 2
                cv2.putText(color_cvt, str(c_frame_num), bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
                cv2.namedWindow("Color Stream", cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Color Stream", color_cvt)
                key = cv2.waitKey(1000)

                # if pressed escape exit program
                if key & 0xFF == ord('q') or key == 27:
                    cv2.destroyAllWindows()
                    break
                elif cv2.getWindowProperty('Color Stream', cv2.WND_PROP_VISIBLE) < 1:
                    cv2.destroyAllWindows()
                    break
                elif key == 112:
                    if pause is False:
                        print 'pause'
                        pause = True
                        key = cv2.waitKey(0)

        except RuntimeError:
            print 'file ended'
            cv2.destroyAllWindows()

        finally:
            print 'finish'
            os._exit(0)
            pipeline.stop()

    def measure(self,frame_id):
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device_from_file(self.file_name)
        config.enable_all_streams()
        profile = pipeline.start(config)

        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)

        align_to = rs.stream.color
        align = rs.align(align_to)
        frame_list = []

        with open('{}\\foto_log\\{}.txt'.format(self.Pro_Dir, self.weg_id), 'r') as csvfile:
            for line in csvfile:
                frame = [elt.strip() for elt in line.split(',')]
                frame_list.append(frame)

        global i
        i = int(frame_id)-1

        try:
            while True:
                x = i
                frames = pipeline.wait_for_frames()
                aligned_frames = align.process(frames)
                depth_frame = aligned_frames.get_depth_frame()
                if not depth_frame:
                    continue
                depth_color_frame = rs.colorizer().colorize(depth_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                if abs(int(vard) - int(frame_list[i][2]))<5:
                    print 'match depth{}'.format(vard)
                    try:
                        while True:
                            new_frames = pipeline.wait_for_frames()
                            new_aligned_frames = align.process(new_frames)
                            color_frame = new_aligned_frames.get_color_frame()
                            if not color_frame:
                                continue
                            var = rs.frame.get_frame_number(color_frame)
                            if abs(int(var) - int(frame_list[i][1]))<5:
                                print 'match color{}'.format(var)
                                color_image = np.asanyarray(color_frame.get_data())
                                color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
                                fig = plt.figure()
                                fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
                                ax = fig.add_axes([0, 0, 1, 1])
                                number = 'Wegnummer:{}\nFrame: c:{}/d:{}'.format(self.weg_id, str(var), str(vard))
                                plt.imshow(color_image)
                                ax.grid(False)
                                fig.suptitle(number, fontsize=20)
                                markerprops = dict(marker='o', markersize=5, markeredgecolor='red')
                                lineprops = dict(color='red', linewidth=2)
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
                                            qq = frame_list.index(x)
                                            return int(qq)
                                        else:
                                            print 'no frame {} founded'.format(a)
                                            pass

                                def quit_figure(event):
                                    global i
                                    if event.key == 'q':
                                        i = 800
                                        plt.close(event.canvas.figure)
                                        return i
                                    elif event.key == 'left':
                                        plt.close(event.canvas.figure)
                                        i -= 1
                                    elif event.key == 'right':
                                        plt.close(event.canvas.figure)
                                        i += 1
                                    elif event.key == 'up':
                                        plt.close(event.canvas.figure)
                                        frame_num = raw_input('frame numer: ')
                                        i = search(frame_num)

                                cid = plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)
                                plt.xlim((-80,2000))
                                plt.ylim((1100,-100))
                                plt.show()
                                if x == i:
                                    i = 800
                                break
                            else:
                                print 'searching for RGB image: {}, now:{}'.format(frame_list[i][1], var)

                    finally:
                        pass
                elif i == 800:
                    break
                else:
                    print 'searching for Depth image: {}, now:{}'.format(frame_list[i][2], vard)
                    pass

        except IndexError:
            print 'file ended'
        finally:
            print 'return'
            os._exit(0)
            pipeline.stop()
            return


def main():
    a = Arc_Real(r'C:\Users\cyh\Desktop\mittel\png\0513_1.png','0513_1')
    #a.video()
    a.measure('5')
    print a

if __name__ == '__main__':
    main()




