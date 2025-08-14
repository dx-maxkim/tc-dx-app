import yaml         # PyYAML 라이브러리
import pathlib
import pytest

# --- 설정 로드 함수 ---
def load_config():
    """config.yaml 파일을 읽어와 설정을 반환합니다."""
    config_path = pathlib.Path('configs/config_02.yaml')
    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}'를 찾을 수 없습니다.")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['application_setup']

# --- 테스트 코드 ---
# 테스트 함수가 실행되기 전에 설정 파일을 미리 읽어옵니다.
CONFIG = load_config()
APP_DIR = pathlib.Path(CONFIG['directory'])
EXPECTED_FILES = set(CONFIG['expected_files']) # 리스트를 집합(set)으로 변환


def test_directory_contains_exact_files_from_config():
    """
    'config_02.yaml'에 명시된 폴더에 정확히 지정된 파일들만 있는지 확인합니다.
    """
    # 1. 테스트할 폴더가 존재하는지 확인합니다.
    if not APP_DIR.is_dir():
        pytest.fail(f"테스트 대상 폴더 '{APP_DIR}'가 존재하지 않습니다.")

    # 2. 폴더 안의 실제 파일 목록을 집합(set)으로 가져옵니다.
    actual_files = {f.name for f in APP_DIR.glob('*') if f.is_file()}

    # 3. YAML에서 로드한 기대 파일 목록과 실제 파일 목록이 정확히 일치하는지 검증합니다.
    assert actual_files == EXPECTED_FILES, (
        "폴더의 내용이 설정 파일(config.yaml)과 다릅니다.\n"
        f"  - 누락된 파일: {sorted(list(EXPECTED_FILES - actual_files))}\n"
        f"  - 불필요한 파일: {sorted(list(actual_files - EXPECTED_FILES))}"
    )
