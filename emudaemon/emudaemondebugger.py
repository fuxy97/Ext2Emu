from emudaemon import emudaemon
import logging
from datetime import datetime


class EmulatorDaemonDebugger(emudaemon.EmulatorDaemon):
    def __init__(self, pid_file, key_file, partition_name):
        logging.basicConfig(level=logging.DEBUG, filename='logs/emudaemon.log')
        super().__init__(pid_file, key_file, partition_name, 'logs/stdout.log')

    def run(self):
        try:
            super().run()
        except:
            logging.exception(str(datetime.now()) + ':')
