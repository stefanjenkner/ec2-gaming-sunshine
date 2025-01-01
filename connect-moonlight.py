#!/usr/bin/env python

import argparse
import subprocess
from random import randint
from sys import exit, platform
from time import sleep
from typing import List

import boto3

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"
DEFAULT_APP = "Desktop"

if platform == "linux" or platform == "linux2":
    MOONLIGHT_QT = "moonlight-qt"
elif platform == "darwin":
    MOONLIGHT_QT = "/Applications/Moonlight.app/Contents/MacOS/Moonlight"


def main():
    parser = argparse.ArgumentParser(prog="connect-moonlight", epilog="Start streaming")
    parser.add_argument(
        "--stack-name",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )
    parser.add_argument(
        "--app", help=f"App to stream, defaults to '{DEFAULT_APP}'", default=DEFAULT_APP
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
    connect_moonlight(instance_id, public_ip, args.app)


def connect_moonlight(instance_id: str, public_ip: str, app: str):
    print(f"Connecting to EC2 instance {instance_id} using IP {public_ip}")
    if not is_ready(public_ip, app):
        pair(public_ip, instance_id)
    subprocess.run([MOONLIGHT_QT, "stream", public_ip, app])


def pair(public_ip: str, instance_id: str):
    pin = f"{randint(0, 9999):04}"
    command = f"https --ignore-stdin --verify=no -a sunshine:sunshine :47990/api/pin pin={pin}"
    moonlight = subprocess.Popen([MOONLIGHT_QT, "pair", "--pin", pin, public_ip])
    sleep(3)
    run_ssm_command(instance_id, command)
    moonlight.wait()


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


def run_ssm_command(instance_id: str, command: str):
    ssm_client = boto3.client("ssm")
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": [command]},
    )
    command_id = response["Command"]["CommandId"]
    while True:
        sleep(1)
        output = ssm_client.get_command_invocation(
            CommandId=command_id, InstanceId=instance_id
        )
        if output["Status"] in ["Success", "Failed", "Cancelled"]:
            break
    print(output["StandardOutputContent"])


def is_ready(public_ip: str, app: str):
    process = subprocess.Popen(
        f"{MOONLIGHT_QT} list {public_ip}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = process.stdout.readlines()
    print(output)
    retval = process.wait()
    return retval == 0 and bytes(f"{app}\n", "utf-8") in output


if __name__ == "__main__":
    exit(main())
