import os.path
from typing import List, Union
from voyager.types import ResetOptionsPython, PythonEvent
import requests
import gymnasium as gym
import voyager.utils as U
from .process_monitor import SubprocessMonitor


class VoyagerEnvPython(gym.Env):
    def __init__(
        self,
        server_host="http://localhost",
        server_port=3001,
        request_timeout=600,
        log_path="./logs",
    ):
        self.server = f"{server_host}:{server_port}"
        self.server_port = server_port
        self.request_timeout = request_timeout
        self.log_path = log_path
        self.has_reset = False
        self.reset_options: Union[ResetOptionsPython, None] = None
        self.connected = False
        # self.browser_instance = self.run(server_port)

    def run(self, server_port):
        U.f_mkdir(self.log_path, "python")
        file_path = os.path.abspath(os.path.dirname(__file__))
        monitor = SubprocessMonitor(
            commands=[
                "python",
                U.f_join(file_path, "python/main.py"),
                # TODO
                # str(server_port),
            ],
            name="python",
            log_path=U.f_join(self.log_path, "python"),
        )
        monitor.run()
        return monitor

    def check_process(self):
        if self.browser_instance and not self.browser_instance.is_running:
            raise RuntimeError("Python server process has been terminated")

    def step(
        self,
        code: str = "",
        programs: str = "",
    ) -> List[PythonEvent]:
        if not self.has_reset:
            raise RuntimeError("Environment has not been reset yet")
        # self.check_process()
        data = {
            "code": code,
            "programs": programs,
        }
        res = requests.post(
            f"{self.server}/execute", json=data, timeout=self.request_timeout
        )
        if res.status_code != 200:
            raise RuntimeError("Failed to execute Python code")
        returned_data = res.json()
        return returned_data["events"]

    def render(self):
        raise NotImplementedError("render is not implemented")

    def reset(
        self,
        *,
        options: ResetOptionsPython = {
            "currentDir": "",
            "workspace": [],
            "output": ""
        },
    ):

        self.reset_options = options
        self.has_reset = True
        self.connected = True

    def close(self):
        # if self.browser_instance:
        #     self.browser_instance.stop()
        return not self.connected
