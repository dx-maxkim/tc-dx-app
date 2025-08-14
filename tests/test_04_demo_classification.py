import subprocess
import pytest
import yaml
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib

def load_config():
    """config.yaml 파일을 읽어와 설정을 반환합니다."""
    config_path = pathlib.Path('configs/config_04.yaml')
    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}'를 찾을 수 없습니다.")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['classification_test']

def test_classification_from_config(app_base_path):
    """
    config_04.yaml 파일에 정의된 classificaiton 을 실행하고 결과를 검증합니다.
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    config = load_config()
    command_str = config.get('command')
    expected_output = config.get('expected_output')

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not expected_output:
        pytest.fail("config_04.yaml 파일에 'command' 또는 'expected_output' 키가 없습니다.")

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

    # 예외 처리를 포함하여 명령어를 실행합니다.
    try:
        result = subprocess.run(
            command_parts,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        output = result.stdout

    except FileNotFoundError:
        pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command_list[0]}'. 경로를 확인해주세요.")
    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"스크립트 실행에 실패했습니다 (종료 코드: {e.returncode}).\n"
            f"명령어: {command_str}\n"
            f"에러 로그: {e.stderr}"
        )
    except subprocess.TimeoutExpired:
        pytest.fail("스크립트 실행 시간이 초과되었습니다.")

    # 표준 출력(output)에 기대하는 문자열(expected_output)이 포함되어 있는지 확인합니다.
    assert expected_output in output, \
        f"기대 결과('{expected_output}')가 출력에 없습니다.\n전체 출력:\n{output}"
