# EC2 Gaming on Linux

Powered by Ubuntu 22.04 on EC2 g4dn.xlarge Spot instances using NVIDIA gaming driver

## Features

Current features:

 * EC2 launch template with cloud-init config

## Howto

Create stack

    aws cloudformation create-stack \
        --stack-name jammy-sunshine \
        --capabilities CAPABILITY_NAMED_IAM \
        --template-body file://cloudformation/jammy-sunshine.yaml \
        --parameters ParameterKey=CloudConfig,ParameterValue=$(base64 cloud-config.yaml)

Update stack

    aws cloudformation update-stack \
        --stack-name jammy-sunshine \
        --capabilities CAPABILITY_NAMED_IAM \
        --template-body file://cloudformation/jammy-sunshine.yaml \
        --parameters ParameterKey=CloudConfig,ParameterValue=$(base64 cloud-config.yaml)

Launch instance

    aws ec2 run-instances --launch-template LaunchTemplateName=jammy-sunshine-launch-template,Version=\$Latest

## Manual steps

Wait for cloud-init to finish:

    tail -f /var/log/cloud-init.log

Install NVIDIA gaming driver and reboot:

    sudo /opt/install_nvidia_driver.sh

    nvidia-smi -q | head

    sudo nvidia-xconfig --preserve-busid --enable-all-gpus

    sudo reboot

Setup sunshine and configure username and password for sunshine:

    https --verify=no :47990/api/password newUsername="sunshine" newPassword="sunshine" confirmNewPassword="sunshine"

Determine public IPv4 address:

    cloud-init query ds.meta_data.public_ipv4

Allow connection by entering the PIN:

    https --verify=no -a sunshine:sunshine :47990/api/pin pin="0000"
