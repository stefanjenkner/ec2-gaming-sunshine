#!/usr/bin/env python

import argparse
from sys import exit

import boto3

from helper.ec2_helper import get_one_instance

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="stop", epilog="Stop EC2 instance")
    parser.add_argument(
        "--stack-name",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    parser.add_argument(
        "instance_id",
        nargs="?",
        help="ID of the EC2 instance to stop, optional if only one running instance",
    )
    args = parser.parse_args()

    try:
        instance = get_one_instance(
            args.stack_name, args.instance_id, ["running", "pending"]
        )
        instance_id = instance["InstanceId"]
        stop_instance(instance_id)
    except Exception as e:
        print(e)
        exit(1)


def stop_instance(instance_id: str):
    ec2 = boto3.resource("ec2")
    ec2_instance = ec2.Instance(instance_id)
    print(f"Stopping {instance_id}")
    response = ec2_instance.stop()
    print(response)


if __name__ == "__main__":
    main()
