from subprocess import PIPE, Popen
from psutil import Process, NoSuchProcess
from py_cui import PyCUI
from py_cui.keys import KEY_ENTER


class UserProcess(object):
    def __init__(self, spawn, wrap):
        self._popen: Popen = spawn
        self._process: Process = wrap

        self._identifier = None
        self._cmd = ' '.join(self._process.cmdline())

    def get_pid(self):
        return self._process.pid

    def get_status(self):
        return self._process.status()

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, val):
        self._identifier = val

    @property
    def cmd(self):
        return self._cmd

    @staticmethod
    def compute_identifier(value: str) -> int:
        if value == "":
            return -1
        return sum(ord(i) for i in value)


class UIManager:
    def __init__(self, x, y):
        # Get the root window
        self.master = PyCUI(x, y)

        # Started processes
        self.process_list = []

        # Add widgets

        # Process List
        self.menu = self.master.add_scroll_menu(
            "Processes",
            0, 0,
            row_span=7,
            column_span=4
        )

        # Execute command
        self.command_block = self.master.add_text_box(
            "Exec",
            7, 0,
            row_span=1,
            column_span=4
        )
        self.command_block.add_key_command(KEY_ENTER, self.execute_command)

        # Process Output
        self.output = self.master.add_text_block(
            "Output",
            0, 5,
            row_span=9,
            column_span=4
        )

    def start(self):
        self.master.start()

    def set_title(self, title):
        self.master.set_title(title)

    def set_unicode_border(self):
        self.master.toggle_unicode_borders()

    def check_processes_status(self):
        if not self.process_list:
            return
        self.menu.clear()
        refresh = []
        for proc in self.process_list:
            try:
                name = f'{proc.cmd} ' \
                       f'- {proc.get_status()} -' \
                       f' {proc.get_pid()} '
                self.menu.add_item(name)

                identifier = UserProcess.compute_identifier(name)
                proc.identifier = identifier

                refresh.append(proc)
            except NoSuchProcess:
                pass
        self.process_list = refresh

    def execute_command(self):
        command = self.command_block.get()
        if command == "":
            return
        # Spawn new process with shell
        spawn_process = Popen(command, stdout=PIPE, stderr=PIPE, text=True, shell=True)
        # Wrap the new process in a Process object
        wrap_process = Process(spawn_process.pid)
        # Wrapper for proc objs
        user_process = UserProcess(spawn_process, wrap_process)
        # Add process management list
        self.process_list.append(user_process)
        # Refresh process list
        self.check_processes_status()
        # Clear command box
        self.command_block.clear()


ui_manager = UIManager(9, 9)
ui_manager.set_unicode_border()
ui_manager.set_title("Process Manager")
ui_manager.start()
