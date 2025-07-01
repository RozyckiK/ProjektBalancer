# Prerequisites:
# 1. W GUI Proxmox → Datacenter → twój node → local-lvm → Content → CT Templates
#    • Kliknij 'Download from URL' i wklej:
#        https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.tar.zst
#    • W CT Templates pojawi się plik, np. ubuntu-24.04-standard_24.04-2_amd64.tar.zst
# 2. Skopiuj ścieżkę template (np. local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst).
# 3. Uzupełnij poniższe zmienne.

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = ">= 2.9.7"
    }
  }
}

provider "proxmox" {
  pm_api_url      = var.proxmox_api_url
  pm_user         = var.proxmox_user
  pm_password     = var.proxmox_password
  pm_tls_insecure = var.proxmox_tls_insecure
}

# Variables
variable "proxmox_api_url" {
  description = "URL API Proxmox"
  type        = string
  default     = "https://192.168.0.239:8006/api2/json"
}

variable "proxmox_user" {
  description = "Użytkownik Proxmox"
  type        = string
  default     = "root@pam"
}

variable "proxmox_password" {
  description = "Hasło lub token Proxmox"
  type        = string
  default     = "adminadmin"
  sensitive   = true
}

variable "proxmox_tls_insecure" {
  description = "Pominięcie weryfikacji TLS"
  type        = bool
  default     = true
}

variable "proxmox_node" {
  description = "Nazwa węzła Proxmox"
  type        = string
  default     = "pvetest"
}

variable "cluster_containers" {
  description = "Lista kontenerów do utworzenia"
  type = list(object({
    name  = string
    ct_id = number
    ip    = string
  }))
  default = [
    { name = "ct-1", ct_id = 200, ip = "192.168.0.201/24" },
    { name = "ct-2", ct_id = 201, ip = "192.168.0.202/24" },
    { name = "ct-3", ct_id = 202, ip = "192.168.0.203/24" },
  ]
}

variable "ct_template" {
  description = "Ścieżka do LXC-template (storage:plik.tar.zst)"
  type        = string
  default     = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
}

variable "ssh_public_key" {
  description = "Ścieżka do publicznego klucza SSH do CT"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "ssh_private_key" {
  description = "Ścieżka do prywatnego klucza SSH do CT"
  type        = string
  default     = "~/.ssh/id_rsa"
}

variable "provision_commands" {
  description = "Polecenia shell do wykonania w CT"
  type        = list(string)
  default     = []
}

# Tworzenie kontenerów LXC\ 
resource "proxmox_lxc" "k8s_cts" {
  for_each    = { for ct in var.cluster_containers : ct.name => ct }
  vmid        = each.value.ct_id
  hostname    = each.value.name
  target_node = var.proxmox_node
  ostemplate  = var.ct_template
  cores       = 1
  memory      = 1024
  swap        = 512
  start       = true

  rootfs {
    storage = "local-lvm"
    size    = "8G"
  }
 
  network {
    name    = "eth0"
    bridge  = "vmbr0"
    ip      = each.value.ip
    gw      = "192.168.0.1"
    type    = "veth"
  }

  features {
    nesting = true
  }

  # Provisioning przez SSH w CT
  connection {
    type        = "ssh"
    host        = replace(each.value.ip, "/24", "")
    user        = "root"
    private_key = file(var.ssh_private_key)
    timeout     = "2m"
  }

  provisioner "remote-exec" {
    inline = var.provision_commands
  }
}

# Outputs
output "container_ips" {
  description = "Adresy IP kontenerów"
  value       = { for name, ct in proxmox_lxc.k8s_cts : name => ct.network[0].ip }
}