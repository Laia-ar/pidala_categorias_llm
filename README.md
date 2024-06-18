# pidala_categorias_llm
 Proyecto de categorización de consultas en colaboración Pidala.info y LAIA

## Instalación
- git clone [repo]
- cd pidala_categorias_llm
- python -v venv venv
- source venv/bin/activate
- pip install -r requirements.txt

## Como usar
```python batch_llama3.py [API_ENDPOINT_URL] [API_KEY]```

Parámetros: 
- El primer parámetro es url del endpoint openAI compatible (normalmente .../v1/chat/completions).
- El segundo parámetro es el API KEY que requiere el endpoint para autentificación

Funcionamiento: batch_llama3.py contiene un script inicial. Ingresar datos del endpoint y api-key (de ser necesario), y el programa tomará los datos del archivo preguntas_pnt_puebla.csv para ingresarlos a una consulta.

 El prompt puede ajustarse según necesidad. 

TODO: Implementar validación

 # Sobre el proyecto

 # Objetivos

 # Resultados

 # Próximos Pasos


