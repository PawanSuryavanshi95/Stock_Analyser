class Validator:
    
    def __init__(self):
        pass

    def validate_alpha_vantage_response(self, res):

        if res.get('Note', None) is not None:
            return {
                'success': False,
                'error': res.get('Note')
            }
        
        if res.get('Error Message', None) is not None:
            return {
                'success': False,
                'error': res.get('Error Message')
            }

        return {
            'success': True,
        }

    def validate_twelve_data_response(self, res):

        status = res.get('status', None)

        if status == 'error':
            return {
                'success': False,
                'error': res.get('message', 'No Error Message')
            }
        elif status is None:
            return {
                'success': False,
                'error': "'status' was not found in the Twelve Data response"
            }
        

        return {
            'success': True,
        }