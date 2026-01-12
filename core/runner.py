import subprocess

from PyQt5.QtCore import QThread, pyqtSignal


class MaestroRunner(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, yaml_path):
        super().__init__()
        self.yaml_path = yaml_path

    def run(self):
        process = subprocess.Popen(
            ["maestro", "test", self.yaml_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in process.stdout:
            self.log.emit(line.rstrip())

        process.wait()
        self.finished.emit(process.returncode)
