build {
  sources = ["source.proxmox-iso.ubuntu-2404"]

  provisioner "shell" {
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do sleep 1; done",
      "sudo systemctl enable qemu-guest-agent",
      "sudo systemctl start qemu-guest-agent",
      "sudo cloud-init clean",
      "sudo rm -f /etc/netplan/00-installer-config.yaml"
    ]
  }
}
