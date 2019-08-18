

__author__ = 'Junya Kaneko<junya@mpsamurai.org>'


import time
import cv2
import numpy as np
from mpstello.tello import Tello
from watchdog import controller


def transform_frame_to_image(frame):
    if frame is not None and frame.body is not None:
        return cv2.resize(frame.body, (360, 240))
    else:
        return np.zeros((240, 360, 3), np.uint8)


def execute_command(key, tello):
    if key == ord('t'):
        tello.commands.takeoff()
    elif key == ord('l'):
        tello.commands.land()
    elif key == ord('w'):
        tello.commands.up(50)
    elif key == ord('a'):
        tello.commands.left(50)
    elif key == ord('d'):
        tello.commands.right(50)
    elif key == ord('x'):
        tello.commands.down(50)
    elif key == ord('s'):
        tello.commands.forward(50)
    elif key == ord('z'):
        tello.commands.back(50)
    elif key == ord('v'):
        if not tello.is_video_started:
            tello.commands.streamon()
            tello.start_video()
        else:
            tello.commands.streamoff()
            tello.stop_video()
    elif key == ord('c'):
        tello.commands.command()


def input_loop(tello):
    tracker = controller.Tracker()
    tello.start()
    tello.commands.command()
    while True:
        image = transform_frame_to_image(tello.video)
        cv2.imshow('tello', image)
        key = cv2.waitKey(1) & 0XFF
        if key == ord('q'):
            tello.commands.land()
            break
        if not tello.response is not None or tello.response.is_set:
            if key:
                execute_command(key, tello)
            else:
                for command in tracker.generate_commands(image):
                    tello.commands.execute(command[0], command[1])
        time.sleep(0.1)
    cv2.destroyAllWindows()
    tello.stop_all()


if __name__ == '__main__':
    tello = Tello()
    input_loop(tello)
