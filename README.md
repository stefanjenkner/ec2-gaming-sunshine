# EC2 Gaming on Linux

Powered by Ubuntu 22.04 on EC2 g4dn.xlarge Spot instances using NVIDIA gaming driver

## Features

Current features:

 * EC2 launch template
 * cloud-init config to setup EC2 instance

## Howto

Create stack

    aws cloudformation create-stack \
        --stack-name jammy-sunshine \
        --template-body file://cloudformation/jammy-sunshine.yaml

Update stack

    aws cloudformation update-stack \
        --stack-name jammy-sunshine \
        --template-body file://cloudformation/jammy-sunshine.yaml

## Manual steps

Wait for cloud-init to finish:

    tail -f /var/log/cloud-init.log

Update grub:

    sudo update-initramfs -u
    sudo update-grub

    reboot

Install NVIDIA gaming driver:

    cd /tmp
    aws s3 cp --recursive s3://nvidia-gaming/linux/latest/ .
    unzip *Cloud_Gaming-Linux-Guest-Drivers.zip -d nvidia-drivers
    chmod +x ./nvidia-drivers/NVIDIA-Linux-x86_64*-grid.run
    sudo /bin/sh ./nvidia-drivers/NVIDIA-Linux-x86_64*-grid.run

    cat << EOF | sudo tee -a /etc/nvidia/gridd.conf
    vGamingMarketplace=2
    EOF

    sudo curl -o /etc/nvidia/GridSwCert.txt "https://nvidia-gaming.s3.amazonaws.com/GridSwCert-Archive/GridSwCertLinux_2021_10_2.cert"

    sudo reboot

    nvidia-smi -q | head

    sudo nvidia-xconfig --preserve-busid --enable-all-gpus

Install sunshine:

    wget https://github.com/LizardByte/Sunshine/releases/download/v0.16.0/sunshine-22.04.deb
    sudo apt-get install -y ./sunshine-22.04.deb

    sudo usermod -a -G input $USER

    systemctl --user enable sunshine
    systemctl --user start sunshine


Install Steam:

    cat << EOF | sudo tee --append /etc/apt/sources.list.d/steam.list
    deb [arch=amd64,i386] https://repo.steampowered.com/steam/ stable steam
    deb-src [arch=amd64,i386] https://repo.steampowered.com/steam/ stable steam
    EOF

    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends steam-launcher steam-libs-amd64 steam-libs-i386:i386
