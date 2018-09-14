from charms.reactive import when, when_not, set_flag
from charmhelpers.contrib.python.packages import (
    pip_install
)
from charmhelpers.core.hookenv import (
    config
)


@when_not('charm-avi-openstack-neutron.installed')
def install_charm_avi_openstack_neutron():
    pip_install('https://github.com/avinetworks/openstack-lbaasv2/releases/'
                'download/%s/avi-lbaasv2-%s.tar.gz'
                % (config('avi-controller-version'),
                   config('avi-controller-version')))
    set_flag('charm-avi-openstack-neutron.installed')


@when('neutron-plugin-api-subordinate.connected')
def configure_principle(api_principle):
    inject_config = {
        "neutron-api": {
            "/etc/neutron/neutron.conf": {
                "sections": {
                    'DEFAULT': [
                        ('service_provider',
                         'LOADBALANCERV2:avi_adc:avi_lbaasv2.'
                         'avi_driver.'
                         'AviDriver:default'),
                    ],
                    'avi_adc': [
                        ('address', config('avi-controller-ip')),
                        ('user', 'admin'),
                        ('password', config('avi-controller-password')),
                        ('cloud', 'openstack'),
                    ],
                }
            }
        }
    }
    api_principle.configure_plugin(
        neutron_plugin='odl',
        core_plugin='neutron.plugins.ml2.plugin.Ml2Plugin',
        neutron_plugin_config='/etc/neutron/plugins/ml2/ml2_conf.ini',
        service_plugins='router,firewall,lbaas,vpnaas,metering',
        subordinate_configuration=inject_config)

    api_principle.request_restart(service_type='neutron')
