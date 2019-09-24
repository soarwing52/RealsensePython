# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2

# Import os.path for file path manipulation
import os.path

def dir_generate(in_dir):
    """test if this folder exist, if not, create one"""
    in_dir = str(in_dir)
    if not os.path.exists(in_dir):
        try:
            os.makedirs(in_dir, 0o700)
        finally:
            pass
    return in_dir

def depth_to_png(input_file):
    """create jpg of Depth image with opencv"""
    bag_dir = os.path.dirname(input_file)
    project_dir = os.path.dirname(bag_dir)
    png_dir = dir_generate(project_dir + '/png')
    filenum = os.path.splitext(os.path.split(input_file)[1])[0]
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_all_streams()
        config.enable_device_from_file(input_file,False)
        profile = pipeline.start(config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)
        align_to = rs.stream.color
        align = rs.align(align_to)

        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth_color = rs.colorizer().colorize(depth_frame)
            depth_color_image = np.asanyarray(depth_color.get_data())
            var = rs.frame.get_frame_number(depth_frame)
            cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Depth Stream", depth_color_image)
            print 'compressing {}-{}.png'.format(filenum,str(var))
            cv2.imwrite('{}/{}-{}-D.png'.format(png_dir, filenum,str(var)), depth_color_image,[cv2.IMWRITE_PNG_COMPRESSION,1])
            key = cv2.waitKey(100)
            # if pressed escape exit program
            if key == 27:
                cv2.destroyAllWindows()
                break

    except RuntimeError:
        print 'frame covert finished for '+input_file
        cv2.destroyAllWindows()
    finally:
        pass


def color_to_png(file_name):
    """create jpg of RGB image with opencv"""
    bag_dir = os.path.dirname(file_name)
    project_dir = os.path.dirname(bag_dir)
    png_dir = dir_generate(project_dir + '/png')
    filenum = os.path.splitext(os.path.split(file_name)[1])[0]
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_all_streams()
        config.enable_device_from_file(file_name, False)
        profile = pipeline.start(config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)
        while True:
            frames = pipeline.wait_for_frames()
            frames.keep()
            if frames:
                color_frame = frames.get_color_frame()
                var = rs.frame.get_frame_number(color_frame)
                print 'frame number: ' + str(var)
                time_color = rs.frame.get_timestamp(color_frame)
                color_image = np.asanyarray(color_frame.get_data())
                color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

                cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
                cv2.imshow("Color Stream",color_cvt)
                cv2.imwrite('{}/{}_c_{}.png'.format(png_dir,filenum,var),color_cvt)
                print '{}/{}_c_{}.png'.format(png_dir,filenum,var)
                key = cv2.waitKey(1)
                # if pressed escape exit program
                if key == 27:
                    cv2.destroyAllWindows()
                    break
    except RuntimeError:
        print("No more frames arrived, reached end of BAG file!")
        cv2.destroyAllWindows()
    finally:
        pipeline.stop()
        pass

def main():
    file_name = raw_input('file name: \n')
    color_to_png(file_name)
    depth_to_png(file_name)

if __name__ == '__main__':
    main()