ifneq (,$(wildcard ./.env))
    include .env
    export
endif

ACCOUNT_ID=$(shell aws sts get-caller-identity --query Account --output text --profile ${AWS_PROFILE})
SAM_BUCKET=${ACCOUNT_ID}-sam-deploy-${AWS_REGION}
STACK_NAME=serverless-todo-demo


.PHONY: clean clean-all build setup deploy destroy outputs



clean:
	rm -rf backend/functions/user/jwt
	rm -rf backend/functions/user/PyJWT*

clean-all: destroy clean
	aws s3 rb s3://$(SAM_BUCKET) --profile ${AWS_PROFILE} --force

build:
	pip3 install -r backend/functions/user/requirements.txt -t backend/functions/user/

setup:
	aws s3 mb s3://$(SAM_BUCKET) --profile ${AWS_PROFILE}

deploy: build setup
	aws cloudformation package --template-file template.yaml --s3-bucket ${SAM_BUCKET} --s3-prefix ${STACK_NAME} --output-template-file template.packaged.yaml --profile ${AWS_PROFILE}
	aws cloudformation deploy --template-file template.packaged.yaml --stack-name ${STACK_NAME} --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset --profile ${AWS_PROFILE}

destroy:
	aws cloudformation delete-stack --stack-name ${STACK_NAME}

outputs:
	aws cloudformation describe-stacks --stack-name $(STACK_NAME) | jq '.Stacks[0]["Outputs"]'
