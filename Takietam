packer {
  required_plugins {
    proxmox = {
      version = ">= 1.1.3"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

source "proxmox-iso" "ubuntu-2404" {
  vm_name    = "ubuntu-2404-template"
  cloud_init = true

  additional_iso_files {
    cd_files = [
      "./http/meta-data",
      "./http/user-data"
    ]
    cd_label = "cidata"
  }

  boot_command = [
    "<esc><wait>",
    "e<wait>",
    "<down><down><down><end>",
    " autoinstall quiet ds=nocloud",
    "<f10><wait>"
  ]
}
