import os
import json
from datetime import datetime
from flask import (Blueprint,
                   render_template)
from ._loader import register_route
from workers import (load_all_workers,
                     WORKERS)
from ag95 import (SinglePlot,
                  ScatterPlotDef,
                  SqLiteDbWrapperServiceClient)

ROUTE_NAME = 'workers_history'
ROUTE_PREFIX = '/workers_history'

# load all workers only once at application startup
load_all_workers()

@register_route
def build():
    bp = Blueprint(ROUTE_NAME, __name__, url_prefix=ROUTE_PREFIX)

    @bp.route("/", methods=["GET", "POST"])
    def route_builder():

        with open('configuration.json', 'r') as f:
            config = json.load(f)

        # get all valid workers to filter out old workers that are still in the db
        # and query the db for relevant data
        valid_workers = ','.join(f'"{_.worker_name}"' for _ in WORKERS)

        with SqLiteDbWrapperServiceClient(port=config['db_ops_port']) as client:
            db_data = client.get_records(table_name='workers_status',
                                         where_statement=f'worker_name IN ({valid_workers})')

        # iterate through db_data and sort data for the plots
        plots_data_per_worker = dict((_.worker_name, []) for _ in WORKERS)
        for record in db_data:

            ID, TIMESTAMP, worker_name, exec_timestamp, exec_return_code, exec_duration_s = record

            plots_data_per_worker[worker_name].append({'datetime': datetime.fromtimestamp(TIMESTAMP),
                                                       'exec_return_code': exec_return_code,
                                                       'exec_duration_s': exec_duration_s})

        # build the required graphs
        final_plots = []
        for worker_name, worker_plot_data in plots_data_per_worker.items():
            if worker_plot_data:
                common_x_axis = [_['datetime'] for _ in worker_plot_data]
                exec_return_code_y_axis = [_['exec_return_code'] for _ in worker_plot_data]
                exec_duration_s_y_axis = [_['exec_duration_s'] for _ in worker_plot_data]

                exec_return_code_fig = SinglePlot(ScatterPlotDef(x_axis=[common_x_axis],
                                                             y_axis=[exec_return_code_y_axis],
                                                             force_show_until_current_datetime=True,
                                                             grey_out_missing_data_until_current_datetime=True))
                exec_duration_s_fig = SinglePlot(ScatterPlotDef(x_axis=[common_x_axis],
                                                                y_axis=[exec_duration_s_y_axis],
                                                                force_show_until_current_datetime=True,
                                                                grey_out_missing_data_until_current_datetime=True))

                # average_exec_time = sum(exec_duration_s_y_axis) / len(exec_duration_s_y_axis)
                # max_exec_time_vs_average_unit = max(exec_duration_s_y_axis) - average_exec_time
                # max_exec_time_vs_average_percentage = max_exec_time_vs_average_unit / average_exec_time * 100
                max_exec_time_vs_average_percentage = 1
                final_plots.append({'worker_name': worker_name,
                                    'return_code_html': exec_return_code_fig.return_html_ScatterPlot(),
                                    'return_code_values': set(exec_return_code_y_axis),
                                    'exec_duration_html': exec_duration_s_fig.return_html_ScatterPlot(),
                                    'exec_time_deviation': round(max_exec_time_vs_average_percentage, 2)})
            else:
                final_plots.append({'worker_name': worker_name,
                                    'return_code_html': 'NO_PLOT_DATA',
                                    'return_code_values': 'NO_PLOT_DATA',
                                    'exec_duration_html': 'NO_PLOT_DATA',
                                    'exec_time_deviation': 0})

        return render_template(template_name_or_list='DataTableFull_template.html',
                               page_title='Workers History',
                               tables=[
                                   {
                                       'table_id': 'ID_0',
                                       'table_title': f"{os.environ['COMPUTERNAME']} -> {config['framework_title']} -> Workers History",
                                       'headers': ['py',
                                                   'Return Code History', 'Return Codes',
                                                   'Exec Time [s] History', 'Exec Time Deviation [%]'],
                                       'restrict_width_columns': str([0, 2, 4]),
                                       'rows': [[
                                           {'text_color': 'black', 'text': _['worker_name'].split('/')[-1]},
                                           {'text_color': 'black', 'text': _['return_code_html']},
                                           {'text_color': 'black', 'text': _['return_code_values']},
                                           {'text_color': 'black', 'text': _['exec_duration_html']},
                                           {'text_color': 'black', 'text': _['exec_time_deviation']},
                                       ] for _ in final_plots],
                                       'order': {'columnID': 4, 'direction': 'desc'},
                                       'pageLength': 50
                                   }
                               ])

    return bp