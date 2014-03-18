
from gi.repository import GObject
GObject.threads_init()
import threading


class SpinnerThread(threading.Thread):
    def __init__(self, spinner, wait_for_function):
        threading.Thread.__init__(self)
        self.callback = self.work_finished_cb
        self.spinner = spinner
        self.function = wait_for_function

    def run(self):
        # Run function we're waiting for here
        self.function()
        # The callback runs a GUI task, so wrap it!
        GObject.idle_add(self.callback)

    def work_finished_cb(self):

        self.spinner.stop()
        self.spinner.set_visible(False)