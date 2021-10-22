from WindowMgmt import NosWindowNotFound, NonAdminUser, get_nostale_windows
from Interface import MainInterface
from multiprocessing import Process


if __name__ == '__main__':
    windows = None
    try:
        windows = get_nostale_windows()
    except (NosWindowNotFound, NonAdminUser) as e:
        print(e.message)
        input('Press enter to exit.')
        exit(0)

    if windows:
        interfaces = [MainInterface(window) for window in windows]

        processes = []
        for interface in interfaces:
            prc = Process(target=interface.run)
            processes.append(prc)
            prc.start()

        processes[0].join()
