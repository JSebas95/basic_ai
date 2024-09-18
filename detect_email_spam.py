import openai

# Abre el archivo y lee la API key
with open("") as f:
    api_key = f.readline().strip()  # Usamos strip() para eliminar saltos de línea

# Inicializa el cliente de OpenAI con la API key leída
openai.api_key = api_key

def obtener_completion(prompt, model="gpt-3.5-turbo"):
  mensaje = [{"role": "user", "content": prompt}]
  completion  = openai.chat.completions.create(
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


correo1 = """Hello Dear. I have a proposition for you, this however is not mandatory nor will I in any manner compel you to honor against your will.Let me start by introducing myself. I am  Mr Author Magnus, manager crew team. I have a mutual beneficial business suggestion for you and a very Important
 matter that we both had to engage in.

1. Can you handle the project?

2. Can I give you this trust ?

3. Can we work together as partner?

Absolute confidentiality is required from you.Besides I will use my connection to get some documents to back up the fund so that the fund can not be question by any authority. More information await you in my next response to your email.

Treat as urgent.

Yours Sincerely

Author Magnus."""


correo2 = """Hola Santiago:

Hay una nueva respuesta a "Kali Linux en Hyper-V" en tu curso "Curso completo de Hacking Ético y Ciberseguridad"

Utiliza el botón de abajo para ver la respuesta e indicar si ha sido útil. Allí encontrarás un enlace para "dejar de seguir" si prefieres no recibir notificaciones de respuestas futuras."""

print(clasificar_email(correo1))