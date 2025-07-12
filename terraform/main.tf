terraform {
    required_providers {
        proxmox = {
            source = "telmate/proxmox"
            version = "3.0.1-rc6"
        }
    }
}

provider "proxmox" {
    pm_api_url          = "https://YOUR_IP/api2/json"               #Do wypełnienia i opisania
    pm_api_token_id     = "TOKEN_ID"                                #Do wypełnienia i opisania
    pm_api_token_secret = "TOKEN_SECRET"                            #Do wypełnienia i opisania
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
    clone               = "ubuntu-2404-template"                                            #Do wypełnienia i opisania
    full_clone          = true
    cores               = 2
    memory              = 2048
    vmid                = "${count.index + 6600 + 1}"
    agent = 1
    additional_wait     = 60

    disk {
        slot            = "scsi0"
        size            = "20G"                                             #Do wypełnienia i opisania
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

resource "local_file" "ansible_inventory" {
  content = <<EOT
[masters]
${proxmox_vm_qemu.vm-instance[0].name} ansible_host=${proxmox_vm_qemu.vm-instance[0].default_ipv4_address} ansible_user=ubuntu ansible_ssh_pass=ubuntu ansible_ssh_common_args='-o StrictHostKeyChecking=no'

[workers]
%{ for idx, vm in proxmox_vm_qemu.vm-instance }
%{ if idx > 0 }
${vm.name} ansible_host=${vm.default_ipv4_address} ansible_user=ubuntu ansible_ssh_pass=ubuntu ansible_ssh_common_args='-o StrictHostKeyChecking=no'
%{ endif }
%{ endfor }
EOT

  filename = "${path.module}/hosts"
}

resource "null_resource" "ansible_provision" {
  # Zależność: odpali się dopiero po VM i pliku hosts!
  depends_on = [proxmox_vm_qemu.vm-instance, local_file.ansible_inventory]

  # Komenda odpala ansible-playbook na host-maszynie (twoim controllerze)
  provisioner "local-exec" {
    command = <<EOT
      sleep 30
      ansible-playbook -i ${path.module}/hosts playbooks/fix_dns.yml
      ansible-playbook -i ${path.module}/hosts playbooks/host_name_change.yml
      ansible-playbook -i ${path.module}/hosts playbooks/k8s_prepare.yml
      ansible-playbook -i ${path.module}/hosts playbooks/k8s_containerd.yml
      ansible-playbook -i ${path.module}/hosts playbooks/k8s_tools.yml
      ansible-playbook -i ${path.module}/hosts playbooks/master_init.yml
      ansible-playbook -i ${path.module}/hosts playbooks/worker_join.yml
      ansible-playbook -i ${path.module}/hosts playbooks/k8s_deploy.yml
    EOT
  }
}
