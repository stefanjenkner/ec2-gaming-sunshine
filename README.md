# EC2 Gaming on Linux

Powered by Ubuntu 22.04 on EC2 g4dn.xlarge Spot instances using NVIDIA gaming driver

## Features

Current features:

 * EC2 launch template with cloud-init config

## Howto

Create stack

    aws cloudformation create-stack \
        --stack-name jammy-sunshine \
        --template-body file://cloudformation/jammy-sunshine.yaml \
        --parameters ParameterKey=CloudConfig,ParameterValue=$(base64 cloud-config.yaml)

Update stack

    aws cloudformation update-stack \
        --stack-name jammy-sunshine \
        --template-body file://cloudformation/jammy-sunshine.yaml \
        --parameters ParameterKey=CloudConfig,ParameterValue=$(base64 cloud-config.yaml)

## Manual steps

Wait for cloud-init to finish:

    tail -f /var/log/cloud-init.log

Update grub:

    sudo update-initramfs -u
    sudo update-grub

Add default user to group input:

    sudo usermod -a -G input $USER

Install Steam:

    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends steam-launcher steam-libs-amd64 steam-libs-i386:i386

Install NVIDIA gaming driver and reboot:

    /opt/install_nvidia_driver.sh

    sudo reboot

    nvidia-smi -q | head

    sudo nvidia-xconfig --preserve-busid --enable-all-gpus

    reboot

Install sunshine:

    wget https://github.com/LizardByte/Sunshine/releases/download/v0.16.0/sunshine-22.04.deb
    sudo apt-get install -y ./sunshine-22.04.deb

    systemctl --user enable sunshine
    systemctl --user start sunshine

Configure username and password for sunshine:

    https --verify=no :47990/api/password newUsername="sunshine" newPassword="sunshine" confirmNewPassword="sunshine"

Determine public IPv4 address:

    cloud-init query ds.meta_data.public_ipv4

Allow connection by entering the PIN:

    https --verify=no -a sunshine:sunshine :47990/api/pin pin="0000"
