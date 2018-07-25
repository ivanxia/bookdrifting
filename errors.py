import json
import falcon
import httplib
import pymysql

def handle_exceptions(e, req, resp, param):
    resp.status = httplib.INTERNAL_SERVER_ERROR

    if isinstance(e, pymysql.Error):
        msg = "mysql error {0}: {1}".format(type(e).__name__,e)
    elif isinstance(e, Exception):
        print dir(e)
        if 'title' in e:
            msg = e.title + " "+ e.message
        else:
            msg = e.message
    else:
        msg = "unknown error {0}: {1}".format(type(e).__name__,e)

    resp.body = json.dumps({
        "errors": [
            {
                "code": httplib.INTERNAL_SERVER_ERROR,
                "message": msg,
            }
        ]
    })
