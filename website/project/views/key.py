from framework import request
from framework.auth import get_current_user
from ..decorators import must_be_valid_project, must_be_contributor
from ..model import ApiKey
from .node import _view_project


@must_be_valid_project # returns project
@must_be_contributor # returns user, project
def get_node_keys(*args, **kwargs):
    node_to_use = kwargs['node'] or kwargs['project']
    return {
        'keys' : [
            {
                'key' : key._id,
                'label' : key.label,
            }
            for key in node_to_use.api_keys
        ]
    }

@must_be_valid_project # returns project
@must_be_contributor # returns user, project
def create_node_key(*args, **kwargs):

    # Generate key
    api_key = ApiKey(label=request.form['label'])
    api_key.save()

    # Append to node
    node_to_use = kwargs['node'] or kwargs['project']
    node_to_use.api_keys.append(api_key)
    node_to_use.save()

    # Return response
    return {'response' : 'success'}, 201

@must_be_valid_project # returns project
@must_be_contributor # returns user, project
def revoke_node_key(*args, **kwargs):

    # Load key
    api_key = ApiKey.load(request.form['key'])

    # Remove from user
    node_to_use = kwargs['node'] or kwargs['project']
    node_to_use.api_keys.remove(api_key)
    node_to_use.save()

    # Send response
    return {'response' : 'success'}

@must_be_valid_project # returns project
@must_be_contributor # returns user, project
def node_key_history(*args, **kwargs):

    api_key = ApiKey.load(kwargs['kid'])
    auth = kwargs['auth']
    node_to_use = kwargs['node'] or kwargs['project']

    rv = {
        'key' : api_key._id,
        'label' : api_key.label,
        'route' : '/settings',
        'logs' : [
            {
                'lid' : log._id,
                'nid' : log.node__logged[0]._id,
                'route' : log.node__logged[0].url,
            }
            for log in api_key.nodelog__created
        ]
    }

    rv.update(_view_project(node_to_use, auth))
    return rv