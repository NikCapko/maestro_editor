import subprocess


class MaestroRunner:
    def run(self, test_path, callback):
        process = subprocess.Popen(
            ["maestro", "test", test_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in process.stdout:
            callback(line)
