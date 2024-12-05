#!/usr/bin/env python

import subprocess
import argparse

import boto3

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="connect-ssh", epilog="SSH into EC2 instance")
    parser.add_argument(
        "--stack",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )

    args = parser.parse_args()
    stack_name = args.stack

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
        return

    instances = reservations[0]["Instances"]
    if len(instances) > 1:
        print("More than one instance found, aborting.")
        return

    public_ip = instances[0]["PublicIpAddress"]
    distribution = list(
        filter(lambda tag: tag["Key"] == "Distribution", instances[0]["Tags"])
    )[0]["Value"]
    print(distribution)
    print(f"Connecting to IP {public_ip}")

    if distribution == "Ubuntu":
        subprocess.run(["ssh", f"ubuntu@{public_ip}"])
    elif distribution == "Debian":
        subprocess.run(["ssh", f"admin@{public_ip}"])


if __name__ == "__main__":
    main()
