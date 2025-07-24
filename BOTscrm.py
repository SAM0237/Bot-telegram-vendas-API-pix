import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, )
from CRIAPAGAMENTO import criaPAGAMENTO
from CHECAPAGAMENTO import Pagamento_Concluido
import asyncio
pagamentos = {} #array auxiliar

#função que consome a criarPAGAMENTO para criar especificamente para o usuario
def criaPAGAMENTO_usuario(chatid): 

    pixinformations = criaPAGAMENTO() #cria um pagamento novo e guarda todas as informações
    
    pagamentos[chatid] = {
        'payment_id': pixinformations[0], #pega o qr code do pagamento, e o id de pagamento e atrela com o id do usuario que solicitou o pagamento
        'qrcode': pixinformations[1],
     }
    return pagamentos[chatid]

#Função que pega o id de pagamento gerado e atrelado ao usuario anteriormente e verifica se foi pago
def Pagamento_Concluido_usuario(chatid):
    if chatid not in pagamentos: #verifica se o usuario tem pagamentos pendentes
        print('o usuario não tem pagamentos para realizar')
    idpay = pagamentos[chatid]['payment_id'] 

    #consome a função que ferifica pagamento
    confirma_aprovação = Pagamento_Concluido(id=idpay) 
    
    if confirma_aprovação == True: #Retorna true se o pagamento foi confirmado
        print('pagamento concluido')
        return confirma_aprovação
            
    













#token do bot pego no botfather
TOKEN = "8x6xxxxx970:AAHJixxxxxxxxxxxxxxxx"

#Estados de conversação do bot
MENU, opcao_produto_um, opcao_produto_dois, Pagar, NaoPagar, = range(5)



#configura o logger (para ver oq está acontecendo no bot)
logging.basicConfig(
    format="%(asctime)s - %(name)s %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

#handler para mandar primeira mensagem pro usuario e para mostrar o menu
async def start (update: Update, context: CallbackContext) -> int: # type: ignore
    imgpath = './images/Inforacoes_complementares_menu.png'

    #configuração do teclado de opçoes para inserir no menu
    keyboard = [
        [InlineKeyboardButton('🔓Liberar acesso produto um', callback_data="opcao_produto_um")],
        [InlineKeyboardButton('🔓Liberar acesso produto dois', callback_data="opcao_produto_dois")]    
    ]

    marcacaoDoMenu = InlineKeyboardMarkup(keyboard) #insere o teclado como menú
    #envia uma imagem de saudação inicial para o usuario
    with open(imgpath, 'rb') as imgfile:
        imagem = InputFile(imgfile.read(), filename="Imagem_de_saudacao.jpeg")
    
    #Envia o menú de opçoes        
    if update.message:
        await update.message.reply_photo(imagem) 
        await update.message.reply_text("🟢Itens Disponiveis no menu: ", reply_markup=marcacaoDoMenu) # type: ignore
        
    #Callback para reenviar o menú caso o usuario clique em voltar depois de ter entrado em uma das opções    
    elif update.callback_query:
        chat_id = update.effective_chat.id # type: ignore
        
        
        await context.bot.send_message(chat_id=chat_id, text="🟢Itens Disponiveis no menu: ", reply_markup=marcacaoDoMenu)
    return MENU

#HANDLER para regras de botão
async def botaoupdateH (update: Update, context: CallbackContext) -> int: # type: ignore
    keyboardconfirm = [
        [InlineKeyboardButton('Continuar com a compra 🟢', callback_data="confirmapagamento")],
        [InlineKeyboardButton('Cancelar compra🔴', callback_data="cancelapagamento")] 
    ]
    markupkeyboardconfirm = InlineKeyboardMarkup(keyboardconfirm)
    query = update.callback_query
    await query.answer() # type: ignore

    if query.data == "opcao_produto_um": # type: ignore
        await query.edit_message_text(text="Produto um selecionado ☑️", reply_markup=markupkeyboardconfirm) # type: ignore
        
        return opcao_produto_um
    elif query.data == "opcao_produto_dois": # type: ignore
        await query.edit_message_text(text="Produto dois selecionado ☑️", reply_markup=markupkeyboardconfirm) # type: ignore

        return opcao_produto_dois
    else:
        await query.edit_message_text(text="opção invalida") # type: ignore

#Handler para processo de pagamento
async def pagamento (update: Update, context: CallbackContext) -> int: # type: ignore    
    caminho_pic_agradecimento = './images/poscompra.png' #imagem de agradecimento caso usuario compre

    
    query = update.callback_query #especifica uma query de callback caso usuario deseje cancelar, confirmar... etc...
    #aguarda o usuario iniciar um callback
    await query.answer() # type: ignore

                
    #VERIFICA SE O USUARIO CLICOU EM CONFIRMAR PAGAMENTO
    if query.data == 'confirmapagamento': # type: ignore
        chatid = update.effective_chat.id # type: ignore
        pagamento_criado = criaPAGAMENTO_usuario(chatid=chatid)
        await query.edit_message_text(text='🟢A transação está em andamento... Gerando Chave Pix, por favor aguarde🟢') # type: ignore
        
        await context.bot.send_message(chat_id=chatid, text=f'✔️ Chave Pix copia e cola gerada: \n')
        await context.bot.send_message(chat_id=chatid, text=pagamento_criado['qrcode'])
        try:
            for _ in range(40):
                testepagamento = Pagamento_Concluido_usuario(chatid=chatid) #Chama a funçao que verifica se o pagamento foi pago
                if (testepagamento == True):
                    
                    await context.bot.send_photo(chat_id=chatid, photo=caminho_pic_agradecimento) #Envia uma imagem de agradecimento caso usuario tenha comprado
                    break 
                await asyncio.sleep(2)
        except Exception:
            print('erro ao processar o pagamento enquanto aguardava confirmação')


        return Pagar
    elif query.data == 'cancelapagamento': # type: ignore
        await query.delete_message() # type: ignore
        
        return await start(update, context)
        
        
    else:
        await query.edit_message_text(text="opção invalida") # type: ignore 
        return MENU   




#HANDLER para cancelar
async def cancel (update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(text="operação cancelada") # type: ignore
    return ConversationHandler.END        



#FUNÇÃO principal para corpo do bot
def main():
    app = (
        ApplicationBuilder().token(TOKEN).read_timeout(10).write_timeout(10).concurrent_updates(True).build()
    )

    #HANDLER de conversação para manipular a conversação especificada (junção de todos os handlers)
    conv_h = ConversationHandler(entry_points=[CommandHandler("start", start)], states={MENU: [CallbackQueryHandler(botaoupdateH)], opcao_produto_um: [CallbackQueryHandler(pagamento)], opcao_produto_dois: [CallbackQueryHandler(pagamento)], Pagar: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)], NaoPagar: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)] }, fallbacks=[(CommandHandler("start", start))], )  

    app.add_handler(conv_h)
    app.run_polling()

if __name__ == "__main__":
    main()