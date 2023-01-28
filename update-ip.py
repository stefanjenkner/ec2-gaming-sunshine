#!/usr/bin/env python

import base64
import logging
import urllib.request
import urllib.parse

import botocore
import boto3

from jinja2 import Template

STACK_NAME = "jammy-sunshine"


def main():

    logging.basicConfig(level=logging.INFO)

    client = boto3.client("cloudformation")

    logging.info(f"Updating stack {STACK_NAME}")

    try:
        ip = get_ip()
        ip_cidr = f"{ip}/32"
        response = client.update_stack(
            StackName=STACK_NAME,
            UsePreviousTemplate=True,
            Parameters=[
                {"ParameterKey": "MyIp", "ParameterValue": ip_cidr},
                {"ParameterKey": "KeyPair", "UsePreviousValue": True},
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )

    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            logging.error(error.response["Error"]["Message"])
        else:
            raise error


def get_ip():

    f = urllib.request.urlopen("http://ifconfig.me/ip")
    return f.read().decode("utf-8")


if __name__ == "__main__":
    main()
