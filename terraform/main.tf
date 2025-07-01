terraform {
    required_providers {
        proxmox = {
            source = "telmate/proxmox"
            version = "3.0.1-rc6"
        }
    }
}

provider "proxmox" {
    pm_api_url          = "https://YOUR_IP/api2/json"            #Do wypełnienia i opisania
    pm_api_token_id     = "TOKEN ID"                             #Do wypełnienia i opisania
    pm_api_token_secret = "API TOKEN SECRET"                     #Do wypełnienia i opisania
    pm_tls_insecure     = true

    /*
    pm_log_enable = true
    pm_log_file = "terraform-plugin-proxmox.log"
    pm_debug = true
    pm_log_levels = {
    _default = "debug"
    _capturelog = ""
    }
    */
}

resource "proxmox_vm_qemu" "vm-instance" {
    count               = 3
    name                = "vm-instance-${count.index + 1}"
    target_node         = "pvetest"
    clone               = "tmpl"                                            #Do wypełnienia i opisania
    full_clone          = true
    cores               = 2
    memory              = 2048
    vmid                = "${count.index + 6600 + 1}"

    disk {
        slot            = "scsi0"
        size            = "10G"
        storage         = "local-lvm"                                       #Do wypełnienia i opisania
    }

    network {
        id = 0
        model     = "virtio"
        bridge    = "vmbr0"                                                 #Do wypełnienia i opisania
        firewall  = false
        link_down = false
    }

}