FROM python:3.12-alpine

ARG VERSION
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_COMMIT_ID
ARG COMPILE=true
ARG KUBECTL_VERSION

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN apk add jq curl --no-cache && \
    find /app -name requirements.txt | xargs -P 1 -r -t pip install -r && \
    ( \
        echo "VERSION=\"$VERSION\""; \
        echo "BUILD_DATE=\"$BUILD_DATE\""; \
        echo "GIT_COMMIT=\"$GIT_COMMIT\""; \
        echo "GIT_COMMIT_ID=\"$GIT_COMMIT_ID\""; \
    ) > /app/.version

USER nobody
COPY . /app

ENTRYPOINT ["python", "/app/metrics.py"]
