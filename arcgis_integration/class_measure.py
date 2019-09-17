import pyrealsense2 as rs
import numpy as np
import cv2
import os
import copy, math


class Arc_Real:
    def __init__(self, jpg_path):
        # Basic setting
        self.search_count = 0
        # Data from txt log file
        self.path = jpg_path
        self.BagFilePath = os.path.abspath(jpg_path)
        self.file_dir = os.path.dirname(self.BagFilePath)
        self.Pro_Dir = os.path.dirname(self.file_dir)
        self.weg_id, self.color_frame_num = os.path.splitext(os.path.basename(self.BagFilePath))[0].split('-')

        with open('{}/shp/matcher.txt'.format(self.Pro_Dir), 'r') as txtfile:
            self.title = [elt.strip() for elt in txtfile.readline().split(',')]
            self.frame_list = [[elt.strip() for elt in line.split(',')] for line in txtfile if line.split(',')[0] == self.weg_id]

        self.frame_dict, self.i = self.get_attribute(color=self.color_frame_num, weg_id=self.weg_id)
        self.file_name = '{}\\bag\\{}.bag'.format(self.Pro_Dir, self.weg_id)
        # Start Pipeline
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_device_from_file(self.file_name)
        self.config.enable_all_streams()
        self.hole_fill = rs.hole_filling_filter(2)
        profile = self.pipeline.start(self.config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)
        try:
            self.frame_getter('Color')  # Get Color Frame with the matching frame number from self.frame_dict
            while True:
                self.color_intrin = self.color_frame.profile.as_video_stream_profile().intrinsics
                self.color_image = np.asanyarray(self.color_frame.get_data())
                self.color_cvt = cv2.cvtColor(self.color_image, cv2.COLOR_BGR2RGB)

                self.frame_number = str(self.color_frame.get_frame_number())

                self.img_work(mode='Video Mode', img=self.color_cvt)
                self.img_origin = self.color_cvt

                cv2.namedWindow("Color Stream", cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Color Stream", self.color_cvt)
                key = cv2.waitKeyEx(1000)

                # if pressed escape exit program
                if key == 27 or key == 113 or cv2.getWindowProperty('Color Stream', cv2.WND_PROP_VISIBLE) < 1:
                    break

                elif key == 32:  # press space
                    self.frame_dict, self.i = self.get_attribute(color=self.frame_number, weg_id=self.weg_id)
                    search_frame = copy.copy(self.color_cvt)
                    self.img_work(mode='Searching', img=search_frame)
                    cv2.imshow("Color Stream", search_frame)
                    cv2.waitKey(1)
                    item = self.get_attribute(color=self.frame_number, weg_id=self.weg_id)
                    if item is not None:
                        self.measure()
                elif key == 2555904:  # press right
                    frames = self.pipeline.wait_for_frames()
                    self.color_frame = frames.get_color_frame()
                elif key == 2424832:  # press left
                    pass
                elif key == 112:  # press p
                    print('PPPP')
                else:
                    frames = self.pipeline.wait_for_frames()
                    self.color_frame = frames.get_color_frame()

        except RuntimeError:
            print('file ended')
            cv2.destroyAllWindows()

        finally:
            print('finish')
            cv2.destroyAllWindows()
            os._exit(0)
            self.pipeline.stop()


    def get_attribute(self, color, weg_id):
        for obj in self.frame_list:
            if obj[0] == weg_id and abs(int(obj[2]) - int(color)) < 5:
                i = self.frame_list.index(obj)
                obj = dict(zip(self.title, obj))
                return obj, i

    def index_to_obj(self):
        if self.i >= len(self.frame_list):
            self.i = self.i % len(self.frame_list) +1
        content = self.frame_list[self.i]
        self.frame_dict = dict(zip(self.title, content))

    def measure(self):
        self.frame_getter('Depth')
        self.img_origin = self.img_work(mode='Measure Mode', img=self.img_origin)
        self.img_copy = copy.copy(self.img_origin)

        cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback("Color Stream", self.draw)
        cv2.imshow("Color Stream", self.img_copy)
        while True:
            key = cv2.waitKeyEx(10)
            if key & 0xFF == ord('q') or key == 27:
                break
            elif cv2.getWindowProperty('Color Stream', cv2.WND_PROP_VISIBLE) < 1:
                break
            elif key == 2555904:  # press right
                self.i += 1
                self.new_frame(1)

            elif key == 2424832:  # press left
                self.i -= 1
                self.new_frame(-1)

    def new_frame(self, direction):
        self.img_work(mode='Searching', img=self.img_copy)
        cv2.imshow("Color Stream", self.img_copy)
        cv2.waitKeyEx(10)
        self.index_to_obj()
        self.frame_getter('Color', direction=direction)
        self.color_intrin = self.color_frame.profile.as_video_stream_profile().intrinsics
        self.color_image = np.asanyarray(self.color_frame.get_data())
        self.color_cvt = cv2.cvtColor(self.color_image, cv2.COLOR_BGR2RGB)
        self.frame_number = str(self.color_frame.get_frame_number())
        self.frame_getter('Depth')
        self.img_origin = self.img_work(mode='Measure Mode', img=self.color_cvt)
        self.img_copy = copy.copy(self.img_origin)
        cv2.imshow("Color Stream", self.img_origin)

    def draw(self, event, x, y, flags, params):
        img = copy.copy(self.img_copy)
        #print event,x,y,flags,params
        if event == 1:
            self.ix = x
            self.iy = y
            cv2.imshow("Color Stream", self.img_copy)
        elif event == 4:
            img = self.img_copy
            self.img_work(img=img, mode='calc', x=x, y=y)
            cv2.imshow("Color Stream", img)
        elif event == 2:
            self.img_copy = copy.copy(self.img_origin)
            cv2.imshow("Color Stream", self.img_copy)
        elif flags == 1:
            self.img_work(img=img, mode='calc', x=x, y=y)
            cv2.imshow("Color Stream", img)



    def img_work(self, mode, img, frame_num='', x=0, y=0):
        if 'Measure' in mode:
            depth_image = np.asanyarray(self.depth_frame.get_data())
            grey_color = 0
            depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
            grey_color = 0
            depth_image_3d = np.dstack(
                (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
            img = np.where((depth_image_3d <= 0), grey_color, img)

        font = cv2.FONT_ITALIC
        fontScale = 1
        fontColor = (0, 0, 0)
        lineType = 2

        rec1, rec2 = (540, 20), (640, 60)
        text = self.frame_number
        bottomLeftCornerOfText = (550, 50)
        cv2.rectangle(img, rec1, rec2, (255, 255, 255), -1)
        cv2.putText(img, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

        if mode == 'calc':
            pt1, pt2 = (self.ix, self.iy), (x, y)
            ans = self.calculate_distance(x, y)
            text = '{0:.3}'.format(ans)
            bottomLeftCornerOfText = (self.ix + 10, (self.iy - 10))
            rec1, rec2 = (self.ix + 10, (self.iy - 5)), (self.ix + 80, self.iy - 35)

            cv2.line(img, pt1=pt1, pt2=pt2, color=(0, 0, 230), thickness=3)

        else:
            rec1, rec2 = (700, 20), (950, 60)
            text = mode
            bottomLeftCornerOfText = (710, 50)

        cv2.rectangle(img, rec1, rec2, (255, 255, 255), -1)
        cv2.putText(img, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        return img


    def calculate_distance(self, x, y):
        color_intrin = self.color_intrin
        ix, iy = self.ix, self.iy
        udist = self.depth_frame.get_distance(ix, iy)
        vdist = self.depth_frame.get_distance(x, y)
        # print udist,vdist
        if udist ==0.00 or vdist ==0.00:
            dist = 'NaN'

        else:
            point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [ix, iy], udist)
            point2 = rs.rs2_deproject_pixel_to_point(color_intrin, [x, y], vdist)
            # print str(point1)+str(point2)

            dist = math.sqrt(
                math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2) + math.pow(
                    point1[2] - point2[2], 2))
        # print 'distance: '+ str(dist)

        return dist

    def frame_getter(self, mode, direction=1):
        align_to = rs.stream.color
        align = rs.align(align_to)
        while True:
            self.index_to_obj()
            num = self.frame_dict[mode]
            frames = self.pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            if mode == 'Color':
                frame = aligned_frames.get_color_frame()
                self.color_frame_num = frame.get_frame_number()
                self.color_frame = frame
            else:
                frame = aligned_frames.get_depth_frame()
                self.depth_frame_num = frame.get_frame_number()
                self.depth_frame = frame
            if not frame:
                continue
            frame_num = rs.frame.get_frame_number(frame)
            self.count_search(frame_num, int(num), direction)
            print('Suchen {}: {}, Jetzt: {}'.format(mode, num, frame_num))

            if abs(int(frame_num) - int(num)) < 5:
                print('match {} {}'.format(mode, frame_num))
                self.search_count = 0
                break

    def count_search(self, now, target, direction):
        if abs(now - target) < 100:
            self.search_count += 1
            if self.search_count >= 10:
                print(str(target) + ' nicht gefunden, suchen naechste frame')
                self.i += direction

def main():
    Arc_Real(r'X:/Mittelweser/0604/jpg/064_021-514.jpg')


if __name__ == '__main__':
    main()
