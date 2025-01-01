from time import sleep

import boto3


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
