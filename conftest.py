import pytest
from pytest_html import extras

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
