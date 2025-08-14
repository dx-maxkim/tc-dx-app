# tc-dx-app
test scripts for DX APP


```
python3 -m venv venv-tc
source venv-tc/bin/activate
pip install -U pip
pip install -r requirements.txt
```

# 병렬 실행
#pytest -n auto --html=report.html --self-contained-html

# 단일 실행
pytest --html=report.html --self-contained-html
