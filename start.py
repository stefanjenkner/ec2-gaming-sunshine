#!/usr/bin/env python

import argparse
from sys import exit

import boto3

from helper.ec2_helper import get_one_instance

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="start", epilog="Start EC2 instance")
    parser.add_argument(
        "--stack-name",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    parser.add_argument(
        "instance_id",
        nargs="?",
        help="ID of the EC2 instance to start, optional if only one stopped instance exists",
    )
    args = parser.parse_args()

    try:
        args = parser.parse_args()
        instance = get_one_instance(args.stack_name, args.instance_id, ["stopped"])
        instance_id = instance["InstanceId"]
        start_instance(instance_id)
    except Exception as e:
        print(e)
        exit(1)


def start_instance(instance_id: str):
    ec2 = boto3.resource("ec2")
    ec2_instance = ec2.Instance(instance_id)
    print(f"Starting {instance_id}")
    response = ec2_instance.start()
    print(response)


if __name__ == "__main__":
    main()
