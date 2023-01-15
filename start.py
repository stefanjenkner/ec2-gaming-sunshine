#!/usr/bin/env python

import boto3


def main():

    client = boto3.client("ec2")
    ec2 = boto3.resource("ec2")
    response = client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": ["jammy-sunshine-instance"]},
            {"Name": "instance-state-name", "Values": ["stopped"]},
        ]
    )

    reservations = response["Reservations"]
    if len(reservations) == 0:
        print("No stopped instances found, aborting.")
        return

    instances = reservations[0]["Instances"]
    if len(instances) > 1:
        print("More than one instance found, aborting.")
        return

    instance_id = instances[0]["InstanceId"]
    ec2_instance = ec2.Instance(instance_id)
    print(f"Starting {instance_id}")
    response = ec2_instance.start()
    print(response)


if __name__ == "__main__":
    main()
