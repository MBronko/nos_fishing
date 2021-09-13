from WindowMgmt import *


def main_loop():
    recognized_pixels = set()
    pixel_recognition_time = 2

    draw_screen()
    mouse_position()

    log_message('Fishing started')
    wait_time(2, constant=True)

    player.all_actions()

    start = time.perf_counter()
    while True:
        draw_screen()
        mouse_position()

        screenshot = get_screenshot(calculate_bounds(1, 1))

        pixel_check = tuple(screenshot[0][0])

        if time.perf_counter() - start < pixel_recognition_time:
            recognized_pixels.add(pixel_check)

        to_pull = pixel_check not in recognized_pixels

        if to_pull or time.perf_counter() - start > 20:
            if time.perf_counter() - start > 20:
                log_message('Waiting too long, reseting recognized pixels')
                recognized_pixels = set()

            player.all_actions()

            start = time.perf_counter()


if __name__ == '__main__':
    main_loop()
