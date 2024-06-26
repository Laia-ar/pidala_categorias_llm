import pandas as pd
import requests
import time
import sys
from datetime import datetime

if (len(sys.argv[1]) < 1 or len(sys.argv[2]) < 1 ):
    exit("Missing command line parameters URL and API_KEY")

# Connection info
# TODO put into a file and .gitignore it
URL = sys.argv[1];
API_KEY = sys.argv[2];

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

# System Prompt and simulated interactions
example_task_prompt = {}
example_assistant_reply = {}

categorias1 = """

Presupuesto y gastos
Elecciones / Campañas electorales
Compras públicas y contratos
Empleo y servidores públicos
Educación
Salud
Desastres y protección civil
Medio ambiente y territorio
Energía y servicios
Militares, policía y crímen
Discriminación
Programas de subsidios
Sanciones, Sentencias y resoluciones
Violaciones a Derechos Humanos
Legislación, reglas y procedimientos
Impuestos y finanzas
Turismo
Vialidad y transporte público
Vivienda
"""

categorias2 = """
Planificación y presupuesto
Campañas electorales
Compras públicas y contratos
Empleo y servidores públicos
Educación
Salud
Desastres y protección civil
Medio ambiente y territorio
Energía y servicios
Criminalidad
Discriminación, acoso y abuso
Programas de subsidios
Justicia
Violaciones a Derechos Humanos
Legislación vigente y normativas
Impuestos
Turismo
Vialidad y transporte público
Vivienda
"""

# system_prompt_task_multi = """Tu trabajo es responder con las 2 categorías más apropiadas para el texto de una solicitud de acceso a la información pública, separadas con |. 

# Las categorías posibles son:  



# Cada solicitud puede pertenecer a dos categorías correspondientes del listado, sin importar el orden de las categorías en el listado.
# Responde "Otros" en el caso de que no corresponda a ninguna categoría.
# Responde "Falta Información" en el caso de que la pregunta no se entienda o haga referencias inexistentes.
# No uses comillas en la respuesta.

# """  

system_prompt_task = """Tu trabajo es responder con el nombre de la categoría más apropiada para el texto de una solicitud de acceso a la información pública. 

Las categorías posibles son:  
"""+categorias2+"""


Incluye una corta justificación para tu respuesta, sin repetir nombres o cosas específicas. Asegúrate de elegir la categoría más apropiada sin cometer errores, teniendo en cuenta la sutileza del significado de cada palabra y la necesidad de que las categorías se compongan de solicitudes consistentes de temas parecidos. Si se pregunta sobre un tema, la categoría debe ser la correspondiente al tema, no algo más abstracto.
Responde "Otros" en el caso de que no corresponda a ninguna categoría.
Responde "Falta Información" en el caso de que la pregunta no se entienda o haga referencias inexistentes.
No uses comillas en la respuesta.

"""  
example_task_prompt[0] = """Solicitud a categorizar: SOLICITO EL NOMBRE DE LOS GRUPOS MUSICALES Y MONTO PAGADO, CONTRATADOS PARA EL EVENTO DE LA COMIDA NAVIDEÑA A LOS TRABAJADORES DEL AYUNTAMIENTO DE PUEBLA EL PASADO 14 DE DICIEMBRE DE 2018 EN EL CENTRO EXPOSITOR, EN EL CASO DE LA SONORA DINAMITA CUANTO COBRO Y COPIA SIMPLE DEL CONTRATO. 
Categoria: """
example_assistant_reply[0] = "Compras públicas y contratos | Justificación: El monto pagado a los grupos musicales es un tema de compra pública"

example_task_prompt[1] = """Solicitud a categorizar: deseo saber las acciones y resultados de el tema de prevención o atención a personas con cáncer así como los presupuestos para estos temas así como los apoyos a organizaciones de la sociedad civil encargadas de estos temas en el estado de puebla así como los datos de contacto de los responsables de este tema asi como los presupuestos si es posible coen comprobatoria y resumen del 2017 y plan de trabajo del 2018
Categoria: """
example_assistant_reply[1] = "Salud. | Justificación: La prevención del cáncer es un tema de salud"

# "Others" example
# Egar: Ajustar, intuyo que puede generar bias (solo considerar cosas ridiculas podria ser consecuencia de este, quizás?)  
example_task_prompt[2] = """Solicitud a categorizar: Solicito una buena receta de mole poblano.
Categoria: """
example_assistant_reply[2] = "Otros. | Justificación: El mole poblano no es tema público"

# User Prompt appends
follow_up_instruction = "Solicitud a categorizar: "
after_prompt = "Categoria: | Justificación:"

# Function to send text via POST request
def send_texts_in_batches(texts, adjuntos, folios, batch_size=5, iteration_delay=0.1, batch_delay=.5, retry_limit=1):
    responses = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_adjuntos = adjuntos[i:i + batch_size]
        batch_folios = folios[i:i + batch_size]
        # print("batch",i,batch_adjuntos)

        for data_instruction, adjunto, folio in zip(batch_texts, batch_adjuntos, batch_folios):
            # print(folio)
            retry_count = 0
            while retry_count < retry_limit:
                # Format prompt
                prompt = follow_up_instruction + data_instruction
                if (len(adjunto) > 1):
                    prompt+= " Adjunto: "+adjunto;
                prompt+= "\n" + after_prompt

                # if (len(adjuntos) > 1):
                #     print(prompt);

                data = {
                    "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                    "messages": [
                    {"role": "system", "content": system_prompt_task},
                    {"role": "user", "content": example_task_prompt[0]},
                    {"role": "assistant", "content": example_assistant_reply[0]},
                    {"role": "user", "content": example_task_prompt[1]},
                    {"role": "assistant", "content": example_assistant_reply[1]},
                    {"role": "user", "content": example_task_prompt[2]},
                    {"role": "assistant", "content": example_assistant_reply[2]},
                    {"role": "user", "content": prompt},
                    ]
                }
                # print(prompt[:100])
                response = requests.post(URL, json=data, headers=headers)  # Include headers
                if response.status_code == 200:
                    response_text = response.json()['choices'][0]['message']['content'].strip()
                    json = response.json()
                    json["prompt"] = prompt[:300]
                    print(json)
                else:
                    response_text = "Error"

                r = response_text.split("|")
                categoria = r[0].replace(".","").strip()
                justificacion = r[1].replace("Justificación: ","").strip()

                # Check if response is in categorias.csv
                if check_response(response_text):
                    print("Folio: "+ folio+" Categoría: " + categoria,"justificación: ",justificacion)
                    responses.append({'folio_unico': folio, 'categoria_probable': categoria,"justificación": justificacion, 'reintentos': retry_count})
                    # print("Text sent successfully for folio:", folio)
                    time.sleep(iteration_delay)
                    break
                else:
                    if retry_count < retry_limit:
                        print("Error: " + response_text)
                        # Re-prompt for incorrect response
                        reprompt = "Incorrecto. " + system_prompt_task + follow_up_instruction + data_instruction + "\n" + after_prompt
                        data["messages"].append({"role": "assistant", "content": response_text})
                        data["messages"].append({"role": "user", "content": reprompt})
                    else:
                        response_text = "*"
                        
                    retry_count += 1

            if retry_count >= retry_limit:
                responses.append({'folio_unico': folio, 'categoria_probable': categoria,"justificación": justificacion, 'reintentos': retry_count})
                print("Text sent with errors for folio:", folio)
                time.sleep(iteration_delay)

        time.sleep(batch_delay)

        # Add a timestamp to avoid overwriting the file. CONS: can't resume. TODO: skip if filename provided on args
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'responses_{timestamp}.csv'

        # Append responses to the CSV for each batch
        response_df = pd.DataFrame(responses)
        response_df.to_csv(filename, mode='a', header=False, index=False)

        # Clear cache
        responses = []

    return responses

# Simple check for incorrect responses
def check_response(response_text):
    return len(response_text) <= 500  # Compare the length of the response against the maximum length of the categories

# Get info from CSV
df = pd.read_csv('preguntas_pnt_puebla_adjuntos.csv')
descriptions = df['descripcion'].tolist()
adjuntos = df['adjuntos_solicitud.contenido'].tolist()

folios = df['folio_unico'].tolist()

# Send texts in batches and get responses
responses = send_texts_in_batches(descriptions, adjuntos, folios)
