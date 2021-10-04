from WindowMgmt import NosWindowNotFound, NonAdminUser
from Interface import MainInterface

interface = MainInterface()

if __name__ == '__main__':
    try:
        interface.initialize()
        interface.run()
    except (NosWindowNotFound, NonAdminUser) as e:
        print(e.message)

input('Press enter to exit.')
