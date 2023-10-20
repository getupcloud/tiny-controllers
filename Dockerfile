#FROM summerwind/whitebox-controller:latest AS base
FROM caruccio/whitebox-controller:latest AS base

FROM python:3.10-alpine

ARG VERSION
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_COMMIT_ID
ARG COMPILE=true
ARG KUBECTL_VERSION

COPY --from=base /bin/whitebox-controller /bin/whitebox-controller
COPY app/requirements.txt /app/requirements.txt

RUN apk add jq curl bind-tools --no-cache && \
    \
    curl -LO https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
    mv kubectl /usr/bin/kubectl && \
    chmod +x /usr/bin/kubectl && \
    \
    find /app -name requirements.txt | xargs -P 1 -r -t pip install -r && \
    ( \
        echo "VERSION=\"$VERSION\""; \
        echo "BUILD_DATE=\"$BUILD_DATE\""; \
        echo "GIT_COMMIT=\"$GIT_COMMIT\""; \
        echo "GIT_COMMIT_ID=\"$GIT_COMMIT_ID\""; \
    ) > /app/.version

WORKDIR /
USER nobody

COPY app /app
COPY config /config

ENTRYPOINT ["/app/entrypoint"]
