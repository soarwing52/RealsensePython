# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import os.path for file path manipulation
import os.path
from matplotlib import pyplot as plt
from matplotlib.widgets2 import Ruler

from datetime import datetime


file_name = 'record.bag'
print file_name
# Configure depth and color streamsq
pipeline = rs.pipeline()
config = rs.config()
config.enable_device_from_file(file_name)

# Start streaming from file
profile = pipeline.start(config)
device = profile.get_device()
playback = device.as_playback()
playback.set_real_time(False)

print 'profile got'
#align to color map
align_to = rs.stream.color
align = rs.align(align_to)
print 'aligned'

i = 1
while i < 100:
        print i
        playback.resume()
        for x in range(10):
            pipeline.wait_for_frames()

        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        playback.pause()
        var = rs.frame.get_frame_number(color_frame)
        print 'frame number: '+ str(var)
        time_stamp = rs.frame.get_timestamp(color_frame)
        time = datetime.now()
        print 'timestampe: ' + str(time_stamp)
        domain = rs.frame.get_frame_timestamp_domain(color_frame)
        print domain
        meta = rs.frame.get_data(color_frame)
        print 'metadata: ' + str(meta)

        depth_stream = profile.get_stream(rs.stream.depth)
        inst = rs.video_stream_profile.intrinsics
        # get intrinsics of the frames
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
        depth_to_color_extrin = depth_frame.profile.get_extrinsics_to(color_frame.profile)
        print 'instrincts got'

        # Convert images to numpy arrays
        depth_color = rs.colorizer().colorize(depth_frame)
        depth_image = np.asanyarray(depth_color.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        print 'got image'

        xCoord = np.arange(0, 6, 1)
        yCoord = [0, 1, -3, 5, -3, 0]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        markerprops = dict(marker='o', markersize=5, markeredgecolor='red')
        lineprops = dict(color='red', linewidth=2)
        plt.imshow(depth_image)
        ax.grid(True)
        figManager = plt.get_current_fig_manager().window.state('zoomed')



        ruler = Ruler(ax=ax,
                      depth_frame=depth_frame,
                      color_intrin=color_intrin,
                      useblit=True,
                      markerprops=markerprops,
                      lineprops=lineprops,
                      )

        plt.show()


        cv2.waitKey(1000)
        cv2.destroyAllWindows()

        i += 1






