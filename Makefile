
ifndef APIKEY
    APIKEY=APIKEYFORTESTxAPIKEYFORTESTxAPIKEYFORTESTx
endif

default:
	@echo build threadfix from source
	@echo test threadfix rest api

build:
	./build.sh
.PHONY: build

test:
	python test_threadfix.py $(APIKEY)
.PHONY: test



