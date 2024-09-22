#En este caso práctico, se propone al alumno la integración del ChatBot implementando en el caso práctico anterior con el servicio de correo electrónico de Gmail.
#La aplicación debe ser capaz de realizar diferentes funciones sobre los correos electrónicos del usuario. Por ejemplo, debe ser capaz de buscar todos los
# correos electrónicos de un remitente concreto y resumir su contenido

from __future__ import print_function

import os.path
import openai
import panel as pn
pn.extension()

import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


open_ia_key      = os.getenv('OPEN_IA_KEY') #open_ia key
local_json_token = os.getenv('LOCAL_TOKEN_PATH') #save the information after the first time


with open(open_ia_key) as f:
  api_key = f.readline().strip()  # Usamos strip() para eliminar saltos de línea

# Inicializa el cliente de OpenAI con la API key leída
openai.api_key = api_key

#Obtener el modelo chatgpt
def obtener_completion(mensajes, model="gpt-3.5-turbo"):
  respuesta = openai.chat.completions.create(
      model=model,
      messages=mensajes,
      temperature=0, # Este hiperparámetro controla la aleatoriedad del modelo
  )
  return respuesta.choices[0].message.content


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def obtener_correos(remitente_buscar):
    """Proporciona los correos electrónicos del usuario que coincidan con el remitente dado."""
    creds = None
    if os.path.exists(local_json_token):
        creds = Credentials.from_authorized_user_file(local_json_token, SCOPES)

    try:
        correos = """"""
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=10).execute()

        # Verificamos si hay mensajes
        if 'messages' not in results:
            #print("No hay correos no leídos.")
            return

        # Recorremos todos los correos electrónicos
        for msg in results['messages']:
            mensaje = service.users().messages().get(userId='me', id=msg['id']).execute()
            
            # Buscar el campo "From" en los headers
            remitente_encontrado = None
            for cabecera in mensaje['payload']['headers']:
                if cabecera['name'] == 'From':
                    remitente_encontrado = cabecera['value']
                    break  # Salimos del bucle cuando encontramos el "From"

            # Comparamos el remitente con el remitente proporcionado
            if remitente_encontrado and remitente_buscar in remitente_encontrado:
                #print(f"Correo de: {remitente_encontrado}")
                
                # Extraemos el contenido del correo (si está en texto plano)
                if 'parts' in mensaje['payload']:
                    for parte in mensaje['payload']['parts']:
                        if parte['mimeType'] == 'text/plain':
                            contenido = base64.urlsafe_b64decode(parte['body']['data']).decode('utf-8')
                            #print(f"Contenido del correo:\n{contenido}")
                else:
                    # Si no tiene 'parts', el cuerpo puede estar directamente en 'body'
                    contenido = base64.urlsafe_b64decode(mensaje['payload']['body']['data']).decode('utf-8')
                    #print(f"Contenido del correo:\n{contenido}")

                correos += f"""
                                '''
                                Contenido: {contenido}
                                '''
                                """
                return correos

    except HttpError as error:
        print(f'An error occurred: {error}')

#print(obtener_correos("julianarbotero4@gmail.com"))


def collect_messages(_):
    prompt = inp.value_input
    inp.value = ''
    context.append({'role':'user', 'content':f"{prompt}"})
    response = obtener_completion(context)
    try:
      remitente = eval(response)["remitente"]
      accion_solicitada = eval(response)["accion_solicitada"]
      correos = obtener_correos(remitente)
      context.pop(0) # Elimino del contexto la regla inicial
      context.append({'role': 'user', 'content': f"Realiza la siguiente acción: {accion_solicitada} sobre los siguientes correos electrónicos: {correos}"})
      response = obtener_completion(context)
    except:
      pass
    context.append({'role':'assistant', 'content':f"{response}"})
    panels.append(
        pn.Row('User:', pn.pane.Markdown(prompt, width=600)))
    panels.append(
        pn.Row('Assistant:', pn.pane.Markdown(response, width=600, styles={'background-color': '#F6F6F6'})))
    return pn.Column(*panels)


def end_chat(event):
    panels.append(pn.pane.Alert("Chat terminado por el usuario.", alert_type='success'))
    context.append({'role': 'system', 'content':"Despídete del usuario de manera amable y amigable."})
    response = obtener_completion(context)
    context.append({'role':'assistant', 'content':f"{response}"})
    panels.append(
        pn.Row('Assistant:', pn.pane.Markdown(response, width=600, styles={'background-color': '#F6F6F6'})))
    return pn.Column(*panels)

panels = []

context = [ {'role':'system', 'content':
"""
Debes solicitar al usuario que te indique una dirección de correo electrónico que no sea la suya y la tarea que quiere realizar sobre sus correos electrónicos. \
Con esta información, debes generar un JSON con las siguientes claves. No debes generar nada más.
"remitente":<correo electrónico indicado por el usuario>
"accion_solicitada":<descripción de la accion solicitada por el usuario sobre los correos electrónicos del remitente>
"""} ]


inp = pn.widgets.TextInput(value="Hola", placeholder='Introduce texto aqui...')
button_conversation = pn.widgets.Button(name="Chat!")
button_end_chat = pn.widgets.Button(name="Terminar Chat")

button_end_chat.on_click(end_chat)

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation, button_end_chat),
    pn.panel(interactive_conversation, loading_indicator=True, sizing_mode="stretch_both"),
)

pn.serve(dashboard)

#print(obtener_correos("julianarbotero4@gmail.com"))