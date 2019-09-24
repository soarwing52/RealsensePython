import pyrealsense2 as rs
import numpy as np
import cv2
import os
import copy, math
import Tkinter


class Arc_Real:
    def __init__(self, jpg_path):
        # Basic setting
        self.width, self.height = self.screen_size()
        self.x_ratio, self.y_ratio = self.screen_ratio()

        # Data from txt log file
        BagFilePath = os.path.abspath(jpg_path)
        file_dir = os.path.dirname(BagFilePath)
        Pro_Dir = os.path.dirname(file_dir)
        self.weg_id, target_color = os.path.splitext(os.path.basename(BagFilePath))[0].split('-')

        with open('{}/shp/matcher.txt'.format(Pro_Dir), 'r') as txtfile:
            self.title = [elt.strip() for elt in txtfile.readline().split(',')]
            self.frame_list = [[elt.strip() for elt in line.split(',')] for line in txtfile if line.split(',')[0] == self.weg_id]

        self.frame_dict, self.i = self.get_attribute(color=target_color, weg_id=self.weg_id)
        file_name = '{}\\bag\\{}.bag'.format(Pro_Dir, self.weg_id)
        # Start Pipeline
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device_from_file(file_name)
        config.enable_all_streams()
        profile = self.pipeline.start(config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)

        self.frame_getter('Color') # Get Color Frame with the matching frame number from self.frame_dict
        mode = 'Video Mode'
        direction = 1
        while True:
            img = self.frame_to_image()
            self.img_work(mode=mode, img=img)
            cv2.namedWindow("Color Stream", cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Color Stream", img)

            if mode == 'Measure Mode':
                self.img_origin = self.img_work(mode='Measure Mode', img=img)
                self.img_copy = copy.copy(self.img_origin)
                cv2.setMouseCallback("Color Stream", self.draw)
                cv2.imshow("Color Stream", self.img_copy)

            key = cv2.waitKeyEx(0)

            # if pressed escape exit program
            if key == 27 or key == 113 or cv2.getWindowProperty('Color Stream', cv2.WND_PROP_VISIBLE) < 1:
                break

            elif key == 32:  # press space
                if mode == 'Measure Mode':
                    mode = 'Video Mode'
                else:
                    self.frame_dict, self.i = self.get_attribute(color=self.color_frame_num, weg_id=self.weg_id)
                    self.img_work(mode='Searching', img=img)
                    cv2.imshow("Color Stream", img)
                    cv2.waitKey(1)
                    item = self.get_attribute(color=self.color_frame_num, weg_id=self.weg_id)
                    if item is not None:
                        print item
                        mode = 'Measure Mode'

            elif key == 2555904:  # press right
                self.i += 1
                direction = 1
            elif key == 2424832:  # press left
                self.i -= 1
                direction = -1

            if mode == 'Measure Mode':
                self.img_work(mode='Searching', img=img)
                cv2.imshow("Color Stream", img)
                cv2.waitKey(1)
                while True:
                    Color, Depth = self.frame_getter('Color'), self.frame_getter('Depth')
                    if Color and Depth:
                        break
                    else:
                        self.i += direction

            if mode != 'Measure Mode':
                frames = self.pipeline.wait_for_frames()
                self.color_frame = frames.get_color_frame()
                self.color_frame_num = self.color_frame.get_frame_number()

        print('finish')
        cv2.destroyAllWindows()
        os._exit(0)
        self.pipeline.stop()

    def screen_size(self):
        root = Tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        return int(width * 0.8), int(height * 0.8)

    def screen_ratio(self):
        img_size = (1920.0, 1080.0)
        screen = self.screen_size()
        width_ratio, height_ratio = screen[0]/img_size[0],screen[1]/img_size[1]
        return width_ratio, height_ratio

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

    def draw(self, event, x, y, flags, params):
        img = copy.copy(self.img_copy)
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

    def img_work(self, mode, img, x=0, y=0):
        if 'Measure' in mode: # show black at NAN
            depth_image = np.asanyarray(self.depth_frame.get_data())
            grey_color = 0
            depth_image_3d = np.dstack(
                (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
            depth_image_3d= cv2.resize(depth_image_3d, self.screen_size())
            img = np.where((depth_image_3d <= 0), grey_color, img)

        font = cv2.FONT_ITALIC
        fontScale = 1
        fontColor = (0, 0, 0)
        lineType = 2

        # Add frame number
        mid_line_frame_num = int(self.width/4)
        rec1, rec2 = (mid_line_frame_num - 50, 20), (mid_line_frame_num + 50, 60)
        text = str(self.color_frame_num)
        bottomLeftCornerOfText = (mid_line_frame_num - 45, 50)
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
            mid_line_screen = int(self.width/2)
            rec1, rec2 = (mid_line_screen-100, 20), (mid_line_screen + 130, 60)
            text = mode
            bottomLeftCornerOfText = (mid_line_screen - 95, 50)

        cv2.rectangle(img, rec1, rec2, (255, 255, 255), -1)
        cv2.putText(img, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        return img

    def calculate_distance(self, x, y):
        color_intrin = self.color_intrin
        x_ratio, y_ratio = self.x_ratio, self.y_ratio
        ix, iy = int(self.ix/x_ratio), int(self.iy/y_ratio)
        x, y = int(x/x_ratio), int(y/y_ratio)
        udist = self.depth_frame.get_distance(ix, iy)
        vdist = self.depth_frame.get_distance(x, y)
        if udist ==0.00 or vdist ==0.00:
            dist = 'NaN'
        else:
            point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [ix, iy], udist)
            point2 = rs.rs2_deproject_pixel_to_point(color_intrin, [x, y], vdist)
            dist = math.sqrt(
                math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2) + math.pow(
                    point1[2] - point2[2], 2))
        return dist

    def frame_getter(self, mode):
        align_to = rs.stream.color
        align = rs.align(align_to)
        count = 0
        while True:
            self.index_to_obj()
            num = self.frame_dict[mode]
            frames = self.pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            if mode == 'Color':
                frame = aligned_frames.get_color_frame()
                self.color_frame_num = frame.get_frame_number()
                self.color_intrin = frame.profile.as_video_stream_profile().intrinsics
                self.color_frame = frame
            else:
                frame = aligned_frames.get_depth_frame()
                self.depth_frame_num = frame.get_frame_number()
                self.depth_frame = frame

            frame_num = frame.get_frame_number()

            count = self.count_search(count, frame_num, int(num))
            print 'Suchen {}: {}, Jetzt: {}'.format(mode, num, frame_num)

            if abs(int(frame_num) - int(num)) < 5:
                print('match {} {}'.format(mode, frame_num))
                return frame
            elif count > 10:
                print(num + ' nicht gefunden, suchen naechste frame')
                return None


    def frame_to_image(self):
        color_image = np.asanyarray(self.color_frame.get_data())
        color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        color_final = cv2.resize(color_cvt, (self.width, self.height))
        return color_final

    def count_search(self, count, now, target):
        if abs(now - target) < 100:
            count += 1
            print  'search count:{}'.format(count)
        return count


def main():
    Arc_Real(r'X:/WER_Werl/Realsense/jpg/0917_012-1916.jpg')

if __name__ == '__main__':
    main()
