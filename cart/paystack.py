import json
import requests
from django.conf import settings

def checkout(payload):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers=headers, 
            data=json.dumps(payload)
        )
        response_data = response.json() 

        if response_data.get('status') == True:
            return True, response_data['data']['authorization_url']
        else:
            return False, "Failed to initiate payment, please try again later."
        
    except requests.exceptions.ConnectionError as e:
        return False, e
    
    except requests.exceptions.Timeout as e:
        return False, "Paystack connection Timed out"
    
    except requests.exceptions.HTTPError as e:
        return False, e
    
    except requests.exceptions.RequestException as e:
        return False, e
    
    except Exception as e:
        return False, e
    
