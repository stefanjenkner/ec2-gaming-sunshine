#!/usr/bin/env python

import argparse
import sys

import boto3

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="stop", epilog="Stop EC2 instance")
    parser.add_argument(
        "--stack-name",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    args = parser.parse_args()
    stack_name = args.stack_name

    ec2_client = boto3.client("ec2")
    instances = get_instances(ec2_client, stack_name)
    if len(instances) == 0:
        print("No running instances found, aborting.")
        return 1
    elif len(instances) > 1:
        print("More than one instance found, aborting.")
        return 1

    for instance in instances:
        instance_id = instance["InstanceId"]
        ec2_instance = ec2_client.Instance(instance_id)
        print(f"Stopping {instance_id}")
        response = ec2_instance.stop()
        print(response)


def get_instances(ec2_client, stack_name: str):
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [f"{stack_name}-instance"]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
        ]
    )
    reservations = response["Reservations"]
    return reservations[0]["Instances"] if len(reservations) > 0 else []


if __name__ == "__main__":
    sys.exit(main())
