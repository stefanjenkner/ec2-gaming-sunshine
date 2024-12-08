# EC2 Gaming on Linux

Cloud Gaming powered by [Sunshine] on EC2 Spot Instances, tested with:

* EC2 g4dn instances using NVIDIA gaming driver
* EC2 g5 instances using NVIDIA gaming driver

## Features

Stable features:

* Launch templates for both Spot and On-Demand EC2 instances
* Minimalistic Ubuntu Linux 22.04 with [Sunshine], [Steam] and [Lutris] preinstalled
* VPC with public subnet and security groups to restrict access by IP
* S3 bucket for fast backup/restore of the Steam Library to/from instance storage using [restic]

Experimental features:

* Debian Bookworm (without gamepad support at this time)

## How-to

Show template:

    ./deploy.py --print-only

Deploying the CloudFormation stack the first time requires a keypair (in this case `ec2-gaming`) to exist:

    ./deploy.py --stack ec2-gaming-sunshine --keypair ec2-gaming

When updating CloudFormation stack, passing parameters is not required and existing settings remain untouched:

    ./deploy.py --stack ec2-gaming-sunshine

Launch spot instance:

    aws ec2 run-instances --launch-template LaunchTemplateName=ec2-gaming-sunshine-jammy-spot,Version=\$Latest

Launch on-demand instance:

    # ubuntu noble (24.04)
    aws ec2 run-instances --launch-template LaunchTemplateName=ec2-gaming-sunshine-noble-on-demand,Version=\$Latest
    # or: ubuntu jammy (22.04)
    aws ec2 run-instances --launch-template LaunchTemplateName=ec2-gaming-sunshine-jammy-on-demand,Version=\$Latest
    # or: debian bookworm (12)
    aws ec2 run-instances --launch-template LaunchTemplateName=ec2-gaming-sunshine-bookworm-on-demand,Version=\$Latest

Launch on-demand instance with custom instance type:

    aws ec2 run-instances --launch-template LaunchTemplateName=ec2-gaming-sunshine-jammy-on-demand,Version=\$Latest \
        --instance-type g5.4xlarge

By default, access to the EC2 instance is restriced. To update the whitelisted IP address to the IP address of the
caller:

    ./update-ip.py --stack ec2-gaming-sunshine

## Manual steps on first boot

### Install NVIDIA driver

Login to the EC2 instance:

    ./connect-ssh.py --stack ec2-gaming-sunshine

    # or: manually connect to Ubuntu (jammy) instances
    ssh ubuntu@<IP>
    # or: manually connect to Debian (bookworm) instances
    ssh admin@<IP>

Wait for [cloud-init] to finish:

    tail -f /var/log/cloud-init.log

Install NVIDIA gaming driver and reboot:

    sudo /opt/install_nvidia_driver.sh

    sudo reboot

### Setup Sunshine

Configure username and password for sunshine API user:

    https --verify=no :47990/api/password newUsername="sunshine" newPassword="sunshine" confirmNewPassword="sunshine"

Add apps for different screen resolutions:

    # 1280x720
    https --verify=no -a sunshine:sunshine :47990/api/apps \
        name="1280x720" prep-cmd:='[{"do":"xrandr --output DVI-D-0 --mode 1280x720","undo":""}]' \
        output="" cmd:=[] index=-1 detached:=[] image-path="desktop-alt.png"

    # 1280x800
    https --verify=no -a sunshine:sunshine :47990/api/apps \
        name="1280x800" prep-cmd:='[{"do":"xrandr --output DVI-D-0 --mode 1280x800","undo":""}]' \
        output="" cmd:=[] index=-1 detached:=[] image-path="desktop-alt.png"

    # 1920x1080
    https --verify=no -a sunshine:sunshine :47990/api/apps \
        name="1920x1080" prep-cmd:='[{"do":"xrandr --output DVI-D-0 --mode 1920x1080","undo":""}]' \
        output="" cmd:=[] index=-1 detached:=[] image-path="desktop-alt.png"

Set a password for `sunshine` Linux user:

    sudo passwd sunshine

Determine the public IPv4 address and connect via the [Moonlight] client:

    cloud-init query ds.meta_data.public_ipv4

Allow connection by entering the PIN:

    https --verify=no -a sunshine:sunshine :47990/api/pin pin="0000"

Launch Steam, Login for the first time and:

* Move the Steam Library to `/mnt/sunshine/SteamLibrary` (Setting/Downloads/Steam Library Folder)
* Enable Steam Play (Proton) for supported and all other titles (Setting/Steam Play)
* Run Backup (via application icon or `/usr/local/bin/backup` before next shutdown/reboot)

## Known issues

* no gamepad support in Debian Bookworm (12) due to missing `uinput` module in kernel flavour `cloud-amd64`
* no percentage indicator when restoring instance storage from S3

## Contribution

Prerequisites for development:

<details>
<summary>macOS</summary>

    brew install pre-commit commitizen

</details>

Set up pre-commit hooks:

    pre-commit install && pre-commit install --hook-type commit-msg && pre-commit run

[cloud-init]: https://cloudinit.readthedocs.io/
[Lutris]: https://lutris.net
[Moonlight]: https://github.com/moonlight-stream/moonlight-qt/
[restic]: https://github.com/restic/restic/
[Steam]: https://repo.steampowered.com/steam/
[Sunshine]: https://github.com/LizardByte/Sunshine/
