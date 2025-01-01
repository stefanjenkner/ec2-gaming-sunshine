#!/usr/bin/env python

import argparse
import subprocess
from sys import exit

from helper.ec2_helper import get_one_instance

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

    try:
        instance = get_one_instance(
            args.stack_name, args.instance_id, ["running", "pending"]
        )
        instance_id = instance["InstanceId"]
        public_ip = instance["PublicIpAddress"]
        tags = instance["Tags"]
        dist = list(filter(lambda tag: tag["Key"] == "Distribution", tags))[0]["Value"]
        connect_ssh(instance_id, public_ip, dist, args.forward_web)
    except Exception as e:
        print(e)
        exit(1)


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


if __name__ == "__main__":
    main()
