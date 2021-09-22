# VXLAN tunnel interface configuration and Underlay
"""
author: Luis Enrique Tapia
email: luis.e.hernandez@nokia.com
version: 1.0
"""

# Populate a data object, Add formatter instances
from srlinux.data import ColumnFormatter, TagValueFormatter, Border, Data, Borders, Alignment
from srlinux import strings

from srlinux.mgmt.cli import CliPlugin

# Build the SchemaNode
from srlinux.schema import FixedSchemaRoot
# Retrieve the state from the management server
from srlinux.location import build_path

from srlinux.syntax import Syntax


from srlinux.mgmt.cli.plugins.reports.gnmi_lite import GNMIHandlerLite
import datetime

uplink_network_instance = "default"


class Plugin(CliPlugin):

    def load(self, cli, **_kwargs):
        report = cli.show_mode.add_command(Syntax(
            'report',  help='shows how to give the input parameters for "show report" commands'))
        help = report.add_command(Syntax(
            'help', help='requires uplinks, route-reflector, statistics or summary keywords'), update_location=False, callback=self._show_help)
        vxlan = report.add_command(Syntax(
            'help', help='requires uplinks, route-reflector, statistics or summary keywords'), update_location=False, callback=self._show_vxlan_info, schema=self._get_schema())

    def _show_help(self, state, output, **_kwargs):
        print('''
        This 'show report' command correlate the vxlan tunnel interface configuration and the status of the underlay. 
        Therefore it requires some inputs that need to be added in the 'report.py' file.
        
        '/etc/opt/srlinux/cli/plugins'

        ''')

    def _show_vxlan_info(self, state, output, **_kwargs):
        server_data = self._fetch_state(state, _kwargs[0])
        result = Data(self._get_schema())
        self._set_formatter_vxlan(result)
        data = result.vxlan_header.create()

        for interface in server_data.interface.items():
            print(interface)

    def _set_formatter_vxlan(self, data):
        data.set_formatter('/vxlan_header/vxlan_child', ColumnFormatter(
            horizontal_alignment={'Ingress VNI': Alignment.Center}))

    def _populate_data_vxlan(self, result, state):
        pass

    def _get_schema(self):
        # Build the SchemaNode
        root = FixedSchemaRoot()

        # Section of the VXLAN
        vxlan_header = root.add_child(
            'vxlan_header',
            fields=['uplinks']
        )
        vxlan_header.add_child(
            'vxlan_child',
            key='Local Interface',
            fields=['Tunnel Interface', 'VxLAN Interface', 'Type',
                    'Ingress VNI', 'Egress source-ip']
        )

    def _fetch_state(self, state, arguments):
        # Retrieve the state from the management server
        """
        2. Recupere el estado del servidor de administración usando state.server_data_store.get_data y la ruta (<ruta>)
        """
        print(arguments)
        path = build_path('/tunnel-interface[name=*]/vxlan-interface[index=*]')
        return state.server_data_store.get_data(path, recursive=True)
