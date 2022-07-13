from datetime import datetime
from subprocess import PIPE, Popen
import prettytable
import psutil
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

    def get_cpu_percent(self):
        return f'{self._process.cpu_percent()}%'

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
            "PID | Process | Status | CPU",
            0, 0,
            row_span=7,
            column_span=5
        )

        # Execute command
        self.command_block = self.master.add_text_box(
            "Exec",
            7, 0,
            row_span=1,
            column_span=5
        )
        self.command_block.add_key_command(KEY_ENTER, self.execute_command)
        self.master.move_focus(self.command_block)

        # Display system info
        self.system_info = self.master.add_text_block(
            "System Info",
            0, 5,
            row_span=9,
            column_span=4
        )
        self.system_info.set_text(UIManager.display_system_info())

    @staticmethod
    def display_system_info():
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        battery = psutil.sensors_battery().percent
        uptime = psutil.boot_time()
        uptime = datetime.fromtimestamp(psutil.boot_time()).strftime("%H:%M:%S")
        return f'\nUpTime [ {uptime} ] \t Battery [ {round(battery)}% ]\n\n' \
               f'\n[ Memory ]\n\n => Total: {UIManager.bytes_to_gb(memory.total)} | Free: {UIManager.bytes_to_gb(memory.inactive)} | Used: {UIManager.bytes_to_gb(memory.used)} | {round(memory.percent)}%\n\n' \
               f'\n[ Swap Memory ]\n\n => Total: {UIManager.bytes_to_gb(swap.total)} | Free: {UIManager.bytes_to_gb(swap.free)} | Used: {UIManager.bytes_to_gb(swap.used)} | {round(swap.percent)}%\n\n'

    @staticmethod
    def bytes_to_gb(bytes_size: int) -> float:
        return round(bytes_size / 1000000000, 1)

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
                name = f'{proc.get_pid()} ' \
                       f'| {proc.cmd} ' \
                       f'| {proc.get_status()} ' \
                       f'| {proc.get_cpu_percent()} '
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
