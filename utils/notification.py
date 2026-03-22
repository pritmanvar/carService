import config
import json
from django.core.mail import send_mail, BadHeaderError
from utils.utils import CommonResponse
from smtplib import SMTPException
# from twilio.rest import Client
import requests

# ****************************************************** 2Factor sms sender ******************************************************


class twoFactor():

    def send(self, phoneNumber):
        try:
            smsOtp = requests.get(("https://2factor.in/API/V1/{api}/SMS/:+91{number}/AUTOGEN3/:otp_template_name").format(
                api=config.settings.SMSAPI, number=str(phoneNumber)))
            responseTxt = smsOtp.text
            json_acceptable_string = responseTxt.replace('"', "\"")
            smsResData = json.loads(json_acceptable_string)
            if smsResData["Status"] == "Error":
                return CommonResponse(200, "True", 0, "", Message=smsResData["Details"])
            return CommonResponse(200, "False", 0, "", Message="SMS sent successfully.")
        except Exception as e:
            return CommonResponse(200, "True", 0, "", Message=str(e))

    def verify(self, phoneNumber, OTP):
        verifySmsOtp = requests.get(("https://2factor.in/API/V1/{api}/SMS/VERIFY3/91{phone_number}/{otp_entered_by_user}").format(
            api=config.settings.SMSAPI, phone_number=phoneNumber, otp_entered_by_user=OTP))
        responseTxt = verifySmsOtp.text
        json_acceptable_string = responseTxt.replace('"', "\"")
        smsResData = json.loads(json_acceptable_string)
        if smsResData['Details'] == "OTP Matched":
            return True
        return False

# ******************************************************  email sender ******************************************************


class Email():
    def send(self, subject, message, recipient_list):
        try:
            emailOtp = send_mail(
                subject,       # subject
                message,  # message
                config.settings.EMAIL_HOST_USER,    # from_email
                recipient_list           # recipient_list
            )
            return CommonResponse(200, "False", 0, "", Message="Email Sent Successfully.")

        except BadHeaderError as e:              # If mail's Subject is not properly formatted.
            print(e)
            return CommonResponse(400, "True", 0, "", Message="Invalid Header Found.")

        except SMTPException as e:          # It will catch other errors related to SMTP.
            print(e)
            return CommonResponse(400, "True", 0, "", Message='There Was an Error Sending an Email.' + str(e))
        except Exception as e:
            print(e)
            return CommonResponse(500, "True", 0, "", Message="Failure In Sending Mail!")


# ******************************************************  whatsapp message sender ******************************************************

# def send_whatsapp_notification(number, message):
#     account_sid = config.settings.TWILIO_ACCOUNT_SID
#     auth_token = config.settings.TWILIO_AUTH_TOKEN
#     client = Client(account_sid, auth_token)

#     message = client.messages.create(
#         from_='whatsapp:+14155238886',
#         body=message,
#         to=('whatsapp:+91{}').format(number)
#     )