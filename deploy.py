#!/usr/bin/env python

import base64

import boto3
from jinja2 import Template


def main():

    with open("cloudformation/jammy-sunshine.yaml") as cf_:
        template = Template(cf_.read())

    with open("cloud-config.yaml", "rb") as cloud_config_:
        cloud_config_b64_ = base64.b64encode(cloud_config_.read())
        cloud_config_b64_text_ = cloud_config_b64_.decode("ascii")

    client = boto3.client("cloudformation")
    response = client.update_stack(
        StackName="jammy-sunshine",
        TemplateBody=template.render(cloud_config=cloud_config_b64_text_),
        Parameters=[{"ParameterKey": "MyIp", "UsePreviousValue": True}],
        Capabilities=["CAPABILITY_NAMED_IAM"],
    )
    print(response)


if __name__ == "__main__":
    main()
