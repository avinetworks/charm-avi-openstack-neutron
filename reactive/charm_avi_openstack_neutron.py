from charms.reactive import when, when_not, set_flag, hook
from charmhelpers.contrib.python.packages import (
    pip_install
)
from charmhelpers.fetch import (
    apt_install
)
from charmhelpers.core.hookenv import (
    config
)
from charmhelpers.core import (
    templating
)

import subprocess


@when_not('charm-avi-openstack-neutron.installed')
def install_charm_avi_openstack_neutron():
    subprocess.check_call(['pip3',
                           'install',
                           'https://github.com/avinetworks/openstack-lbaasv2/releases/'
                           'download/%s/avi-lbaasv2-%s.tar.gz'
                           % (config('avi-controller-version'),
                           config('avi-controller-version'))
                           ])
    apt_install('python3-jinja2')
    set_flag('charm-avi-openstack-neutron.installed')


@when('neutron-plugin-api-subordinate.connected')
def configure_principle(api_principle):

    avi_config = {
        'avi_controller_ip': config('avi-controller-ip'),
        'avi_admin_password': config('avi-controller-password')
    }
    templating.render('avi_lbaas.conf.template',
                      '/etc/neutron/plugins/avi/avi_lbaas.conf',
                      avi_config,
                      templates_dir='templates/')
    api_principle.configure_plugin(
        neutron_plugin='avi_lbaas',
        neutron_plugin_config='/etc/neutron/plugins/avi/avi_lbaas.conf',
        service_plugins=('router,firewall,metering,segments,'
                         'neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPluginv2,'
                         'neutron_dynamic_routing.services.bgp.bgp_plugin.BgpPlugin'),
        subordinate_configuration={})

    api_principle.request_restart(service_type='neutron')
