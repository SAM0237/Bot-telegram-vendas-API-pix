import requests
import mercadopago
import mercadopago.config
import time
import uuid
from datetime import datetime, timedelta, timezone

#checa o status de pagamento de uma ordem

def Pagamento_Concluido(id): #passa o id que será checado como parametro para a função
    
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer APP_USR-xxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    }
    for i in range(90): #realiza uma verificação de 3 min se o pagamento foi ou não concluido
        respostaChecagem = requests.get(f'https://api.mercadopago.com/v1/payments/{id}', headers=headers)
        conteudoResposta = respostaChecagem.json()
        
        if conteudoResposta['status'] == 'approved':
            print("transação aprovada")
            return True
            
        else:
            print("O pagamento está pendente")
            

#checaPAGAMENTO()