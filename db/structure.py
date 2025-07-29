from ag95 import SqLiteColumnDef

database_structure = [
    {'table_name': 'workers_status',
     'columns_def': [SqLiteColumnDef(column_name='worker_name',
                                     column_type='TEXT'),
                     SqLiteColumnDef(column_name='exec_timestamp',
                                     column_type='INTEGER'),
                     SqLiteColumnDef(column_name='return_code',
                                     column_type='INTEGER'),
                     SqLiteColumnDef(column_name='exec_time_s',
                                     column_type='INTEGER')]}
]
