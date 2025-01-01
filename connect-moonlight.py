#!/usr/bin/env python

import argparse
import subprocess
from random import randint
from sys import exit, platform
from time import sleep

from helper.ec2_helper import get_one_instance
from helper.ssm_helper import run_ssm_command

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

    try:
        instance = get_one_instance(
            args.stack_name, args.instance_id, ["running", "pending"]
        )
        instance_id = instance["InstanceId"]
        public_ip = instance["PublicIpAddress"]
        connect_moonlight(instance_id, public_ip, args.app)
    except Exception as e:
        print(e)
        exit(1)


def connect_moonlight(instance_id: str, public_ip: str, app: str):
    print(f"Connecting to EC2 instance {instance_id} using IP {public_ip}")
    if not is_ready(public_ip, app):
        pair(public_ip, instance_id)
    subprocess.run([MOONLIGHT_QT, "stream", public_ip, app])


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


def pair(public_ip: str, instance_id: str):
    pin = f"{randint(0, 9999):04}"
    command = f"https --ignore-stdin --verify=no -a sunshine:sunshine :47990/api/pin pin={pin}"
    moonlight = subprocess.Popen([MOONLIGHT_QT, "pair", "--pin", pin, public_ip])
    sleep(3)
    run_ssm_command(instance_id, command)
    moonlight.wait()


if __name__ == "__main__":
    main()
