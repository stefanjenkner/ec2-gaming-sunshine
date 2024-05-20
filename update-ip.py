#!/usr/bin/env python

import logging
import http.client
import socket
import ssl

import botocore
import boto3

STACK_NAME = "ec2-gaming-sunshine"

def main():

    logging.basicConfig(level=logging.INFO)

    client = boto3.client("cloudformation")

    logging.info(f"Updating stack {STACK_NAME}")

    try:
        ip = get_ip()
        ip_cidr = f"{ip}/32"
        logging.info(f"Updating IP whitelisting to: {ip_cidr}")
        client.update_stack(
            StackName=STACK_NAME,
            UsePreviousTemplate=True,
            Parameters=[
                {"ParameterKey": "MyIp", "ParameterValue": ip_cidr},
                {"ParameterKey": "KeyPair", "UsePreviousValue": True},
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )

    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ValidationError":
            logging.error(error.response["Error"]["Message"])
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
    main()
