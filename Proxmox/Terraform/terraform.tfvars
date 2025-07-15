
proxmox_api_url = "https://" #Tutaj wkleić proxmox_url z notatnika, wkleić za https:// ale przed "


target_node = "" #Tutaj wkleić proxmox_node z notatnika, wkleić pomiędzy cudzysłowia


disk_storage = "local-lvm"


network_bridge = "vmbr0"
gateway        = "192.168.0.1"
dns_servers    = ["8.8.8.8", "8.8.4.4"]
dns_domain     = "home"



ssh_public_keys = "" #Tutaj wkleić public_key z notatnika, wkleić pomiędzy cudzysłowia


vms = {
  "node-1" = {
    ip_address = "192.168.0.200/24"
    cores      = 2
    memory     = 2048
    disk_size  = "20"
  }
  "node-2" = {
    ip_address = "192.168.0.201/24"
    cores      = 2
    memory     = 2048
    disk_size  = "20"
  }
  "node-3" = {
    ip_address = "192.168.0.202/24"
    cores      = 2
    memory     = 2048
    disk_size  = "20"
  }
  "node-4" = {
    ip_address = "192.168.0.203/24"
    cores      = 2
    memory     = 2048
    disk_size  = "20"
  }
}
