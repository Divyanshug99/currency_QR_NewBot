import requests
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client-secret.json"

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "newbot-yxrknh"

# -------------------------------------------------------
from pymongo import MongoClient

client = MongoClient("mongodb+srv://test:test@cluster0-wqkyx.mongodb.net/test?retryWrites=true&w=majority")

db = client.get_database('currency_QR_db')
records = db.currency_QR_records

# --------------------------------------------------------

def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

def fetch_reply(msg, session_id):
	push_data={}
	response=detect_intent_from_text(msg,session_id)
	intent_name=response.intent.display_name

	if intent_name == 'currency.convert':
		dict_resp=(dict(response.parameters))
		data_str=currency(dict_resp,push_data)
		if data_str=='':
			data_str="Can you repeat?"
			return data_str, ""

		push_data['intent']=intent_name
		records.insert_one(push_data)

		return data_str, ""

	elif intent_name == 'QR_code':
		
		dict_resp=(dict(response.parameters))
		data_str=qr(dict_resp,push_data)
		if data_str=='':
			data_str="Can you repeat?"	
			return data_str, ""

		push_data['intent']=intent_name
		records.insert_one(push_data)

		return data_str, str(dict(response.parameters).get('url'))
	
	else:
		return response.fulfillment_text, ""

def currency(dict_resp,push_data):
	currency_frm=dict_resp.get('currency-from')
	currency_to=dict_resp.get('currency-to')
	currency_to=currency_to.upper()
	currency_frm=currency_frm.upper()

	push_data['currency-from']=currency_frm
	push_data['currency-to']=currency_to
	
	get_all=dict_resp.get('get_all')
	amount=dict_resp['amount']
	url="https://api.exchangeratesapi.io/latest"
	r=requests.get(url)
	r=r.json()
	if currency_frm == '' or currency_to=='':
		if get_all == '':
			return ''
		else:
			inr=float(r["rates"]["INR"])
			data_str=''
			for frm in r["rates"]:
				data_str+="\n1"+frm+" = "+str(inr/float(r["rates"][frm]))+"INR \n"
			data_str+="\n1 EUR"+" = "+str(float(1/inr))+"INR \n"
			return data_str

	if currency_frm == 'EUR':
		cf=1
	else:
		cf=float(r["rates"][currency_frm])

	if currency_to == 'EUR':
		ct=1
	else:
		ct=float(r["rates"][currency_to])

	rate=ct/cf
	data_str="\n\n1 "+currency_frm+" = "+str(rate)+" "+currency_to+"\n\n"
	if amount != '':
		data_str+="Converted Amount: \n"+str((float(amount)*rate))+" "+currency_to+"\n\n"
	return data_str

def qr(dict_resp,push_data):
	url=dict_resp.get('url')
	push_data['url']=url
	url="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data="+url
	
	push_data['image']=url
	
	return url
