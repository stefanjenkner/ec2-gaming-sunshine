import os
import unittest
from unittest.mock import patch

from moto import mock_aws

from src.on_ec2_start_stop_function import on_start_lambda_handler


class TestOnStartLambdaHandler(unittest.TestCase):
    def setUp(self):
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    @mock_aws
    def test_on_start_lambda_handler(self):
        with patch("boto3.client") as mock_client:
            # setup
            mock_ec2_client = mock_client.return_value
            mock_ec2_client.describe_instances.return_value = {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-aad04ef2c2abadd94",
                                "PublicIpAddress": "9.8.7.6",
                                "State": {"Name": "running"},
                            }
                        ]
                    }
                ]
            }
            event = {
                "detail": {"instance-id": "i-aad04ef2c2abadd94", "state": "running"}
            }
            context = {}
            # execute
            result = on_start_lambda_handler(event, context)
            # verify
            self.assertEqual(result["statusCode"], 200)
