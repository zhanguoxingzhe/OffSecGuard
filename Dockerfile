FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir $(python -c "
import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(' '.join(d['project']['dependencies']))
")

# 复制源代码
COPY offsec_guard/ offsec_guard/
COPY cli.py .

ENTRYPOINT ["python", "cli.py"]
CMD ["run", "--help"]
