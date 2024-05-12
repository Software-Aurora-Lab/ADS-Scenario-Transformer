import time
import docker
import subprocess
from src.config import ADS_ROOT, MY_SCRIPTS_DIR, DOCKER_CONTAINER_NAME, CONTAINER_NUM, DEFAULT_SCRIPT_PORT, PROJECT_ROOT, \
    DIR_ROOT, DOCKER_IMAGE_ID
from prepare import init_prepare


class Container:
    ads_root: str
    ctn_id: str
    ctn_name: str
    script_port: int
    env_file: str

    is_already_setup: bool

    def __init__(self, ads_root: str, ctn_name: str, ctn_id: str, script_port) -> None:
        self.ads_root = ads_root
        self.ctn_id = ctn_id
        self.ctn_name = ctn_name
        self.script_port = script_port
        self.env_file = "dev.env"

        self.is_already_setup = False

    @property
    def container_name(self) -> str:
        """
        Gets the name of the container

        Returns:
            name: str
                name of the container
        """
        return self.ctn_name

    def is_running(self) -> bool:
        """
        Checks if the container is running

        Returns:
            status: bool
                True if running, False otherwise
        """
        try:
            if docker.from_env().containers.get(self.container_name).status == 'running':
                self.is_already_setup = True
                return True
        except:
            return False

    def kill_process(self):
        cmd = f"docker exec {self.container_name} /bin/bash {MY_SCRIPTS_DIR}/kill_process.sh"
        subprocess.run(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def scenario_script_update(self, scenario):
        script_path = f"{MY_SCRIPTS_DIR}/run_scenario_{self.ctn_id}.sh"

        with open(f"{script_path}", "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"cd {ADS_ROOT}\n")
            f.write(f"source install/setup.bash\n")
            f.write(f"ros2 launch scenario_test_runner scenario_test_runner.launch.py \\\n")
            f.write(f"  architecture_type:=awf/universe \\\n")
            f.write(f"  record:=true \\\n")
            f.write(f"  port:={str(self.script_port)} \\\n")
            f.write(f"  scenario:={scenario.initial_scenario_record_path} \\\n")
            f.write(f"  sensor_model:=sample_sensor_kit \\\n")
            f.write(f"  vehicle_model:=sample_vehicle")
        return script_path

    def start_instance(self, restart=False):
        """
        Starts an Apollo instance

        Parameters:
            restart : bool
                forcing container to restart
        """
        if not restart and self.is_running():
            return

        cmd = f'docker network create --driver bridge c{self.ctn_id}'
        subprocess.run(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        cmd = f'docker run -itd --gpus all --privileged --name {self.ctn_name} --network c{self.ctn_id} -v {ADS_ROOT}:{ADS_ROOT} -v {DIR_ROOT}/autoware_map:{DIR_ROOT}/autoware_map -v {PROJECT_ROOT}:{PROJECT_ROOT} -e DISPLAY -e TERM -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix -v /etc/localtime:/etc/localtime:ro {DOCKER_IMAGE_ID}'
        subprocess.run(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def move_bashrc(self):
        cmd = f"docker exec {self.container_name} /bin/bash {ADS_ROOT}/scripts/move_bashrc.sh"
        subprocess.run(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def env_init(self):
        self.kill_process()
        self.move_bashrc()

    def stop_recorder(self):
        cmd = f"docker exec {self.container_name} /bin/bash {MY_SCRIPTS_DIR}/stop_recorder.sh"
        subprocess.run(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def setup_env(self):
        if self.is_already_setup:
            print(f"Container {self.ctn_name} already setup.")
            return
        cmd = f"docker exec --env-file {MY_SCRIPTS_DIR}/{self.env_file} {self.container_name} /bin/bash {MY_SCRIPTS_DIR}/setup_env.sh"
        subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Container {self.ctn_name} setup complete.")

    def replay_example(self):
        cmd = f"docker exec --env-file {MY_SCRIPTS_DIR}/{self.env_file} {self.container_name} /bin/bash {MY_SCRIPTS_DIR}/run_scenario.sh"
        subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    init_prepare()

    # x = 1
    # ctn = Container(ADS_ROOT, f'{DOCKER_CONTAINER_NAME}_{x}', str(x), DEFAULT_SCRIPT_PORT + x)
    # ctn.start_instance()
    # ctn.env_init()
    # ctn.setup_env()
    # ctn.replay_example()

    x = 5
    containers = [Container(ADS_ROOT, f'{DOCKER_CONTAINER_NAME}_{x}', str(x), DEFAULT_SCRIPT_PORT + x) for x in
                  range(CONTAINER_NUM)]

    for ctn in containers:
        ctn.start_instance()
        ctn.env_init()
        ctn.setup_env()

    print("Replaying examples")
    for ctn in containers:
        ctn.replay_example()

    time.sleep(60)
