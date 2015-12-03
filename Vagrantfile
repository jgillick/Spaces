Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.provision "shell", path: "vagrant_provision.sh"
end
