import json
import os

import boto3


def on_start_lambda_handler(event, context):
    instance_id = event["detail"]["instance-id"]
    public_ip = get_public_ip(instance_id)
    hosted_zone_id = os.environ.get("HOSTED_ZONE_ID")
    update_route53_records(hosted_zone_id, instance_id, public_ip)
    return {
        "statusCode": 200,
        "body": json.dumps(
            f"EC2 instance {instance_id} started, DNS records updated to {public_ip}."
        ),
    }


def on_stop_lambda_handler(event, context):
    instance_id = event["detail"]["instance-id"]
    hosted_zone_id = os.environ.get("HOSTED_ZONE_ID")
    delete_route53_records(hosted_zone_id, instance_id)
    return {
        "statusCode": 200,
        "body": json.dumps(f"EC2 instance {instance_id} stopped, DNS records deleted."),
    }


def get_public_ip(instance_id):
    client = boto3.client("ec2")
    response = client.describe_instances(InstanceIds=[instance_id])
    reservations = response["Reservations"]
    for reservation in reservations:
        for instance in reservation["Instances"]:
            public_ip = instance.get("PublicIpAddress")
            if public_ip:
                return public_ip
    return None


def update_route53_records(hosted_zone_id, instance_id, ip_address):
    client = boto3.client("route53")
    hosted_zone_name = client.get_hosted_zone(Id=hosted_zone_id)["HostedZone"]["Name"]
    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": f"{instance_id}.{hosted_zone_name}",
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": ip_address}],
                    },
                },
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": f"p{instance_id}.{hosted_zone_name}",
                        "Type": "AAAA",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": f"::ffff:{ip_address}"}],
                    },
                },
            ]
        },
    )
    return response


def delete_route53_records(hosted_zone_id, instance_id):
    client = boto3.client("route53")
    hosted_zone_name = client.get_hosted_zone(Id=hosted_zone_id)["HostedZone"]["Name"]

    delete_route53_record_if_exists(
        client, hosted_zone_id, f"{instance_id}.{hosted_zone_name}", "A"
    )
    delete_route53_record_if_exists(
        client, hosted_zone_id, f"p{instance_id}.{hosted_zone_name}", "AAAA"
    )


def delete_route53_record_if_exists(client, hosted_zone_id, record_name, record_type):
    record_sets = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=record_name,
        StartRecordType=record_type,
        MaxItems="10",
    )
    target_record = next(
        (
            record
            for record in record_sets["ResourceRecordSets"]
            if record["Name"] == record_name and record["Type"] == record_type
        ),
        None,
    )
    if target_record:
        client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [{"Action": "DELETE", "ResourceRecordSet": target_record}]
            },
        )
