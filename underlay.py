# Custom show command
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


class Plugin(CliPlugin):

    def load(self, cli, **_kwargs):
        cli.show_mode.add_command(Syntax('report').add_unnamed_argument(
            'name'), update_location=False, callback=self._print, schema=self._get_my_schema(),)

    def _get_my_schema(self):
        # Build the SchemaNode
        """
        1. Cree un SchemaNode para describir el modelo de datos de los datos para la rutina show.
        """
        """
            root level
            list interface {
                key "name";
                leaf "description";
                leaf "admin-state";
                list child {
                    key "Child-Id";
                    leaf "Is-Cool";
                }
            }
        """
        root = FixedSchemaRoot()
        interface = root.add_child(
            'interface',
            key='name',
            fields=['description', 'admin-state']
        )
        child = interface.add_child(
            'child',
            key='Child-Id',
            fields=['Is-Cool']
        )
        return root

    def _fetch_state(self, state, arguments):
        # Retrieve the state from the management server
        """
        2. Recupere el estado del servidor de administración usando state.server_data_store.get_data y la ruta (<ruta>)
        """
        name = arguments.get('name')
        path = build_path('/interface[name={name}]/subinterface[index=*]')
        return state.server_data_store.get_data(path, recursive=True)

    def _populate_data(self, server_data):
        # Populate a data object
        """
        3. Llene un objeto de datos con todos los datos (keys/fields/…) de la rutina show.
        """
        result = Data(self._get_my_schema())
        for interface in server_data.interface.items():
            data = result.interface.create(interface.name)
            data.description = interface.description
            data.admin_state = interface.admin_state
            self._add_children(data, interface.subinterface)
        return result

    def _add_children(self, data, server_data):
        # server_data is an instance of DataChildrenOfType
        for subinterface in server_data.items():
            child = data.child.create(subinterface.index)
            cool_ids = [42, 1337]
            is_cool = subinterface.index in cool_ids
            child.is_cool = strings.bool_to_yes_no(is_cool)

    def _set_formatters(self, data):
        # Add formatter instances
        """
        4. Agregue instancias de Formatter para determinar cómo se formatearán los datos.
        """
        data.set_formatter('/interface', Border(TagValueFormatter(),
                           Border.Above | Border.Below | Border.Between, '='))
        data.set_formatter('/interface/child', Indent(ColumnFormatter(
            ancestor_keys=False, borders=Borders.Header), indentation=2))

    def _print(self, state, arguments, output, **_kwargs):
        # Implement the callback method
        """
        5. Implemente el método de devolución de llamada para pasar la estructura de datos al
        """
        server_data = self._fetch_state(state, arguments)
        result = self._populate_data(server_data)
        self._set_formatters(result)
        output.print_data(result)
