# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION} as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

#  FIX 1: Install Tesseract OCR binaries before switching down privileges
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

#  FIX 2: Copy the code and explicitly give write ownership permissions to appuser
COPY --chown=appuser:appuser . .

# Now it is completely safe to drop permissions without locking the app out of the DB directory
USER appuser

EXPOSE 4001

CMD ["python3", "app.py"]
