#!/usr/bin/env python

import argparse
import sys

import boto3

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="start", epilog="Start EC2 instance")
    parser.add_argument(
        "--stack-name",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    args = parser.parse_args()
    stack_name = args.stack_name

    client = boto3.client("ec2")
    ec2 = boto3.resource("ec2")
    response = client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [f"{stack_name}-instance"]},
            {"Name": "instance-state-name", "Values": ["stopped"]},
        ]
    )

    reservations = response["Reservations"]
    if len(reservations) == 0:
        print("No stopped instances found, aborting.")
        return 1

    instances = reservations[0]["Instances"]
    if len(instances) > 1:
        print("More than one instance found, aborting.")
        return 1

    instance_id = instances[0]["InstanceId"]
    ec2_instance = ec2.Instance(instance_id)
    print(f"Starting {instance_id}")
    response = ec2_instance.start()
    print(response)


if __name__ == "__main__":
    sys.exit(main())
