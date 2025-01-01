#!/usr/bin/env python

import argparse
import subprocess
import sys
from typing import List

import boto3

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="connect-ssh", epilog="SSH into EC2 instance")
    parser.add_argument(
        "--stack-name",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    parser.add_argument(
        "--forward-web",
        help="Forward Sunshine Webinterface to https://localhost:47990/",
        action="store_true",
    )
    parser.add_argument(
        "instance_id",
        nargs="?",
        help="ID of the EC2 instance to connect to, optional if only one running instance",
    )

    args = parser.parse_args()
    stack_name = args.stack_name

    instances = get_instances(stack_name)
    instance_ids = [instance["InstanceId"] for instance in instances]
    if len(instances) == 0:
        print("No running instances found, aborting.")
        return 1
    elif len(instances) > 1 and args.instance_id is None:
        print(f"More than one instance found: {instance_ids}, aborting.")
        return 1
    elif args.instance_id is not None and args.instance_id not in instance_ids:
        print("Specified instance not found, aborting.")
        return 1

    instance_id = args.instance_id or instances[0]["InstanceId"]
    instance = next(filter(lambda i: i["InstanceId"] == instance_id, instances))
    public_ip = instance["PublicIpAddress"]
    tags = instance["Tags"]
    dist = list(filter(lambda tag: tag["Key"] == "Distribution", tags))[0]["Value"]
    connect_ssh(instance_id, public_ip, dist, args.forward_web)


def connect_ssh(instance_id: str, public_ip: str, dist: str, forward_web: bool):
    print(f"Connecting to EC2 instance {instance_id} ({dist}) using IP {public_ip}")
    subprocess_args = ["ssh"]
    if forward_web:
        subprocess_args.append("-L47990:localhost:47990")
        print("Forwarding Sunshine web-interface to: https://localhost:47990")
    if dist == "Ubuntu":
        subprocess_args.append(f"ubuntu@{public_ip}")
    elif dist == "Debian":
        subprocess_args.append(f"admin@{public_ip}")
    else:
        subprocess_args.append(public_ip)
    subprocess.run(subprocess_args)


def get_instances(stack_name: str) -> List[dict]:
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [f"{stack_name}-instance"]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
        ]
    )
    return [
        instance
        for reservation in response["Reservations"]
        for instance in reservation["Instances"]
    ]


if __name__ == "__main__":
    sys.exit(main())
