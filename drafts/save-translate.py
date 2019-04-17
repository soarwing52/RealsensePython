import pyrealsense2 as rs
import numpy as np
from matplotlib import pyplot as plt
import cv2
import math
from matplotlib import pyplot as plt
from matplotlib.widgets import Ruler

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280,720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280,720, rs.format.bgr8, 30)
# Start streaming from file
profile = pipeline.start(config)

#Define filters
dec = rs.decimation_filter(1)
to_dasparity = rs.disparity_transform(True)
dasparity_to = rs.disparity_transform(False)
spat = rs.spatial_filter()
hole = rs.hole_filling_filter(2)
temp = rs.temporal_filter()

#sensor settings
dev = profile.get_device()
depth_sensor = dev.first_depth_sensor()
depth_sensor.set_option(rs.option.visual_preset, 4)
range = depth_sensor.get_option_range(rs.option.visual_preset)
preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)

#align to color map
align_to = rs.stream.color
align = rs.align(align_to)

# Get frameset of depth
frames = pipeline.wait_for_frames()
aligned_frames = align.process(frames)
global depth_frame
depth_frame = aligned_frames.get_depth_frame()
color_frame = frames.get_color_frame()
depth = dec.process(depth_frame)
depth_dis = to_dasparity.process(depth)
depth_spat = spat.process(depth_dis)
depth_temp = temp.process(depth_spat)
depth_hole = hole.process(depth_temp)
global depth_final
depth_final = dasparity_to.process(depth_hole)
depth_color = rs.colorizer().colorize(depth_final)

#depth stream
depth_stream = profile.get_stream(rs.stream.depth)
inst = rs.video_stream_profile.intrinsics

depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
depth_to_color_extrin = depth_frame.profile.get_extrinsics_to(color_frame.profile)

# Convert images to numpy arrays
depth_image = np.asanyarray(depth_color.get_data())
color_image = np.asanyarray(color_frame.get_data())

# Apply colormap on depth image (image must be converted to 8-bit per pixel first)
#depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, None, 0.5, 0), cv2.COLORMAP_JET)

# Stack both images horizontally
images = color_image

font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(images, preset_name, (60, 80), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


drawing = False # true if mouse is pressed
mode = True # if True, draw rectangle. Press 'm' to toggle to curve

def draw_circle(event,x,y,flags,param):
    global ix,iy,drawing,mode

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x0, y0 = x, y
        print 'ixiy=' + str(ix)+','+str(iy)
        print 'x0y0=' + str(x0) + ',' + str(y0)
        udist = depth_frame.get_distance(ix, iy)
        vdist = depth_frame.get_distance(x0, y0)
        print udist,vdist

        point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [ix, iy], udist)
        point2 = rs.rs2_deproject_pixel_to_point(color_intrin, [x0, y0], vdist)
        print point1,point2
        dist = math.sqrt(
            math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1],2) + math.pow(
                point1[2] - point2[2], 2))
        print 'distance: '+ str(dist)
        if mode == True:
            cv2.line(images,(ix,iy),(x,y),(0,255,0),100)
        else:
            cv2.circle(images,(x,y),5,(0,0,255),100)


cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('RealSense',draw_circle)
cv2.imshow('RealSense', images)
cv2.waitKey()



