import subprocess
import pytest
import yaml
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib

def load_config():
    """config.yaml 파일을 읽어와 설정을 반환합니다."""
    config_path = pathlib.Path('configs/config_06.yaml')
    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}'를 찾을 수 없습니다.")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['object_detection_test']

def get_test_ids(test_cases):
    """테스트 케이스의 'name'을 pytest ID로 사용합니다."""
    return [case['name'] for case in test_cases]

# @pytest.mark.parametrize 데코레이터 추가
@pytest.mark.parametrize(
    "test_case",                # 테스트 함수에 전달될 인자 이름
    load_config(),              # 인자에 주입될 데이터 (테스트 케이스 리스트)
    ids=get_test_ids(load_config()) # 각 테스트를 구별할 ID
)

def test_imagenet_classification_from_config(app_base_path, test_case):
    """
    config_06.yaml 파일에 정의된 yolo w/ image input 실행하고 결과를 검증합니다.
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    command_str = test_case.get('command')
    result_file = pathlib.Path(test_case.get('expected_result'))

    # 혹시 이전에 실패해서 파일이 남아있다면 미리 삭제하여 테스트 환경을 깨끗하게 합니다.
    if result_file.exists():
        result_file.unlink()

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not result_file:
        pytest.fail(f"설정 파일의 테스트 케이스 '{test_case.get('name')}'에 'command' 또는 'expected_result' 키가 없습니다.")

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

    print(f"'{result_file}' 파일의 존재를 확인합니다.")
    assert result_file.is_file(), f"PASS 조건 실패: '{result_file}' 파일이 생성되지 않았습니다."

    # 삭제하여 테스트 환경을 깨끗하게 합니다.
    if result_file.exists():
        output_dir = pathlib.Path("output")
        output_dir.mkdir(exist_ok=True)
        result_file.rename(f"output/{test_case.get('name')}_{test_case.get('expected_result')}")

