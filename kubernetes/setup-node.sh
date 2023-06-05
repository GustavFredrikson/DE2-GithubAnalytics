sudo snap install microk8s --classic
sudo usermod -a -G microk8s ubuntu
mkdir -p ~/.kube
sudo chown -R ubuntu ~/.kube
newgrp microk8s
#microk8s enable dashboard dns registry istio mayastor hostpath-storage helm
#sudo microk8s enable dashboard dns registry istio mayastor hostpath-storage helm
sudo sysctl vm.nr_hugepages=1024
echo 'vm.nr_hugepages=1024' | sudo tee -a /etc/sysctl.conf
echo vm.nr_hugepages = 1024 | sudo tee -a /etc/sysctl.d/20-microk8s-hugepages.conf
echo '192.168.2.36 gp10-0' | sudo tee -a /etc/hosts
echo '192.168.2.231 gp10-1' | sudo tee -a /etc/hosts
echo '192.168.2.51 gp10-2' | sudo tee -a /etc/hosts
echo '192.168.2.98 gp10-3' | sudo tee -a /etc/hosts
sudo apt install -y linux-modules-extra-$(uname -r)
sudo modprobe nvme_tcp
echo 'nvme-tcp' | sudo tee -a /etc/modules-load.d/microk8s-mayastor.conf
microk8s stop
microk8s start
#sudo microk8s enable core/mayastor --default-pool-size 40G
microk8s join 192.168.2.36:25000/5072de17300771d54b956859ae45aa5b/144669b6ad2a
#sudo reboot now

