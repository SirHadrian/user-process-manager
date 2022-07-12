from subprocess import PIPE, Popen, run
from psutil import Process
from py_cui import PyCUI
from py_cui.keys import KEY_ENTER


class UIManager:
    def __init__(self, master: PyCUI):
        # Get the root window
        self.master = master

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

    def execute_command(self):
        command = self.command_block.get()
        if command == "":
            return
        output = run(command, stdout=PIPE, stderr=PIPE, text=True, shell=True)
        self.menu.add_item(command)
        self.command_block.clear()
        if output.returncode == 0:
            self.output.set_text(output.stdout)
        else:
            self.output.set_text(output.stderr)


root = PyCUI(9, 9)
root.toggle_unicode_borders()
root.set_title("Process Manager")

manager = UIManager(root)
manager.start()



