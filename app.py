from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from utils import fetch_reply

app = Flask(__name__)

@app.route("/", methods=['POST'])
def sms_reply():
    print(request.form)
    msg = request.form.get('Body')
    sender = request.form.get('From')

    resp = MessagingResponse()
    x,y=fetch_reply(msg,sender)
    if y=="":
    	resp.message(x)
    else:
    	resp.message(y).media(x)
    return str(resp)

 
if __name__ == "__main__":
    app.run(debug=True)