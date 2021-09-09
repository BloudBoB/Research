"""
Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
"""

import json
import decimal

from lambda_runtime_exception import FaultException


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        raise TypeError(repr(o) + " is not JSON serializable")


def to_json(obj):
    return json.dumps(obj, cls=DecimalEncoder)


class LambdaMarshaller:
    def unmarshal_request(self, request, content_type='application/json'):
        if content_type != 'application/json':
            return request
        try:
            return json.loads(request)
        except Exception as e:
            raise FaultException(FaultException.UNMARSHAL_ERROR, "Unable to unmarshal input: {}".format(str(e)), None)

    def marshal_response(self, response):
        if isinstance(response, bytes):
            return response, 'application/unknown'

        try:
            return to_json(response), 'application/json'
        except Exception as e:
            raise FaultException(FaultException.MARSHAL_ERROR, "Unable to marshal response: {}".format(str(e)), None)
