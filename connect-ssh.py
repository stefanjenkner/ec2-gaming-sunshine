#!/usr/bin/env python

import argparse
import subprocess
import sys

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

    args = parser.parse_args()
    stack_name = args.stack_name

    client = boto3.client("ec2")
    boto3.resource("ec2")
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
    if len(instances) > 1:
        print("More than one instance found, aborting.")
        return 1

    public_ip = instances[0]["PublicIpAddress"]
    tags = instances[0]["Tags"]
    dist = list(filter(lambda tag: tag["Key"] == "Distribution", tags))[0]["Value"]
    print(f"Connecting to EC2 instance ({dist}) IP {public_ip}")

    subprocess_args = ["ssh"]
    if args.forward_web:
        subprocess_args.append("-L47990:localhost:47990")
    if dist == "Ubuntu":
        subprocess_args.append(f"ubuntu@{public_ip}")
    elif dist == "Debian":
        subprocess_args.append(f"admin@{public_ip}")
    else:
        subprocess_args.append(public_ip)
    subprocess.run(subprocess_args)


if __name__ == "__main__":
    sys.exit(main())
