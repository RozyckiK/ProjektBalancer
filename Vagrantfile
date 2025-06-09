Vagrant.configure("2") do |config|
  # Base box and global settings
  config.vm.box = "ubuntu/focal64"
  config.vm.boot_timeout = 600

  # Define nodes (uncomment for multi-node cluster)
  nodes = [
    { name: "node-1", ip: "192.168.56.11", memory: 2048, cpus: 2 },
    { name: "node-2", ip: "192.168.56.12", memory: 2048, cpus: 2 },
    { name: "node-3", ip: "192.168.56.13", memory: 2048, cpus: 2 },
    # { name: "node-4", ip: "192.168.56.14", memory: 2048, cpus: 2 },
    # { name: "node-5", ip: "192.168.56.15", memory: 2048, cpus: 2 },
  ]

  nodes.each do |n|
    config.vm.define n[:name] do |node|
      node.vm.hostname = n[:name]
      node.vm.network "private_network", ip: n[:ip]

      node.vm.provider "virtualbox" do |vb|
        vb.memory = n[:memory]
        vb.cpus   = n[:cpus]
      end

      # Common provisioning
      node.vm.provision "shell", inline: <<-SHELL
        set -eux
        echo "=== Disable swap ==="
        swapoff -a
        sed -i '/ swap / s/^/#/' /etc/fstab

        echo "=== Load kernel modules ==="
        modprobe overlay
        modprobe br_netfilter
        cat <<EOF > /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

        echo "=== Apply sysctl params ==="
        cat <<EOF > /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
        sysctl --system

        echo "=== Install dependencies ==="
        apt-get update
        apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

        echo "=== Install containerd ==="
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
          | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
          | tee /etc/apt/sources.list.d/docker.list > /dev/null
        apt-get update
        apt-get install -y containerd.io
        mkdir -p /etc/containerd
        containerd config default > /etc/containerd/config.toml
        systemctl restart containerd
        systemctl enable containerd

        echo "=== Add Kubernetes v1.28 repo ==="
        mkdir -p /etc/apt/keyrings
        curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key \
          | gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
        echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" \
          | tee /etc/apt/sources.list.d/kubernetes.list > /dev/null

        echo "=== Install kubeadm, kubelet & kubectl v1.28.1 ==="
        apt-get update
        apt-get install -y \
          kubelet=1.28.1-1.1 \
          kubeadm=1.28.1-1.1 \
          kubectl=1.28.1-1.1
        apt-mark hold kubelet kubeadm kubectl

        echo "=== Provisioning complete ==="
      SHELL

      if n[:name] == "node-1"
        # Initialize master
        node.vm.provision "shell", inline: <<-SHELL
          set -eux
          echo "=== Initialize Kubernetes master ==="
          kubeadm init --apiserver-advertise-address=#{n[:ip]} --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=Swap,Mem

          # Save join command for workers
          kubeadm token create --print-join-command > /vagrant/join.sh

          # Configure kubectl for vagrant user
          mkdir -p /home/vagrant/.kube
          cp -i /etc/kubernetes/admin.conf /home/vagrant/.kube/config
          chown vagrant:vagrant /home/vagrant/.kube/config

          # Deploy Flannel CNI
          su - vagrant -c "kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml"
        SHELL
      else
        # Worker nodes wait for join.sh then join
        node.vm.provision "shell", inline: <<-SHELL
          set -eux
          echo "=== Waiting for join.sh to appear ==="
          while [ ! -f /vagrant/join.sh ]; do sleep 2; done
          echo "=== Join Kubernetes cluster ==="
          bash /vagrant/join.sh --ignore-preflight-errors=Swap,Mem
        SHELL
      end
    end
  end

  # After all VMs are up, wait 2 minutes then display node list on master
  config.trigger.after :up do |t|
    t.info = "Waiting 120 seconds then listing Kubernetes nodes"
    t.run  = {
      inline: "powershell -Command \"vagrant ssh node-1 -c 'kubectl get nodes'\""
    }
  end
end
