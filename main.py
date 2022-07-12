from subprocess import PIPE, Popen

import psutil
from psutil import Process
from py_cui import PyCUI
from py_cui.keys import KEY_ENTER


class UserProcess(object):
    def __init__(self, pid):
        self._process = Process(pid)
        self.name = ' '.join(self._process.cmdline())

    def get_pid(self):
        return str(self._process.pid)

    def status(self):
        return self._process.status()

    @property
    def get_name(self):
        return self.name


class UIManager:
    def __init__(self, master: PyCUI):
        # Get the root window
        self.master = master

        # Started processes
        self.proc_list = []

        # Add widgets

        # Process List
        self.menu = master.add_scroll_menu(
            "Processes",
            0, 0,
            row_span=7,
            column_span=4
        )

        # Execute command
        self.command_block = master.add_text_box(
            "Exec",
            7, 0,
            row_span=1,
            column_span=4
        )
        self.command_block.add_key_command(KEY_ENTER, self.execute_command)

        # Process Output
        self.output = master.add_text_block(
            "Output",
            0, 5,
            row_span=9,
            column_span=4
        )

    def start(self):
        self.master.start()

    def check_processes_status(self):
        if not self.proc_list:
            return

        self.menu.clear()
        refresh = []
        for i in range(len(self.proc_list)):
            try:
                self.menu.add_item(
                    self.proc_list[i].get_name
                    + " --- " +
                    self.proc_list[i].status()
                    + " --- " +
                    self.proc_list[i].get_pid())
                refresh.append(self.proc_list[i])
            except psutil.NoSuchProcess:
                pass
        self.proc_list = refresh

    def execute_command(self):
        command = self.command_block.get()
        if command == "":
            return
        proc = Popen(command, stdout=PIPE, stderr=PIPE, text=True, shell=True)
        # Add new process to list
        self.proc_list.append(UserProcess(proc.pid))
        # Check processes status
        self.check_processes_status()
        # Refresh process list
        self.command_block.clear()


root = PyCUI(9, 9)
root.toggle_unicode_borders()
root.set_title("Process Manager")

ui_manager = UIManager(root)
ui_manager.start()
