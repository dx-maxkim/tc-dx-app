import subprocess
import pytest
import yaml
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib
import time
import signal

def load_config():
    """config.yaml 파일을 읽어와 설정을 반환합니다."""
    config_path = pathlib.Path('configs/config_05.yaml')
    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}'를 찾을 수 없습니다.")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['classification_test']

def test_imagenet_classification_from_config(app_base_path):
    """
    config_05.yaml 파일에 정의된 imagenet_classificaiton 을 실행하고 결과를 검증합니다.
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    config = load_config()
    command_str = config.get('command')
    timeout_sec = config.get('timeout_sec')

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not timeout_sec:
        pytest.fail("config_05.yaml 파일에 'command' 또는 'timeout_sec' 키가 없습니다.")

    command_parts = shlex.split(command_str)

    # ❗ 실행 파일 경로를 base_path와 조합하여 절대 경로로 만듭니다.
    executable_path = app_base_path + '/' + command_parts[0]
    command_parts[0] = executable_path

    # ❗ 모델(-m)과 이미지(-i) 경로도 절대 경로로 변경합니다.
    for i, part in enumerate(command_parts):
        if part == "-m" and i + 1 < len(command_parts):
            command_parts[i+1] = app_base_path + '/' + command_parts[i+1]
        elif part == "-i" and i + 1 < len(command_parts):
            command_parts[i+1] = app_base_path + '/' + command_parts[i+1]
        elif part == "-p" and i + 1 < len(command_parts):
            command_parts[i+1] = app_base_path + '/' + command_parts[i+1]

    process = None
    try:
        # 1. Popen으로 백그라운드에서 프로세스 시작
        print(f"\n프로세스 실행: {' '.join(command_parts)}")
        process = subprocess.Popen(command_parts)

        # 2. config 파일에 지정된 시간(초)만큼 대기
        print(f"{timeout_sec}초 동안 대기합니다...")
        time.sleep(timeout_sec)

        # 3. 대기 시간이 끝난 후, 프로세스에 종료 신호(SIGINT) 전송
        print(f"시간 초과. 프로세스(PID: {process.pid})에 종료 신호를 보냅니다.")
        process.send_signal(signal.SIGINT) # Ctrl+C와 동일한 신호

        # 4. 프로세스가 실제로 종료될 때까지 최대 10초 대기
        process.wait(timeout=10)
        print("프로세스가 정상적으로 종료되었습니다.")

    except FileNotFoundError:
        pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command_parts[0]}'. 경로를 확인해주세요.")
    except subprocess.TimeoutExpired:
        # wait(10) 시간 동안 종료되지 않은 경우
        print("프로세스가 종료 신호에 반응하지 않아 강제 종료합니다.")
        process.kill() # 강제 종료
        pytest.fail("프로세스가 정상적으로 종료되지 않았습니다.")
    except Exception as e:
        # 기타 예외 처리
        if process:
            process.kill()
        pytest.fail(f"테스트 실행 중 예기치 않은 오류 발생: {e}")

