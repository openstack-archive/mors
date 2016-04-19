#! vim noexpandtab
# Copyright (C) 2016 Platform 9 Systems, Inc.

TOP_DIR := $(abspath ../)
SRC_DIR := $(TOP_DIR)
BUILD_DIR := $(TOP_DIR)/build

NPM := npm

APP_NAME :=pf9-mors
APP_DESC :="Platform9 mors (lease manager)"
APP_BUILD_DIR := $(BUILD_DIR)

PF9_VERSION ?=2.0.0
BUILD_NUMBER ?= 0
GIT_HASH := $(shell git rev-parse --short HEAD)
FULL_VERSION := $(PF9_VERSION)-$(BUILD_NUMBER)

APP_DESC :="Platform9 mors(lease manager) git hash $(GIT_HASH)"

APP_RPM_DIR := $(APP_BUILD_DIR)/rpmbuild
APP_RPM_STAGE_DIR := $(APP_BUILD_DIR)/stage
APP_RPM_VENV := $(APP_RPM_STAGE_DIR)/opt/pf9/$(APP_NAME)
APP_ARCHITECTURE := noarch
APP_RPM := $(APP_RPM_DIR)/$(APP_NAME)-$(FULL_VERSION).noarch.rpm
APP_SPEC_FILE := $(APP_BUILD_DIR)/$(APP_NAME)-rpm.spec

############################################################

${APP_RPM_DIR}:
	mkdir -p $@

${APP_RPM_STAGE_DIR}:
	mkdir -p $@

${APP_RPM_VENV}:
	mkdir -p $@
	virtualenv $@
	$@/bin/pip install ${SRC_DIR}

stage: $(APP_RPM_DIR) $(APP_RPM_STAGE_DIR) $(APP_RPM_VENV)
	cp -r $(SRC_DIR)/etc/ $(APP_RPM_STAGE_DIR)/
	cp $(SRC_DIR)/mors_repo/migrate.cfg $(APP_RPM_VENV)/lib/python2.7/site-packages/mors_repo/

${APP_RPM}: stage
	echo "RPM build "
	fpm -t rpm \
		-s dir \
		-n $(APP_NAME) \
		--description $(APP_DESC) \
		--version $(PF9_VERSION) \
		--iteration $(BUILD_NUMBER) \
		--provides $(APP_NAME) \
		--license "Commercial" \
		--architecture $(APP_ARCHITECTURE) \
		--url "http://www.platform9.net" \
		--vendor Platform9 \
		-p $@ \
		-C $(APP_RPM_STAGE_DIR) . && \
	$(SRC_DIR)/support/sign_packages.sh ${APP_RPM}

clean:
	rm -rf $(BUILD_DIR)

all: clean $(APP_RPM)
