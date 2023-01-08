# EC2 Gaming on Linux

Powered by Ubuntu 22.04 on EC2 g4dn.xlarge Spot instances using NVIDIA gaming driver


## Howto

Validate template

    aws cloudformation validate-template \
        --template-body file://cloudformation/jammy-sunshine.yaml

Create stack

    aws cloudformation create-stack \
        --stack-name jammy-sunshine \
        --template-body file://cloudformation/jammy-sunshine.yaml

Update stack

    aws cloudformation update-stack \
        --stack-name jammy-sunshine \
        --template-body file://cloudformation/jammy-sunshine.yaml
