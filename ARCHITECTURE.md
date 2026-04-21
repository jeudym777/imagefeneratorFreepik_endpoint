# Arquitectura del Sistema: Agente Creativo IA para Generación de Campañas Publicitarias

## Visión General

El sistema implementa un agente inteligente basado en IA capaz de generar campañas publicitarias personalizadas integrando tecnologías de procesamiento de lenguaje natural y generación de imágenes. La arquitectura sigue un patrón modular que permite escalabilidad, mantenibilidad y fácil integración con sistemas externos.

## Componentes Principales

### 1. Capa de Orquestación (n8n)

El sistema utiliza n8n como orquestador de flujos de trabajo, proporcionando:

- **Webhook Trigger**: Punto de entrada para solicitudes externas
- **HTTP Request Node**: Comunicación con la API backend a través de REST
- **Manejo de flujos complejos**: Posibilidad de integrar validaciones, transformaciones y ramificaciones

Ventajas: No requiere código adicional, interfaz visual, fácil mantenimiento.

### 2. Backend (FastAPI + Uvicorn)

Servidor de aplicaciones implementado en Python con FastAPI, desplegado en Railway.

**Características:**
- Endpoints RESTful para generación de campañas
- CORS habilitado para comunicación desde diferentes orígenes
- Manejo de sesiones para rastreo de requests
- Validación de entrada mediante modelos Pydantic

**Endpoints principales:**

```
POST /api/generate-campaign
  Input: company_name, ejes, quantity, style, session_id
  Output: csv, images (base64)

GET /api/health
  Verifica estado del servicio

GET/PUT /api/knowledge/{type}
  Gestiona bases de conocimiento (brand, copywriter, designer)

GET /api/styles
  Lista estilos disponibles para generación
```

### 3. Sistema de Agentes IA (RAG - Retrieval Augmented Generation)

**Tres agentes especializados:**

1. **Agente Brand Manager**: Genera estrategia de marca y messaging
2. **Agente Copywriter Creativo**: Produce copy publicitario optimizado
3. **Agente Diseñador Creativo**: Define directrices visuales y de diseño

Cada agente accede a una base de conocimiento personalizada almacenada en archivos Markdown, permitiendo ajustes sin cambios de código.

**Sistema RAG:**
- Carga documentos conocimiento al iniciar aplicación
- Contexto incorporado en prompts de OpenAI
- Actualizaciones dinámicas mediante endpoints PUT

### 4. Integraciones Externas

#### OpenAI API (GPT-4o-mini)

- Generación de copy publicitario basado en contexto RAG
- Creación de prompts para generación de imágenes
- Procesamiento de consultas complejas de marketing

#### Freepik AI

- Generación de imágenes a partir de prompts textuales
- Soporte para 1-5 imágenes por campaña
- Control de costos mediante limitación de cantidad

#### DuckDuckGo Search

- Búsqueda web para información adicional sobre empresas
- Enriquecimiento de contexto de la campaña

### 5. Frontend (HTML5 + Vanilla JavaScript)

Interfaz web responsiva para interacción directa con el sistema:

**Características:**
- Formulario de generación de campañas
- Modal de 3 pestañas para edición de bases de conocimiento
- Descarga automática de resultados en ZIP
- Actualización real de archivos de conocimiento

**Tecnologías:**
- HTML5 semántico
- CSS3 con variables personalizadas
- JavaScript vanilla (sin frameworks)
- Font Awesome 6.4.0 para iconografía

### 6. Almacenamiento y Persistencia

**Bases de Conocimiento (.md files):**
```
knowledge/
  ├── brand_info.md
  ├── copywriting_guidelines.md
  └── design_guidelines.md
```

Formato: Markdown para facilitar edición manual y control de versiones

## Flujo de Datos

### Flujo 1: Generación de Campaña (desde UI)

```
Frontend Form
    ↓
/api/generate-campaign (POST)
    ↓
FastAPI Backend
    ├→ Load RAG Context (knowledge/*.md)
    ├→ Call OpenAI (generar copy + prompts imagen)
    ├→ Call Freepik API (generar imágenes)
    └→ Generate CSV Report
    ↓
Response (CSV + Base64 Images)
    ↓
Browser (descarga ZIP)
```

### Flujo 2: Generación de Campaña (desde n8n)

```
n8n Webhook
    ↓
HTTP Request → /api/generate-campaign
    ↓
FastAPI Backend
    ├→ Authentication & Validation
    ├→ RAG Processing
    ├→ AI Generation
    └→ Image Creation
    ↓
Response JSON (campaign data)
    ↓
n8n Workflow Continuation
```

### Flujo 3: Actualización de Bases de Conocimiento

```
Frontend Modal
    ↓
PUT /api/knowledge/{type}
    ↓
Backend:
  ├→ Valida tipo (brand|copywriter|designer)
  ├→ Actualiza archivo .md
  ├→ Recarga contexto RAG
  └→ Responde OK
    ↓
Frontend: Confirma actualización
```

## Tecnología Stack

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Orquestación | n8n | Latest |
| Backend | FastAPI | 0.104+ |
| Runtime | Python | 3.10+ |
| Servidor | Uvicorn | 0.24+ |
| Hosting | Railway.app | - |
| Frontend | HTML5/CSS3/JS | ES6+ |
| IA | OpenAI GPT-4o-mini | Latest |
| Imágenes | Freepik AI | v1 |
| Búsqueda | DuckDuckGo | - |

## Configuración de Despliegue

### Environment Variables

```
OPENAI_API_KEY=sk-proj-...
FREEPIK_API_KEY=FPSX-...
PORT=8000
```

### Arquitectura de Deployment

```
GitHub Repository
    ↓
Auto-Deploy Trigger
    ↓
Railway.app:
  ├→ Pull Code
  ├→ Build Docker Image
  ├→ Install Dependencies
  └→ Run Uvicorn on Port 8000
    ↓
Public Domain: imagefeneratorfreepikendpoint-production.up.railway.app
```

## Seguridad y Validación

1. **Input Validation**: Esquemas Pydantic para todas las entradas
2. **API Keys**: Almacenadas en variables de entorno (no en código)
3. **Rate Limiting**: Cantidad máxima de imágenes limitada a 5 por petición
4. **Error Handling**: Respuestas JSON estructuradas con códigos HTTP apropiados
5. **CORS**: Configurado para producción

## Escalabilidad y Mantenimiento

### Puntos de Extensión Futuros

1. **Base de datos**: Reemplazar archivos .md con PostgreSQL
2. **Caché**: Implementar Redis para respuestas frecuentes
3. **Autenticación**: Agregar JWT para control de acceso
4. **Analytics**: Logging centralizado y dashboards
5. **A/B Testing**: Múltiples versiones de prompts con tracking

### Monitoreo

- Health check en `/api/health`
- Logs en Railway Dashboard
- Error tracking integrado

## Documentación Adicional

- Guía de configuración: Ver `SETUP.md`
- Integración n8n: Ver `N8N_WORKFLOW_README.md`
- API Reference: Swagger en `/docs`

## Conclusión

La arquitectura propuesta balancean flexibilidad y simplicidad, permitiendo rápida iteración mientras mantiene calidad de producción. La separación modular de responsabilidades facilita futuras integraciones y mejoras sin impacto en componentes existentes.
