from twilio.rest import Client, TwilioException
from app import app
import requests, random

CODE = None
def _get_twilio_verify_client():
    return Client(
        app.config['TWILIO_ACCOUNT_SID'],
        app.config['TWILIO_AUTH_TOKEN']
    ).verify.services(
        app.config['TWILIO_VERIFY_SERVICE_ID']
    )


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
    CODE = random.randint(1000, 9999)
    data = {
        "outboundSMSMessageRequest": {
            "address": "tel:" + num,
            "senderAddress": "tel:+221772262747",
            "outboundSMSTextMessage": {
                "message": "Merci de recevoir, votre code de verification dans le compte LITA : Ecole d'été 2023 est :"+str(CODE)
            }
        }
    }

    response = requests.post(url, json=data, headers=headers)


def request_verification_token(phone):
    verify = _get_twilio_verify_client()
    try:
        verify.verifications.create(to=phone, channel='sms')
    except TwilioException:
        verify.verifications.create(to=phone, channel='call')

def request_verification_code(token):
    try:
        if CODE == token:
            return True
    except TwilioException:
        return False
    return 'approved'

def check_verification_token(phone, token):
    verify = _get_twilio_verify_client()
    try:
        result = verify.verification_checks.create(to=phone, code=token)
    except TwilioException:
        return False
    return result.status == 'approved'

def check_verification_code(token):
    #verify = _get_twilio_verify_client()
    try:
        if str(CODE) == token:
            return True
    except TwilioException:
        return False
    return 'approved'
