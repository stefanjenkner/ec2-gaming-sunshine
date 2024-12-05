#!/usr/bin/env python

import argparse
import subprocess
import sys
from sys import platform

import boto3

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"
DEFAULT_APP = "Low Res Desktop"

if platform == "linux" or platform == "linux2":
    MOONLIGHT_QT = "moonlight-qt"
elif platform == "darwin":
    MOONLIGHT_QT = "/Applications/Moonlight.app/Contents/MacOS/Moonlight"


def main():
    parser = argparse.ArgumentParser(prog="connect", epilog="Start streaming")
    parser.add_argument(
        "--stack",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    parser.add_argument(
        "--app", help=f"App to stream, defaults to '{DEFAULT_APP}'", default=DEFAULT_APP
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
        return 1

    instances = reservations[0]["Instances"]
    if len(instances) > 1:
        print("More than one instance found, aborting.")
        return 1

    public_ip = instances[0]["PublicIpAddress"]
    print(f"Connecting to IP {public_ip}")

    if not is_ready(public_ip, args.app):
        subprocess.run([MOONLIGHT_QT, "pair", "--pin", "0000", public_ip])

    subprocess.run([MOONLIGHT_QT, "stream", public_ip, args.app])


def is_ready(public_ip, app):
    process = subprocess.Popen(
        f"{MOONLIGHT_QT} list {public_ip}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = process.stdout.readlines()
    print(output)
    retval = process.wait()
    print(retval)
    return retval == 0 and b"{app}\n" in output


if __name__ == "__main__":
    sys.exit(main())
