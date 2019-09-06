import pyrealsense2 as rs
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.widgets2 import Ruler
import os

class Arc_Real:
    def __init__(self, object_id):
        self.command = {'q': 0, 'left': -1, 'right': 1}
        with open('all.csv', 'r') as csvfile:
            self.frame_list = [[elt.strip() for elt in line.split(';')] for line in csvfile]

        obj = self.get_attribute(object_id=object_id)
        self.search_count = 0
        self.path = obj['jpg_path']
        self.weg_id = obj['weg_num']
        self.color_frame_num = obj['Color']
        self.BagFilePath = os.path.abspath(self.path)
        self.file_dir = os.path.dirname(self.BagFilePath)
        self.Pro_Dir = os.path.dirname(self.file_dir)
        self.file_name = '{}\\bag\\{}.bag'.format(self.Pro_Dir,self.weg_id)
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_device_from_file(self.file_name)

        self.config.enable_all_streams()
        profile = self.pipeline.start(self.config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)



    def get_attribute(self, object_id=False, color=False, weg_id=False):
        title = self.frame_list[0]
        for obj in self.frame_list:
            if obj[0] == object_id or (obj[1] == weg_id and obj[5] == color):
                self.i = self.frame_list.index(obj)
                obj = dict(zip(title, obj))
                return obj


    def video(self):
        try:
            self.color_frame = self.frame_getter('color',int(self.color_frame_num))
            while True:
                c_frame_num = str(self.color_frame.get_frame_number())
                color_image = np.asanyarray(self.color_frame.get_data())
                color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                color_cvt = cv2.resize(color_cvt, (1680, 1050))

                cv2.rectangle(color_cvt, (540, 20), (640, 60), (255, 255, 255), -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = (550, 50)
                fontScale = 1
                fontColor = (0, 0, 0)
                lineType = 2
                cv2.putText(color_cvt, c_frame_num, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

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
                    cv2.rectangle(color_cvt, (500, 20), (520, 60), (255, 255, 255), -1)
                    cv2.putText(color_cvt, 'P', (500,50), font, fontScale, fontColor,
                                lineType)

                    cv2.imshow("Color Stream", color_cvt)
                    cv2.waitKey(0)

                elif key == 32:
                    item = self.get_attribute(color=c_frame_num, weg_id=self.weg_id)
                    if item is not None:
                        cv2.rectangle(color_cvt, (500, 20), (525, 60), (255, 255, 255), -1)
                        cv2.putText(color_cvt, 'M', (500, 50), font, fontScale, fontColor,
                                    lineType)

                        cv2.imshow("Color Stream", color_cvt)
                        cv2.waitKey(0)
                        self.measure2(item['OBJECTID'])

                frames = self.pipeline.wait_for_frames()
                self.color_frame = frames.get_color_frame()

        except RuntimeError:
            print('file ended')
            cv2.destroyAllWindows()

        finally:
            print('finish')
            os._exit(0)
            self.pipeline.stop()

    def measure2(self,object_id):
        obj = self.get_attribute(object_id=object_id)
        x, depth_num, color_num = self.i, obj['Depth'], obj['Color']
        try:
            while True:
                print(x, depth_num, color_num)
                depth_frame = self.frame_getter('depth', depth_num)
                color_frame = self.frame_getter('color', color_num)

                color_image = np.asanyarray(color_frame.get_data())
                color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
                fig = plt.figure()
                fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
                ax = fig.add_axes([0, 0, 1, 1])
                number = 'Wegnummer:{}\nFrame: c:{}/d:{}'.format(self.weg_id, self.color_frame_num,
                                                                 self.depth_frame_num)
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
                plt.xlim((-80, 2000))
                plt.ylim((1100, -100))
                plt.show()
                if x == self.i:  # close script if close window or press q
                   break

                x, depth_num, color_num = self.i, self.frame_list[self.i][6], self.frame_list[self.i][5]

        except IndexError:
            print('file ended')

        finally:
            print('close measure')



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
                    print('match {} {}'.format(type, frame_num))
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
            try:
                self.direction = event.key
                self.i += self.command[event.key]
                plt.close(event.canvas.figure)
            except:
                pass




def main():
    Arc_Real('5793').video()
    print(a)

if __name__ == '__main__':
    main()




