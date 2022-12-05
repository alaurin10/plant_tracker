import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages.create(
  body='Hello Andrew!',
  from_='+16506634922',
  to='+15032130137' 
)

print(message.sid)