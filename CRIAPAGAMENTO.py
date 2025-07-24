import requests
import mercadopago
import mercadopago.config
import time
import uuid
from datetime import datetime, timedelta, timezone


def criaPAGAMENTO():
    sdk = mercadopago.SDK("APP_USR-xxxxxxxxxxxxxxxxxxxxxxxxxxxx") #CHAVE DO MERCADO PAGO RECEBEDOR

    uid = str(uuid.uuid4())
    
    
    email = f"email@{uuid.uuid4()}.com"
    external_ref = f"pedido_{uuid.uuid4()}"

    request_options = mercadopago.config.RequestOptions()
    #Configura o pagamento que será gerado. Valores, metodo de pagamento etc...
    request_options.custom_headers = {
        'x-idempotency-key': uid,
    }

    payment_data = {
        "transaction_amount": 100,
        "payment_method_id": "pix",
        "external_reference": external_ref,    
        "payer": {
            "email": email,
        }
    }

    payment_response = sdk.payment().create(payment_data, request_options) 
    resposta = payment_response['response'] #pega a resposta da criação do pagamento
    idpay = resposta['id'] #filtra somente o ID de pagamento
    qrcodepix = resposta['point_of_interaction']['transaction_data']['qr_code'] #Filtra o QR code copia e cola
    id_qrcode = [idpay, qrcodepix] #guarda ambos em uma lista
    

    print("o id de pagamento é: ", idpay)
    print('o qr code para pagamento é: ', qrcodepix)
    
    return id_qrcode
    #retorna ambos
criaPAGAMENTO()





