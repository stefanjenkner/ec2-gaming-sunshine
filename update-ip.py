#!/usr/bin/env python

import argparse
import http.client
import logging
import socket
import ssl
import sys

import boto3
import botocore

DEFAULT_STACK_NAME = "ec2-gaming-sunshine"


def main():
    parser = argparse.ArgumentParser(prog="update-ip", epilog="Update whitelisted IP")
    parser.add_argument(
        "--stack-name",
        help=f"Name of CloudFormation stack, defaults to '{DEFAULT_STACK_NAME}'",
        default=DEFAULT_STACK_NAME,
    )

    args = parser.parse_args()
    stack_name = args.stack_name

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Updating stack {stack_name}")

    client = boto3.client("cloudformation")

    try:
        ip = get_ip()
        ip_cidr = f"{ip}/32"
        logging.info(f"Updating IP whitelisting to: {ip_cidr}")
        client.update_stack(
            StackName=stack_name,
            UsePreviousTemplate=True,
            Parameters=[
                {"ParameterKey": "MyIp", "ParameterValue": ip_cidr},
                {"ParameterKey": "KeyPair", "UsePreviousValue": True},
            ],
            Capabilities=["CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"],
        )

    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            logging.error(error.response["Error"]["Message"])
            return 1
        else:
            raise error


def get_ip():
    host = "ifconfig.me"
    conn = IPv4HTTPSConnection(host)
    conn.request("GET", "/ip", headers={"Host": host})
    response = conn.getresponse()
    ip = response.read().decode("utf-8")
    conn.close()
    return ip


class IPv4HTTPSConnection(http.client.HTTPSConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        if self._tunnel_host:
            self._tunnel()
        context = ssl.create_default_context()
        self.sock = context.wrap_socket(self.sock, server_hostname=self.host)


if __name__ == "__main__":
    sys.exit(main())
