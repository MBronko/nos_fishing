from WindowMgmt import NosWindowNotFound
from Interface import MainInterface

interface = MainInterface()

if __name__ == '__main__':
    try:
        interface.initialize()
    except NosWindowNotFound as e:
        print(e.message)
        exit()

    interface.run()
