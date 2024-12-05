#!/usr/bin/env python

import argparse
import base64
import logging
import sys

import boto3
import botocore
from jinja2 import Template

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"
DEFAULT_KEYPAIR = "ec2-gaming"
INITIAL_WHITELISTED_IP = "127.0.0.1/32"


def main():
    parser = argparse.ArgumentParser(prog="deploy", epilog="Create or update stack")
    parser.add_argument(
        "--print-only", help="Print CF template but do not deploy", action="store_true"
    )
    parser.add_argument(
        "--keypair",
        help=f"Name of EC2 keypair to use, defaults to '{DEFAULT_KEYPAIR}'",
        default=DEFAULT_KEYPAIR,
    )
    parser.add_argument(
        "--stack",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )

    args = parser.parse_args()

    with open("cloudformation/ec2-gaming-sunshine.yaml") as cf_:
        template = Template(cf_.read())

    cloud_config = {}
    for flavour in ["jammy", "bookworm"]:
        with open(f"cloud-init/cloud-config-{flavour}.yaml", "rb") as cloud_config_:
            cloud_config_b64_ = base64.b64encode(cloud_config_.read())
            cloud_config[flavour] = cloud_config_b64_.decode("ascii")

    if args.print_only:
        print(template.render(cloud_config=cloud_config))
        return 0

    logging.basicConfig(level=logging.INFO)

    client = boto3.client("cloudformation")

    stack_name = args.stack
    stack_exists = False
    try:
        response = client.describe_stacks(StackName=stack_name)
        stack_exists = True
        stack_status = response["Stacks"][0]["StackStatus"]
        logging.info(f"Found stack {stack_name} with status {stack_status}")
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            logging.info(f"Stack {stack_name} does not exist yet")
            return 1
        else:
            raise error

    if stack_exists:
        logging.info(f"Updating stack {stack_name}")

        try:
            response = client.update_stack(
                StackName=stack_name,
                TemplateBody=template.render(cloud_config=cloud_config),
                Parameters=[
                    {"ParameterKey": "MyIp", "UsePreviousValue": True},
                    {"ParameterKey": "KeyPair", "UsePreviousValue": True},
                ],
                Capabilities=["CAPABILITY_NAMED_IAM"],
            )

        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ValidationError":
                logging.error(error.response["Error"]["Message"])
                return 1
            else:
                raise error

    else:
        logging.info(f"Creating stack {stack_name}")
        response = client.create_stack(
            StackName=stack_name,
            TemplateBody=template.render(cloud_config=cloud_config),
            Parameters=[
                {"ParameterKey": "MyIp", "ParameterValue": INITIAL_WHITELISTED_IP},
                {"ParameterKey": "KeyPair", "ParameterValue": args.keypair},
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )


if __name__ == "__main__":
    sys.exit(main())
