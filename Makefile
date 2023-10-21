VERSION := v0.2.1
REPOSITORY := getupcloud
IMAGE_NAME := tiny-controllers
GIT_COMMIT := $(shell git log -n1 --oneline)
GIT_COMMIT_ID := $(shell git log -n 1 --pretty=format:%h)
BUILD_DATE := $(shell LC_ALL=C date -u)
KUBECTL_VERSION := 1.25.0

all: docker-build-release help

help:
	@echo Available targets:
	@echo " " docker-build-release, docker-tag-latest
	@echo " " docker-push-release, docker-push-latest
	@echo " " git-tag-release, git-push-main, git-push-release
	@echo " " dev, dev-run, test

release: check-dirty docker-build-release docker-tag-latest git-tag-release git-push-main git-push-release docker-push-release docker-push-latest

check-dirty: DIFF_STATUS := $(shell git diff --stat)
check-dirty:
	@if [ -n "$(DIFF_STATUS)" ]; then \
	  echo "--> Refusing to build release on a dirty tree"; \
	  echo "--> Commit and try again."; \
	  exit 2; \
	fi

docker-build-release:
	docker build . -t $(REPOSITORY)/$(IMAGE_NAME):$(VERSION) \
        --build-arg VERSION="$(VERSION)" \
        --build-arg BUILD_DATE="$(BUILD_DATE)" \
        --build-arg GIT_COMMIT="$(GIT_COMMIT)" \
        --build-arg GIT_COMMIT_ID="$(GIT_COMMIT_ID)" \
        --build-arg KUBECTL_VERSION="$(KUBECTL_VERSION)"

docker-tag-latest:
	docker tag $(REPOSITORY)/$(IMAGE_NAME):$(VERSION) $(REPOSITORY)/$(IMAGE_NAME):latest

git-tag-release:
	git tag $(VERSION)

git-push-main:
	git push origin main

git-push-release:
	git push origin $(VERSION)

docker-push-release:
	docker push $(REPOSITORY)/$(IMAGE_NAME):$(VERSION)

docker-push-latest:
	docker push $(REPOSITORY)/$(IMAGE_NAME):latest

## LOCAL DEV

docker-build-dev:
	docker build . -t $(REPOSITORY)/$(IMAGE_NAME):$(VERSION) \
        --build-arg VERSION="dev" \
        --build-arg KUBECTL_VERSION="$(KUBECTL_VERSION)"

dev: VERSION := $(VERSION)-dev
dev: tls/tls.crt docker-build-dev dev-run

tls/tls.crt:
	mkdir -p tls
	[ -e tls/tls.crt -a -e tls/tls.key ] || openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -subj /CN=dev/ -keyout tls/tls.key -out tls/tls.crt
	chmod -R a+r tls

dev-run: VERSION := $(VERSION)-dev
dev-run: tls
	docker run -it --rm --name $(IMAGE_NAME)-$(VERSION) --network=host -u root -e KUBECONFIG=/.kube/config -v $(PWD)/dev-kubeconfig:/.kube/config -v $(PWD)/tls:/etc/tls/ $(REPOSITORY)/$(IMAGE_NAME):$(VERSION) $(RECONCILER)

test:
	make -C tests
