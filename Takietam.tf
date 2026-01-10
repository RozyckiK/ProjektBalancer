resource "proxmox_virtual_environment_vm" "ubuntu_vm" {
  for_each = var.vms

  name      = each.key
  node_name = var.target_node

  clone {
    vm_id = 9001
    full  = true
  }

  cpu    { cores = each.value.cores }
  memory { dedicated = each.value.memory }

  initialization {
    ip_config {
      ipv4 {
        address = each.value.ip_address
        gateway = var.gateway
      }
    }
    user_account {
      username = "ubuntu"
      keys     = [var.ssh_public_keys]
      password = var.vm_password
    }
  }
}
