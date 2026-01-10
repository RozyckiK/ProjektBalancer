resource "local_file" "ansible_inventory" {
  content = <<EOL
[masters]
${local.vms_info[local.vms_keys[0]].name} ansible_host=${local.vms_info[local.vms_keys[0]].ip} ansible_user=ubuntu

[workers]
%{ for idx, k in local.vms_keys }
%{ if idx > 0 }
${local.vms_info[k].name} ansible_host=${local.vms_info[k].ip} ansible_user=ubuntu
%{ endif }
%{ endfor }
EOL
  filename = "${path.module}/hosts"
}

resource "null_resource" "ansible_provision" {
  depends_on = [proxmox_virtual_environment_vm.ubuntu_vm, local_file.ansible_inventory]

  provisioner "local-exec" {
    command = <<EOT
      sleep 30
      ansible-playbook -i ${path.module}/hosts playbooks/k3s-config.yml
      ansible-playbook -i ${path.module}/hosts playbooks/deployment.yml
    EOT
  }
}
