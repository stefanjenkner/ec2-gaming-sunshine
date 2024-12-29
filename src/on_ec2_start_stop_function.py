import json
import os

import boto3


def on_start_lambda_handler(event, context):
    instance_id = event["detail"]["instance-id"]

    public_ip = get_public_ip(instance_id)

    route53_client = boto3.client("route53")
    hosted_zone_id = os.environ.get("HOSTED_ZONE_ID")
    hosted_zone_name = get_hosted_zone_name(route53_client, hosted_zone_id)
    fqdn = f"{instance_id}.{hosted_zone_name}"
    update_route53_record(route53_client, public_ip, hosted_zone_id, fqdn)

    return {
        "statusCode": 200,
        "body": json.dumps(
            f"EC2 instance {instance_id} started, DNS record {fqdn} updated to {public_ip}."
        ),
    }


def on_stop_lambda_handler(event, context):
    instance_id = event["detail"]["instance-id"]

    route53_client = boto3.client("route53")
    hosted_zone_id = os.environ.get("HOSTED_ZONE_ID")
    hosted_zone_name = get_hosted_zone_name(route53_client, hosted_zone_id)
    fqdn = f"{instance_id}.{hosted_zone_name}"
    delete_route53_record(route53_client, hosted_zone_id, fqdn)

    return {
        "statusCode": 200,
        "body": json.dumps(
            f"EC2 instance {instance_id} stopped, DNS record {fqdn} deleted."
        ),
    }


def get_public_ip(instance_id):
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    reservations = response["Reservations"]
    for reservation in reservations:
        for instance in reservation["Instances"]:
            public_ip = instance.get("PublicIpAddress")
            if public_ip:
                return public_ip
    return None


def get_hosted_zone_name(route53_client, hosted_zone_id):
    response = route53_client.get_hosted_zone(Id=hosted_zone_id)
    return response["HostedZone"]["Name"]


def update_route53_record(route53_client, ip_address, hosted_zone_id, domain_name):
    response = route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": domain_name,
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": ip_address}],
                    },
                }
            ]
        },
    )
    return response


def delete_route53_record(route53_client, hosted_zone_id, domain_name):
    record_sets = route53_client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=domain_name,
        StartRecordType="A",
        MaxItems="10",
    )

    target_record = next(
        (
            record
            for record in record_sets["ResourceRecordSets"]
            if record["Name"] == domain_name and record["Type"] == "A"
        ),
        None,
    )

    if target_record:
        route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [{"Action": "DELETE", "ResourceRecordSet": target_record}]
            },
        )
