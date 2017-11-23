__author__ = 'fuxy'

import os
import sys
import signal
import time
import atexit


class Daemon(object):
    def __init__(self, pidfile, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull,
                 home_dir='.', umask=0o22):
        self.daemon_alive = True
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.umask = umask
        self.home_dir = home_dir

    def daemonize(self):
        # double-fork magic
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir(self.home_dir)
        os.setsid()
        os.umask(self.umask)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        def sigtermhandler(signum, stack_frame):
            self.daemon_alive = False
            sys.exit()

        # set handlers for signals
        signal.signal(signal.SIGTERM, sigtermhandler)
        signal.signal(signal.SIGINT, sigtermhandler)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delpid)
        atexit.register(self.finalize)

        # write pid file
        with open(self.pidfile, 'w+') as pf:
            pf.write('%d\n' % os.getpid())

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        # check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        # get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # try killing the daemon process
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        # restart daemon
        self.stop()
        self.start()

    def finalize(self):
        """Override this method when you derive Daemon"""
        pass

    def run(self):
        """Override this method when you derive Daemon"""
        pass
