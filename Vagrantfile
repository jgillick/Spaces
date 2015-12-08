
require './vagrant/config'

Vagrant.configure(2) do |config|
  config.vm.box = $vagrant_settings[:vm]
  config.vm.network "forwarded_port",
                    guest: 8000,
                    host: $vagrant_settings[:port]
  config.vm.provision "shell", path: "vagrant/provision.sh"
end
