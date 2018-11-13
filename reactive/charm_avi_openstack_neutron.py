from charmhelpers.core.hookenv import config
from charmhelpers.core import templating
from charmhelpers.fetch import apt_install
from charms.reactive import set_flag
from charms.reactive import when
from charms.reactive import when_not

import subprocess


@when_not('charm-avi-openstack-neutron.installed')
def install_charm_avi_openstack_neutron():
    apt_install('python-pip')
    subprocess.check_call(['/usr/bin/pip',
                           'install',
                           'https://github.com/avinetworks/openstack-lbaasv2/'
                           'releases/download/%s/avi-lbaasv2-%s.tar.gz'
                           % (config('avi-controller-version'),
                              config('avi-controller-version'))
                           ])
    apt_install('python3-jinja2')
    set_flag('charm-avi-openstack-neutron.installed')


@when('neutron-plugin-api-subordinate.connected', 'config.changed')
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
        service_plugins=(
            'router,firewall,metering,segments,'
            'neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPluginv2,'
            'neutron_dynamic_routing.services.bgp.bgp_plugin.BgpPlugin'),
        subordinate_configuration={})

    api_principle.request_restart(service_type='neutron')
