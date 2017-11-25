__author__ = 'fuxy'

from emudaemon import emudaemondebugger


def start_daemon(emud):
    emud.start()


def stop_daemon(emud):
    emud.stop()


def restart_daemon(emud):
    emud.restart()


def init_daemon(emud):
    emud.init_daemon()


commands = {
    'start': start_daemon,
    'stop': stop_daemon,
    'restart': restart_daemon,
    'init': init_daemon
}


def exec_ext2emud(args):
    emud = emudaemondebugger.EmulatorDaemonDebugger('ext2emud.pid', 'ext2emud.key', args.partition_name)
    commands[args.action](emud)
