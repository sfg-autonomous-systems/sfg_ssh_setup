# SFG SSH Setup

This repository centrally manages SSH access for the SFG Autonomous Systems hardware.

Instead of manually copying SSH keys to individual robots and workstations, this setup configures the machines to dynamically pull authorized public keys directly from GitHub profiles based on a central JSON access control list. It includes offline caching so access remains active even if the network drops.

## Getting Started

To configure a machine to use this centralized SSH setup, clone this repository onto the target machine and run the setup script.

```bash
git clone https://github.com/sfg-autonomous-systems/sfg_ssh_setup
cd sfg_ssh_setup
sudo ./setup
```

The setup script uses standard Linux file hierarchies to securely install the components:

* **Configurations:** Installed to `/etc/ssh/ssh_config.d/00-sfg_ssh_client.conf` and `/etc/ssh/sshd_config.d/00-sfg_ssh_server.conf`.
* **Authorization Script:** Installed to `/usr/local/bin/sfg_fetch_authorized_keys.py`.
* **Authorized Keys Cache:** Stored in `/var/cache/sfg/authorized_keys/`.

## How to Get SSH Access

1. Ensure you have generated an SSH key pair on your personal machine and added the **public key** to your GitHub account.

    * [Adding a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)

2. Contact an admin with your GitHub username and which machines you would like to have access to.

Once approved by the admin, the hardware will automatically pull your public keys from `https://github.com/<username>.keys` the next time you attempt to log in.