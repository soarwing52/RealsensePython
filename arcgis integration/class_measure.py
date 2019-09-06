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
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_device_from_file(self.file_name)
        self.command = {'q': 0, 'left': -1, 'right': 1}


    def video(self):
        try:
            self.config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
            profile = pipeline.start(self.config)
            device = profile.get_device()
            playback = device.as_playback()
            playback.set_real_time(False)

            while True:
                pause = False
                frames = self.pipeline.wait_for_frames()
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
            self.pipeline.stop()

    def measure(self,object_id):

        self.config.enable_all_streams()

        profile = self.pipeline.start(self.config)

        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)
        frame_list = []

        with open('all.csv'.format(self.Pro_Dir), 'r') as csvfile:
            for line in csvfile:
                frame = [elt.strip() for elt in line.split(';')]
                frame_list.append(frame)

        for obj in frame_list:
            if obj[0] == object_id:
                self.i = frame_list.index(obj)
                break

        self.search_count = 0

        try:
            while True:
                x, depth_num , color_num = self.i, frame_list[self.i][6], frame_list[self.i][5]

                depth_frame = self.frame_getter('depth', depth_num)
                color_frame = self.frame_getter('color', color_num)

                color_image = np.asanyarray(color_frame.get_data())
                color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
                fig = plt.figure()
                fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
                ax = fig.add_axes([0, 0, 1, 1])
                number = 'Wegnummer:{}\nFrame: c:{}/d:{}'.format(self.weg_id, self.color_frame_num, self.depth_frame_num)
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

                cid = plt.gcf().canvas.mpl_connect('key_press_event', self.quit_figure)
                plt.xlim((-80,2000))
                plt.ylim((1100,-100))
                plt.show()
                if x == self.i: # close script if close window or press q
                    os._exit(0)


        except IndexError:
            print 'file ended'

        finally:
            print 'finally'
            os._exit(0)


    def frame_getter(self, type, num):
        align_to = rs.stream.color
        align = rs.align(align_to)
        try:
            while True:
                frames = self.pipeline.wait_for_frames()
                aligned_frames = align.process(frames)
                if type == 'color':
                    frame = aligned_frames.get_color_frame()
                    self.color_frame_num = frame.get_frame_number()
                else:
                    frame = aligned_frames.get_depth_frame()
                    self.depth_frame_num = frame.get_frame_number()

                if not frame:
                    continue
                frame_num = rs.frame.get_frame_number(frame)

                if abs(int(frame_num) - int(num)) < 5:
                    print 'match {} {}'.format(type, frame_num)
                    self.search_count = 0
                    break

        finally:
            return frame

    def count_search(self, now, target):
        if abs(now - target) < 100:
            self.search_count += 1
            if self.search_count > 10:
                self.i += self.command[event.key]

    def quit_figure(self, event):
        """
        keyboard command for matplotlib
        :param event:
        :return:
        """
        if event.key:
            plt.close(event.canvas.figure)
            self.direction = event.key
            self.i += self.command[event.key]




def main():
    a = Arc_Real(r'X:/Mittelweser/0612/jpg/0612_003-511.jpg','0612_003')
    #a.video()
    a.measure('5793')
    print a

if __name__ == '__main__':
    main()




