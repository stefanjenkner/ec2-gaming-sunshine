#!/usr/bin/env python

import boto3

STACK_NAME = "ec2-gaming-sunshine"

def main():

    client = boto3.client("ec2")
    ec2 = boto3.resource("ec2")
    response = client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [f"{STACK_NAME}-instance"]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
        ]
    )
    reservations = response["Reservations"]

    if len(reservations) == 0:
        print("No running instances found, aborting.")
        return

    instances = reservations[0]["Instances"]
    for instance in instances:
        instance_id = instance["InstanceId"]
        ec2_instance = ec2.Instance(instance_id)
        print(f"Stopping {instance_id}")
        response = ec2_instance.stop()
        print(response)


if __name__ == "__main__":
    main()
