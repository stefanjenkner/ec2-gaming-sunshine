#!/usr/bin/env python

import argparse
import base64
import logging
import sys

import boto3
import botocore
from botocore.exceptions import ClientError
from jinja2 import Template

DEFAULT_KEYPAIR = "ec2-gaming"
DEFAULT_REGION = "eu-central-1"
DEFAULT_STACK_NAME = "ec2-gaming-sunshine"
INITIAL_WHITELISTED_IP = "127.0.0.1/32"


def main():
    parser = argparse.ArgumentParser(prog="deploy", epilog="Create or update stack")
    parser.add_argument(
        "--print-only", help="Print CF templates but do not deploy", action="store_true"
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
    parser.add_argument(
        "--region",
        help=f"Name of AWS Region, defaults to '{DEFAULT_REGION}'",
        default=DEFAULT_REGION,
    )

    args = parser.parse_args()

    stack_name = args.stack
    region_name = args.region
    bucket_name = f"{stack_name}-cfn"

    cloud_config = {}
    for flavour in ["jammy", "bookworm", "noble"]:
        with open(f"cloud-init/cloud-config-{flavour}.yaml", "rb") as cloud_config_:
            cloud_config_b64_ = base64.b64encode(cloud_config_.read())
            cloud_config[flavour] = cloud_config_b64_.decode("ascii")

    with open("cloudformation/ec2-gaming-sunshine.yaml") as cf_:
        template = Template(cf_.read())

    if args.print_only:
        print(template.render(cloud_config=cloud_config, bucket_name=bucket_name))
        for flavour in ["jammy", "bookworm", "noble"]:
            file_name = f"launch-templates-{flavour}.yaml"
            print("\n---")
            with open(f"cloudformation/{file_name}") as cf_:
                nested_stack_template = Template(cf_.read())
                print(
                    nested_stack_template.render(
                        cloud_config=cloud_config, bucket_name=bucket_name
                    )
                )
        return 0

    logging.basicConfig(level=logging.INFO)

    s3_client = boto3.client("s3", region_name=region_name)
    try:
        location = {"LocationConstraint": region_name}
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print(f"Bucket '{bucket_name}' created successfully")
    except ClientError as e:
        if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            print(f"Bucket '{bucket_name}' already exists")
        else:
            print(f"An error occurred while creating the bucket: {e}")
            return 1

    for flavour in ["jammy", "bookworm", "noble"]:
        file_name = f"launch-templates-{flavour}.yaml"
        try:
            content = ""
            with open(f"cloudformation/{file_name}") as cf_:
                sub_stack_template = Template(cf_.read())
                content = sub_stack_template.render(
                    cloud_config=cloud_config, bucket_name=bucket_name
                )
            s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=content)
            print(f"File '{file_name}' uploaded successfully")
        except ClientError as e:
            print(f"An error occurred while uploading the file: {e}")
            return 1

    client = boto3.client("cloudformation")

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
                TemplateBody=template.render(
                    cloud_config=cloud_config, bucket_name=bucket_name
                ),
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
            TemplateBody=template.render(
                cloud_config=cloud_config, bucket_name=bucket_name
            ),
            Parameters=[
                {"ParameterKey": "MyIp", "ParameterValue": INITIAL_WHITELISTED_IP},
                {"ParameterKey": "KeyPair", "ParameterValue": args.keypair},
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )


if __name__ == "__main__":
    sys.exit(main())
