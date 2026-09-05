FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

# The runtime image expects a separate requirements manifest.
COPY requirements.txt ./

RUN python -m pip install --no-cache-dir .

CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
