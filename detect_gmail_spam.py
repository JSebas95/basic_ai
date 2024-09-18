import os.path
import openai

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

local_token_path = os.getenv('LOCAL_TOKEN_PATH') #save the information after the first time
local_path = os.getenv('LOCAL_PATH') # To enter the firs to the email
open_ia_key = os.getenv('OPEN_IA_KEY') #open_ia key

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.

  if os.path.exists(local_token_path):
    creds = Credentials.from_authorized_user_file(local_token_path, SCOPES)


  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          local_path, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:

    # Call the Gmail API
    # service = build('gmail', 'v1', credentials=creds)
    # results = service.users().labels().list(userId='me').execute()
    # labels = results.get('labels', [])

    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()

    if 'messages' in results and results['messages']: # Verifica si existe y no está vacío
      for msg in results['messages']:
        mensaje = service.users().messages().get(userId='me', id=msg['id']).execute()
        print(f"Analizando el correo: {mensaje['snippet']}")
        print(f"El correo electrónico con id {msg['id']} es: {clasificar_email(mensaje['snippet'])}\n")
    else:
      print("No hay mensajes pendientes por leer")

  except HttpError as error:
      # TODO(developer) - Handle errors from gmail API.
      print(f'An error occurred: {error}')


with open(open_ia_key) as f:
  api_key = f.readline().strip()  # Usamos strip() para eliminar saltos de línea

# Inicializa el cliente de OpenAI con la API key leída
openai.api_key = api_key

def obtener_completion(prompt, model="gpt-3.5-turbo"):
  mensaje = [{"role": "user", "content": prompt}]
  completion = openai.chat.completions.create(
    model=model,
    messages=mensaje,
    temperature=0,
  )
  return completion.choices[0].message.content


def clasificar_email(correo):
  """Esta función identifica si un correo electrónico es malicioso o benigno."""

  prompt = f"""Actúa como si fueses el mayor experto en Ciberseguridad y análisis de correos electrónicos del mundo. A continuación te voy a proporcionar un email delimitado por triples comillas simples. Tu tarea es determinar si ese correo electrónico es malicioso (SPAM o Phishing) o Benigno. Para ello, realiza las siguientes acciones:
1. Analiza muy en detalle todo el contenido del correo electrónico
2. Extrae los patrones que consideras sospechosos desde el punto de vista de la seguridad
3. Analiza estos patrones y razona detalladamente el motivo por el que pueden ser maliciosos en el contexto del mensaje completo
4. Determina si el email es malioso o benigno.

La salida que debes proporcionarme debe ser un JSON con las claves que se muestran a continuación. No debes proporcionar nada más como salida.
{{\"clasificacion\":<MALICIOSO o BENIGNO>}}

Email: '''{correo}'''
"""

  return obtener_completion(prompt)

if __name__ == '__main__':
    main()