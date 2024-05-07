import docker
from datetime import datetime, timezone

class ContainerManager:
    ads_root: str

    def __init__(self, ads_root: str) -> None:
        self.client = docker.from_env()
        self.container = None
        self.ads_root = ads_root

    def is_running(self) -> bool:
        try:
            if docker.from_env().containers.get(
                    self.container_name).status == 'running':
                self.is_already_setup = True
                return True
        except:
            return False


    def execute_script_in_container(self, script_path):
        if self.container:
            exec_log = self.container.exec_run(f"/bin/bash {script_path}",
                                               tty=True)
            return exec_log.output.decode()
        else:
            return "Container is not running."

    def create_scenario_running_script(self, container_id: str,
                                       script_dir: str,
                                       scenario_file_path: str,
                                       log_dir_path: str):
        script_path = f"{script_dir}/run_scenario_{container_id}.sh"

        with open(f"{script_path}", "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"cd {self.ads_root}\n")
            f.write(f"source /autoware/install/setup.bash\n")
            f.write(
                f"ros2 launch scenario_test_runner scenario_test_runner.launch.py \\\n"
            )
            f.write(f"architecture_type:=awf/universe/20230906 \\\n")
            f.write(f"record:=false \\\n")
            f.write(f"scenario:={scenario_file_path} \\\n")
            f.write(f"output_directory:={log_dir_path} \\\n")
            f.write(f"sensor_model:=sample_sensor_kit \\\n")
            f.write(f"vehicle_model:=sample_vehicle")
        return script_path

    def start_instance(self, container_id: str, container_name: str,
                       map_path: str, scenario_path: str, script_path: str,
                       log_path: str, docker_image_id: str):
        print("Start instance")
        print("container name:", container_name)
        print("container id:", container_id)

        self.container = self.client.containers.run(
            docker_image_id,
            name=container_name,
            detach=True,  # Corresponds to '-d'
            tty=True,  # Corresponds to '-t'
            stdin_open=True,  # Corresponds to '-i'
            privileged=True,
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
            ],  # '--gpus all'
            environment={
                'DISPLAY': ':0',
                'TERM': '',
                'QT_X11_NO_MITSHM': '1'
            },
            volumes={
                '/tmp/.X11-unix': {
                    'bind': '/tmp/.X11-unix',
                    'mode': 'rw'
                },
                map_path: {
                    'bind': map_path,
                    'mode': 'rw'
                },
                scenario_path: {
                    'bind': scenario_path,
                    'mode': 'rw'
                },
                log_path: {
                    'bind': log_path,
                    'mode': 'rw'
                },
                script_path: {
                    'bind': script_path,
                    'mode': 'rw'
                },
                '/etc/localtime': {
                    'bind': '/etc/localtime',
                    'mode': 'ro'
                }
            })

    def remove_instance(self):
        print(f"Remove {self.container}")
        self.container.stop()
        self.container.remove()
        self.container = None

    def stop_container_if_timeout(self, timeout_sec: float):
        if not self.container:
            return

        result_dict = self.client.api.inspect_container(self.container.id)
        created_timestamp_str = result_dict["Created"]

        created_timestamp = datetime.fromisoformat(created_timestamp_str[:26])
        current_utc_time = datetime.utcnow()

        time_difference = current_utc_time - created_timestamp

        if timeout_sec <= time_difference.seconds:
            print(f"Stop Container since it is running for more than {timeout_sec} sec")
            self.remove_instance()