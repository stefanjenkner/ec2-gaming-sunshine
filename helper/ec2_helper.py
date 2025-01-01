from typing import List

import boto3


class NoInstancesFoundError(Exception):
    pass


class MoreThanOneInstanceFoundError(Exception):
    pass


class InstanceNotFoundError(Exception):
    pass


def get_one_instance(stack_name: str, passed_id: str, state_names: List[str]) -> dict:
    """
    Get EC2 instance, filtered by stack name, states and optionally passed instance id.
    """
    instances = get_instances(stack_name, state_names)
    instance_ids = [instance["InstanceId"] for instance in instances]
    if len(instances) == 0:
        raise NoInstancesFoundError(f"No instances found with states: {state_names}")
    elif len(instances) > 1 and passed_id is None:
        raise MoreThanOneInstanceFoundError(
            f"More than one instance found: {instance_ids}"
        )
    elif passed_id is not None and passed_id not in instance_ids:
        raise InstanceNotFoundError(f"Instance not found: {passed_id}")

    instance_id = passed_id or instances[0]["InstanceId"]
    return next(filter(lambda i: i["InstanceId"] == instance_id, instances))


def get_instances(stack_name: str, state_names: List[str]) -> List[dict]:
    """
    Retrieve list EC2 instances, filtered by stack name and states.
    """
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [f"{stack_name}-instance"]},
            {"Name": "instance-state-name", "Values": state_names},
        ]
    )
    return [
        instance
        for reservation in response["Reservations"]
        for instance in reservation["Instances"]
    ]
