def process_date_time(instance,dataframe):
    """Map combinations of date and time formats to processing configurations."""
    config_map = {
        ('yyyy-mm-dd', 'hh:mm:ss'): {},
        ('yyyy-mm-dd', 'hh mm ss'): {'time_replace': ' '},
        ('yyyy-mm-dd', 'SecOfDay'): {'replace_time': False},
        ('yyyy mm dd', 'hh:mm:ss'): {'date_replace': ' '},
        ('yyyy mm dd', 'hh mm ss'): {'date_replace': ' ', 'time_replace': ' '},
        ('yyyy mm dd', 'SecOfDay'): {'replace_time': False, 'date_replace': ' '},
        ('NoDate', 'hh:mm:ss'): {'replace_date': False},
        ('NoDate', 'hh mm ss'): {'replace_date': False, 'time_replace': ' '},
        ('NoDate', 'SecOfDay'): {'replace_date': False, 'replace_time': False},
    }

    # Get the config based on `instance.date` and `instance.time`, or default to an empty dict
    config = config_map.get((instance.date, instance.time), {})

    # Call `_process_date_time` with the resolved configuration
        
    def _insert_column(column_name, value):
        """Insert a column into the dataframe."""
        try:
            dataframe.insert(0, column=column_name, value=value)
        except Exception as e:
            instance._log_exception(e)

    def _replace_column_values(column_name, old, new):
        """Replace values in a column."""
        try:
            dataframe[column_name] = dataframe[column_name].str.replace(old, new)
        except Exception as e:
            instance._log_exception(e)

    def _trim_data_frame():
        """Trim rows in the dataframe based on a condition."""
        try:
            dataframe = dataframe[start< dataframe['DateTime'] < end]
        except:
            print('Not trimming data frame')
    def _process_date_time(replace_time=True, replace_date=True, date_replace=None, time_replace=None):
        """
        Process the DateTime, Date, and Time columns of the dataframe.
        """
        try:
            dataframe.pop('Time')
        except KeyError:
            print(f"Column 'Time' does not exist. Columns available: {dataframe.columns}")
        except Exception as e:
            instance._log_exception(e)

        _insert_column('DateTime', instance.dtime)

        _trim_data_frame()

        if replace_time:
            _insert_column('Time', instance.dtime_time)
            if time_replace:
                _replace_column_values('Time', ':', time_replace)

        if replace_date:
            _insert_column('Date', instance.dtime_date)
            if date_replace:
                _replace_column_values('Date', '-', date_replace)

        dataframe.pop('DateTime')


        return dataframe

    return _process_date_time(**config)