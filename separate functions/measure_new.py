import pyrealsense2 as rs
import numpy as np
import cv2
import copy
import math

class ARC:
    def __init__(self):
        bag = r'0626_005.bag'
        self.pipeline = rs.pipeline()

        config = rs.config()
        config.enable_device_from_file(bag, False)
        config.enable_all_streams()

        profile = self.pipeline.start(config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)


    def video(self):
        align_to = rs.stream.color
        align = rs.align(align_to)
        for i in range(10):
            self.pipeline.wait_for_frames()
        while True:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            self.depth_frame = depth_frame

            color_image = np.asanyarray(color_frame.get_data())
            self.color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

            depth_color_frame = rs.colorizer().colorize(depth_frame)

            # Convert depth_frame to numpy array to render image in opencv
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            self.show(color_cvt)

            break
            # Render image in opencv window
            # Create opencv window to render image in


    def show(self, img):
        self.img_origin = img
        self.img_copy = copy.copy(self.img_origin)
        cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)

        cv2.setMouseCallback("Color Stream", self.draw)
        while True:
            cv2.imshow("Color Stream", self.img_copy)
            key = cv2.waitKey(10)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break

    def draw(self, event,x,y,flags,params):
        img = copy.copy(self.img_copy)
        #print event,x,y,flags,params
        if(event==1):
            self.ix = x
            self.iy = y
        elif event == 4:
            img = self.img_copy
            self.img_work(img, x,y)
        elif event == 2:
            self.img_copy = copy.copy(self.img_origin)
        elif(flags==1):
            self.img_work(img,x,y)
            cv2.imshow("Color Stream", img)

    def img_work(self, img,x,y):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        fontColor = (0, 0, 0)
        lineType = 2

        ans = self.calculate_distance(x, y)
        cv2.line(img, pt1=(self.ix, self.iy), pt2=(x, y), color=(255, 255, 255), thickness=3)
        cv2.rectangle(img, (self.ix, self.iy), (self.ix + 80, self.iy - 20), (255, 255, 255), -1)
        cv2.putText(img, '{0:.5}'.format(ans), (self.ix, self.iy), font, fontScale, fontColor,
                    lineType)

    def calculate_distance(self,x,y):
        color_intrin = self.color_intrin
        ix,iy = self.ix, self.iy
        udist = self.depth_frame.get_distance(ix,iy)
        vdist = self.depth_frame.get_distance(x, y)
        #print udist,vdist

        point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [ix, iy], udist)
        point2 = rs.rs2_deproject_pixel_to_point(color_intrin, [x, y], vdist)
        #print str(point1)+str(point2)

        dist = math.sqrt(
            math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1],2) + math.pow(
                point1[2] - point2[2], 2))
        #print 'distance: '+ str(dist)
        return dist


if __name__ == '__main__':
    ARC().video()
