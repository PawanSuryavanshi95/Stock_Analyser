from managers.api import Services

class Validator:

    msg = "Third Part API ({}) Gave Invalid Response - {}"
    
    def __init__(self):
        pass

    def validate_alpha_vantage_response(self, res):

        if res.get('Note', None) is not None:
            return {
                'success': False,
                'status': 500,
                'error': self.msg.format(Services.ALPHA_VANTAGE, res.get('Note'))
            }
        
        if res.get('Error Message', None) is not None:
            return {
                'success': False,
                'status': 500,
                'error': self.msg.format(Services.ALPHA_VANTAGE, res.get('Error Message'))
            }

        return {
            'success': True,
        }

    def validate_twelve_data_response(self, res):

        status = res.get('status', None)

        if status == 'error':
            return {
                'success': False,
                'status': 500,
                'error': self.msg.format(Services.TWELVE_DATA, res.get('message'))
            }
        elif status is None:
            return {
                'success': False,
                'status': 500,
                'error': self.msg.format(Services.TWELVE_DATA, "'status' was not found in the Twelve Data response")
            }
        

        return {
            'success': True,
        }