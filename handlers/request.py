from sanic.request import Request as req

class Request(req):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_query_params(self):
        
        params = {}
        for key in list(self.args.keys()):
            params[key] = self.args.get(key).upper()
        
        return params