#!/usr/bin/env python

import argparse
import sys
from typing import List

import boto3

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
    stack_name = args.stack_name

    instances = get_instances(stack_name)
    instance_ids = [instance["InstanceId"] for instance in instances]
    if len(instances) == 0:
        print("No stopped instances found, aborting.")
        return 1
    elif len(instances) > 1 and args.instance_id is None:
        print(f"More than one instance found: {instance_ids}, aborting.")
        return 1
    elif args.instance_id is not None and args.instance_id not in instance_ids:
        print("Specified instance not found, aborting.")
        return 1

    instance_id = args.instance_id or instances[0]["InstanceId"]
    start_instance(instance_id)


def start_instance(instance_id: str):
    ec2 = boto3.resource("ec2")
    ec2_instance = ec2.Instance(instance_id)
    print(f"Starting {instance_id}")
    response = ec2_instance.start()
    print(response)


def get_instances(stack_name: str) -> List[dict]:
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [f"{stack_name}-instance"]},
            {"Name": "instance-state-name", "Values": ["stopped"]},
        ]
    )
    return [
        instance
        for reservation in response["Reservations"]
        for instance in reservation["Instances"]
    ]


if __name__ == "__main__":
    sys.exit(main())
