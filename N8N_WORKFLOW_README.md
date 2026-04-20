# n8n Workflow - CreativoAgent Campaign Generator

Workflow simple para integrar tu API de Railway con n8n.

## Pasos para importar:

1. **Abre n8n** → click en `+` (New Workflow)
2. **Menu → Import from file**
3. Selecciona `n8n_workflow.json` (o copia el JSON)
4. Click **Import**

## Flujo del Workflow:

```
Webhook (POST /generate-campaign) 
    ↓
HTTP Request → Railway API
    ↓
Respuesta (CSV + imágenes en base64)
```

## Prueba rápida (cURL):

```bash
curl -X POST "http://localhost:5678/webhook/generate-campaign" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Mi Marca",
    "ejes": "diversión;color;innovación",
    "quantity": 2,
    "style": "cartoon"
  }'
```

## Request esperado:

```json
{
  "company_name": "string",        // Nombre de la empresa
  "ejes": "string",                // Ejes temáticos (separados por ;)
  "quantity": number,              // Cantidad de imágenes (1-20)
  "style": "string",               // Estilo (photo, cartoon, 3d, etc.)
  "session_id": "string"           // Opcional
}
```

## Respuesta:

```json
{
  "csv": "Número,Frase Publicitaria,Prompt de Imagen,Estilo,Archivo\n1,Frase...",
  "images": [
    {
      "filename": "imagen_01.png",
      "b64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
  ]
}
```

## Configuración opcional en n8n:

- **Auth**: Si quieres proteger el webhook, añade un **API Key header**
- **Split en batches**: Si necesitas procesar múltiples requests en paralelo
- **Error handling**: Añade nodos para reintentos si la API falla

## Para producción:

- Activa el workflow (toggle arriba derecho)
- Configura notificaciones de error (Email, Slack, etc.)
- Monitorea ejecuciones en History

¡Listo! Ya puedes llamar al webhook desde cualquier lugar (Zapier, Make, apps, etc.) y ejecutar el workflow completo.
