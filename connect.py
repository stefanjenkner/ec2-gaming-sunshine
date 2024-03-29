#!/usr/bin/env python

import subprocess
from sys import platform

import boto3

if platform == "linux" or platform == "linux2":
    MOONLIGHT_QT = "moonlight-qt"
elif platform == "darwin":
    MOONLIGHT_QT = "/Applications/Moonlight.app/Contents/MacOS/Moonlight"


def main():

    client = boto3.client("ec2")
    boto3.resource("ec2")
    response = client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": ["jammy-sunshine-instance"]},
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
    print(f"Connecting to IP {public_ip}")

    if not is_ready(public_ip):
        subprocess.run([MOONLIGHT_QT, "pair", "--pin", "0000", public_ip])

    subprocess.run([MOONLIGHT_QT, "stream", public_ip, "Low Res Desktop"])


def is_ready(public_ip):

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
    return retval == 0 and b"Low Res Desktop\n" in output


if __name__ == "__main__":
    main()
