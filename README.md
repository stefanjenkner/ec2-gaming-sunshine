# EC2 Gaming on Linux

Powered by Ubuntu 22.04 on EC2 g4dn.xlarge Spot instances using NVIDIA gaming driver

## Features

Current features:

 * EC2 launch templates with cloud-init config
 * VPC with public subnet  and security groups to restrict access by IP
 * S3 bucket for fast backup/restore of SteamLibrary to/from instance storage

## Howto

Create or update stack:

    ./deploy.py

Launch spot instance:

    aws ec2 run-instances --launch-template LaunchTemplateName=jammy-sunshine-spot,Version=\$Latest

Launch on-demand instance:

    aws ec2 run-instances --launch-template LaunchTemplateName=jammy-sunshine-on-demand,Version=\$Latest

## Manual steps on first boot

Login to EC2 instance:

    ssh ubuntu@<IP>

Wait for cloud-init to finish:

    tail -f /var/log/cloud-init.log

Install NVIDIA gaming driver and reboot:

    sudo /opt/install_nvidia_driver.sh

    sudo reboot

Setup sunshine and configure username and password for sunshine API user:

    https --verify=no :47990/api/password newUsername="sunshine" newPassword="sunshine" confirmNewPassword="sunshine"

Set a password for sunshine Linux user:

    sudo passwd sunshine

Determine public IPv4 address and connect from Moonlight client:

    cloud-init query ds.meta_data.public_ipv4

Allow connection by entering the PIN:

    https --verify=no -a sunshine:sunshine :47990/api/pin pin="0000"

Launch Steam, Login for the first time and:

  * Move the Steam Library to `/mnt/sunshine/SteamLibrary` (Setting/Downloads/Steam Library Folder)
  * Enable Steam Play (Proton) for supported and all other titles (Setting/Steam Play)
  * Run Backup (via appliction icon or `/usr/local/bin/backup` before next shutdown/reboot)

## Optional steps

Add apps for different screen resolutions:

    https --verify=no -a sunshine:sunshine :47990/api/apps \
        name="1280x720" prep-cmd:='[{"do":"xrandr --output HDMI-1 --mode 1280x720","undo":""}]' \
        output="" cmd:=[] index=-1 detached:=[] image-path="desktop-alt.png"

    https --verify=no -a sunshine:sunshine :47990/api/apps \
        name="1280x800" prep-cmd:='[{"do":"xrandr --output HDMI-1 --mode 1280x800","undo":""}]' \
        output="" cmd:=[] index=-1 detached:=[] image-path="desktop-alt.png"

    https --verify=no -a sunshine:sunshine :47990/api/apps \
        name="1920x1080" prep-cmd:='[{"do":"xrandr --output HDMI-1 --mode 1920x1080","undo":""}]' \
        output="" cmd:=[] index=-1 detached:=[] image-path="desktop-alt.png"
