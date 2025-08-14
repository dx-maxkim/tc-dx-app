import pytest
import os
from pytest_html import extras

@pytest.fixture(scope="session")
def app_base_path():
    """애플리케이션의 기본 경로를 반환하는 Fixture"""
    # 환경 변수에서 경로를 가져오거나, 직접 지정할 수 있습니다.
    path = "/home/max/Works/dx-runtime/dx_app"
    if not os.path.isdir(path):
        pytest.fail(f"지정한 애플리케이션 경로를 찾을 수 없습니다: {path}")
    return path

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest-html 리포트의 'Extra' 섹션에 테스트 함수의 docstring을 추가합니다.
    """
    outcome = yield
    report = outcome.get_result()
    # 'report.extra'를 'report.extras'로 변경합니다.
    extras_list = getattr(report, "extras", [])
    if report.when == "call":
        docstring = item.obj.__doc__
        if docstring:
            extras_list.append(extras.html(f"<p>{docstring}</p>"))
        # 'report.extra'를 'report.extras'로 변경합니다.
        report.extras = extras_list
