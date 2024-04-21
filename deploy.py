#!/usr/bin/env python

import base64
import logging
import argparse

import botocore
import boto3

from jinja2 import Template

STACK_NAME = "jammy-sunshine"
DEFAULT_KEYPAIR = "ec2-gaming"
INITIAL_WHITELISTED_IP = "127.0.0.1/32"


def main():

    parser = argparse.ArgumentParser(prog="deploy", epilog="Create or update stack")
    parser.add_argument("--print-only", help="Print CF template but do not deploy", action="store_true")
    parser.add_argument("--keypair", help=f"Name of EC2 keypair to use, defaults to '{DEFAULT_KEYPAIR}'", default=DEFAULT_KEYPAIR)

    args = parser.parse_args()

    with open("cloudformation/jammy-sunshine.yaml") as cf_:
        template = Template(cf_.read())

    with open("cloud-init/cloud-config.yaml", "rb") as cloud_config_:
        cloud_config_b64_ = base64.b64encode(cloud_config_.read())
        cloud_config_b64_text_ = cloud_config_b64_.decode("ascii")

    if args.print_only:
        print(template.render(cloud_config=cloud_config_b64_text_))
        return

    logging.basicConfig(level=logging.INFO)

    client = boto3.client("cloudformation")

    stack_exists = False
    try:
        response = client.describe_stacks(StackName=STACK_NAME)
        stack_exists = True
        stack_status = response["Stacks"][0]["StackStatus"]
        logging.info(f"Found stack {STACK_NAME} with status {stack_status}")
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            logging.info(f"Stack {STACK_NAME} does not exist yet")
        else:
            raise error

    if stack_exists:

        logging.info(f"Updating stack {STACK_NAME}")

        try:
            response = client.update_stack(
                StackName=STACK_NAME,
                TemplateBody=template.render(cloud_config=cloud_config_b64_text_),
                Parameters=[
                    {"ParameterKey": "MyIp", "UsePreviousValue": True},
                    {"ParameterKey": "KeyPair", "UsePreviousValue": True},
                ],
                Capabilities=["CAPABILITY_NAMED_IAM"],
            )

        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ValidationError":
                logging.error(error.response["Error"]["Message"])
            else:
                raise error

    else:

        logging.info(f"Creating stack {STACK_NAME}")
        response = client.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template.render(cloud_config=cloud_config_b64_text_),
            Parameters=[
                {"ParameterKey": "MyIp", "ParameterValue": INITIAL_WHITELISTED_IP},
                {"ParameterKey": "KeyPair", "ParameterValue": args.keypair},
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )


if __name__ == "__main__":
    main()
