from WindowMgmt import NosWindowNotFound, NonAdminUser, get_nostale_windows
from Interface import MainInterface
from multiprocessing import Process


if __name__ == '__main__':
    windows = None
    try:
        windows = get_nostale_windows()
    except (NosWindowNotFound, NonAdminUser) as e:
        print(e.message)

    if windows:
        interfaces = [MainInterface(window) for window in windows]

        procs = []
        for interf in interfaces:
            proc = Process(target=interf.run)
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

    input('Press enter to exit.')
