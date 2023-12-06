import requests, random

CODE = None


def get_oauth_token():
    url = 'https://api.orange.com/oauth/v3/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic UzRLN0dRZklXSnJxMExvU0VualBuQVN2VktDekl4UTM6SXRreXpjQ3Nvb1haYlJWMQ=='
    }

    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, data=data, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract and return the access token from the JSON response
        return response.json().get('access_token')
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")
        return None


def sms(num):
    access_token = get_oauth_token()

    url = 'https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B221772262747/requests'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token  # Add a space after 'Bearer'
    }
    global CODE
    CODE = str(random.randint(1000, 9999))
    data = {
        "outboundSMSMessageRequest": {
            "address": "tel:" + num,
            "senderAddress": "tel:+221772262747",
            "outboundSMSTextMessage": {
                "message": "Merci de recevoir, votre code de verification dans le compte LITA : Ecole d'été 2023 est :" + CODE
            }
        }
    }

    response = requests.post(url, json=data, headers=headers)

def code():

    return CODE

def request_verification_code(cd, toke):
    try:
        if str(toke) == str(cd):
            flash('Verification réussie', 'success')
            return True
        else:
            flash('Code de vérification invalide', 'danger')
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False



from flask import flash


def check_verification_code(cd, toke):
    try:
        if str(toke) == str(cd):
            #flash('Verification réussie', 'success')
            return True
        else:
            #flash('Code de vérification invalide', 'danger')
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
