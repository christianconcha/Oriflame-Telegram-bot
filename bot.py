# encoding: utf-8
# This file contains the source code of OriflamianChileBot: a friendly and polite Telegram Bot.
import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config.auth import token, username, password, dns, port, encoding
import cx_Oracle
import os
import logging



cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_6")
#cx_Oracle.init_oracle_client(config_dir=r"C:\oracle\instantclient_19_6\network\admin") 


# Configuración de logging para diplay de mensajes en consola CMD
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('OriflamianChileBot')


def messageProcessor(chat_id, messageToSend):
	context.bot.send_message(
	chat_id=chat_id,
	text=messageToSend)


def queryTextBeautifier(text):
	text = str(text)
	textBeautified = text[2:-3]
	return textBeautified



# Devuelve el UUID de la última boleta o factura generada al socio (Excluye notas de credito y guias de despacho)
def currentBoleta(distributor_number):	
	# try:
		# Parametros de conexión a la DB Oracle de Oriflame:
		#cwd      = os.getcwd() #absolute path to file
		#filename = os.path.abspath('cfg.json') #absolute path to file
	# 	with open('cfg.json', 'r') as file:
	# 		config   = json.load(file)
	# 		username = config['DB']['username']
	# 		password = config['DB']['password']
	# 		dns 	 = config['DB']['dns']
	# 		port 	 = config['DB']['port']
	# 		encoding = config['DB']['encoding']
	# 	logger.info(username)	
	# except ImportError as error:
	# 	print(error)

	try:
		with cx_Oracle.connect(username, password, dns, encoding = encoding) as connection:
			# Imprime version de DB para comprobar la conexion a la DB
			# print ("Version de DB Oracle", connection.version) # Prueba de conexión
			#Abre un cursor a la DB
			cursor = connection.cursor()
			query = """
						SELECT uuid, doc_subtype 
						FROM e_government_invoicing
						WHERE invoice_number = 
						(SELECT * FROM 
						       (SELECT invo_number 
						        FROM orders 
						        WHERE 1 = 1
						        AND invo_amount >= 0
						        AND distributor_number = """  + str(distributor_number) +	"ORDER BY order_date DESC) WHERE rownum = 1)"	

			cursor.execute(query)
			# Trae todo los registros
			registros = cursor.fetchall()
			if registros:
				return registros
			else:
				return None
	except cx_Oracle.Error as error:
		print(error)


def currentDebt(distributor_number):
	try:
		with cx_Oracle.connect(username,password,dns, encoding=encoding) as connection:
			# Imprime version de DB para comprobar la conexion a la DB
			# print ("Version de DB Oracle", connection.version) #Prueba de conexión
			#Abre un cursor a la DB
			cursor = connection.cursor()
			query = 'SELECT first_name, current_debt FROM distributors WHERE distributor_number = ' + distributor_number
			cursor.execute(query)
			# Trae todo los registros
			registros = cursor.fetchall()
			if registros:
				return registros
			else:
				return None
	except cx_Oracle.Error as error:
		print(error)


def start(update, context):
	logger.info('He recibido el comando "start"')
	context.bot.send_message(
		chat_id=update.message.chat_id,
		text="Hola! Soy OriflamianChileBot, estoy aqui para ayudarte."
	)


def hola(update, context):
	logger.info('He recibido el comando "hola"')
	context.bot.send_message(
		chat_id=update.message.chat_id,
		text="Hola, bienvenido!"
	)


def help(update, context):
	logger.info('He recibido el comando "help"')
	respuesta = """Esta es la ayuda de tu bot Oriflame. \n\n**Comandos disponibles:**\n/hola para saludar al bot. \n/deuda 1234 reemplazando 1234 con tu código para ver tu deuda. \n/boleta 1234 reemplazando 1234 con tu código recibirás tu última boleta. \n/factura 1234 reemplazando 1234 con tu código recibirás tu última factura. \n/help para consultar la ayuda. \n /whoisyourdaddy da a conocer al programador del bot"""
	context.bot.send_message(
		chat_id=update.message.chat_id,
		text= respuesta)


def whoisyourdaddy(update, context):
	logger.info('He recibido el comando "whoisyourdaddy"')
	context.bot.send_message(
		chat_id=update.message.chat_id,
		text="Me ha programado Christian Concha 😎")

 
def boleta(update, context):
	logger.info('He recibido el comando "boleta/factura"')
	if not context.args: # Si se ejecutó el comando sin el argunmento #socio:
		respuesta = "Debes colocar el comando /boleta seguido de tu código de empresario, ejemplo: /boleta 1234 🤓"
		context.bot.send_message(
		chat_id=update.message.chat_id,
		text=respuesta)
	else:
		distributor_number = context.args[0]
		uuid = currentBoleta(distributor_number)

		if uuid is None:
			respuesta = "Hmm.. 🧐 Escribiste correctamente tu código?? Si es así, entonces tu boleta aún no está lista, por favor espera unos minutos y vuelve a consultarme... ⏳"
		else:
			respuesta = "Tu último documento electrónico 📃 está disponible en los siguientes enlaces:"
			context.bot.send_message(chat_id=update.message.chat_id, text=respuesta)
			for idx in uuid:
				folio = idx[0]
				doc_subtype = idx[1]
				if doc_subtype == 'RECEIPT':
					respuesta = "http://asp403r.paperless.cl/Facturacion/webservices/VerPDF.jsp?r=96541470&f=" + folio + '&t=39' 
				elif doc_subtype == 'INVOICING':
					respuesta = "http://asp403r.paperless.cl/Facturacion/webservices/VerPDF.jsp?r=96541470&f=" + folio + '&t=33' 
				context.bot.send_message(chat_id=update.message.chat_id, text=respuesta)


def deudaActual(update, context):
	logger.info('He recibido el comando "deuda"')
	if not context.args:
		respuesta = "Debes colocar el comando /deuda seguido del código de empresario, ejemplo: /deuda 3456 😬"
		context.bot.send_message(
		chat_id=update.message.chat_id,
		text=respuesta)
	else:
		distributor_number = context.args[0]
		name_debt = currentDebt(distributor_number)
		if name_debt is None:
			respuesta = "Hmmm parece que escribiste mal tu código de socio?? 🧐 "
		else:
			tupla_nombre_deuda = name_debt[0]
			cons_name = tupla_nombre_deuda[0].title()
			cons_current_debt = tupla_nombre_deuda[1]
			respuesta = cons_name + ", tu deuda actual es de: [$" + str(cons_current_debt) + "] pesos chilenos" + ". Recuerda que puedes pagar en Unired.cl"
		context.bot.send_message(
			chat_id=update.message.chat_id,
			text=respuesta)
	

def echo(update, context):
	logger.info('He recibido el comando "echo"')
	# El bot hace eco a los mensajes que recibe
	update.message.reply_text(update.message.text)
	#context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")




def tarea_repetitiva(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id='971243013', 
                             text='One message every 10 secs')




def main():
	updater = Updater(token=token, use_context=True)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('start', start)) # ('comando Telegram', 'funcion python')
	dispatcher.add_handler(CommandHandler('hola', hola))
	dispatcher.add_handler(CommandHandler('deuda', deudaActual))
	dispatcher.add_handler(CommandHandler('whoisyourdaddy', whoisyourdaddy))
	dispatcher.add_handler(CommandHandler('boleta', boleta))
	dispatcher.add_handler(CommandHandler('factura', boleta ))
	dispatcher.add_handler(CommandHandler('help', help))
	#Handler del 'echo' del bot
	echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
	dispatcher.add_handler(echo_handler)

	# Definiendo un job que envía un texto cada 60seg
	#j = updater.job_queue
	#job_minute = j.run_repeating(tarea_repetitiva, interval=10, first=0)



	#Filtro para cuando desconoce un comando (este handler siempre debe ir de ultimo):
	unknown_handler = MessageHandler(Filters.command, unknown)
	dispatcher.add_handler(unknown_handler)

	# Incia el bot
	updater.start_polling()

	updater.idle()


if __name__ == '__main__':
	main()

