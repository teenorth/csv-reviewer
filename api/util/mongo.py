

def push_pull_to_array(update_data, field, values):
    if not values:
        return

    if isinstance(values, dict):
        if 'push' in values:
            push_values = values['push']
            update_data['$push'] = {field: {'$each': push_values}}
        if 'pull' in values:
            pull_values = values['pull']
            update_data['$pullAll'] = {field: pull_values}
    else:
        update_data['$push'] = {field: {'$each': [values]}}
