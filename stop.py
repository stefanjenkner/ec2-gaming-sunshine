#!/usr/bin/env python

import argparse
import sys

import boto3

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="stop", epilog="Stop EC2 instance")
    parser.add_argument(
        "--stack",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    args = parser.parse_args()
    stack_name = args.stack

    client = boto3.client("ec2")
    ec2 = boto3.resource("ec2")
    response = client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [f"{stack_name}-instance"]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
        ]
    )
    reservations = response["Reservations"]

    if len(reservations) == 0:
        print("No running instances found, aborting.")
        return 1

    instances = reservations[0]["Instances"]
    for instance in instances:
        instance_id = instance["InstanceId"]
        ec2_instance = ec2.Instance(instance_id)
        print(f"Stopping {instance_id}")
        response = ec2_instance.stop()
        print(response)


if __name__ == "__main__":
    sys.exit(main())
