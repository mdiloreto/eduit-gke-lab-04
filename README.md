# Laboratorio de CI/CD: Despliegues Blue-Green y Canary en GKE

## Introducción

Este proyecto es un laboratorio educativo diseñado para demostrar dos estrategias de despliegue avanzadas: **Blue-Green** y **Canary**, utilizando una aplicación Flask simple, Google Cloud Build para la Integración y Entrega Continuas (CI/CD), y Google Kubernetes Engine (GKE) como plataforma de orquestación.

La aplicación web muestra información básica sobre el entorno en el que se ejecuta, incluyendo el nombre del Pod y la versión de la aplicación, lo que permite visualizar fácilmente qué versión está sirviendo el tráfico.

---

## Estructura del Repositorio

El repositorio está organizado para separar claramente la aplicación de los manifiestos de despliegue para cada estrategia.

```
/
├── app/                    # Código fuente de la aplicación Flask
│   ├── static/             # Archivos estáticos (CSS, imágenes)
│   ├── templates/          # Plantillas HTML de Flask
│   ├── app.py              # Lógica principal de la aplicación
│   ├── Dockerfile          # Define cómo construir la imagen de la aplicación
│   └── requirements.txt    # Dependencias de Python
│
├── Manifests-blue-green/   # Manifiestos de Kubernetes para el despliegue Blue-Green
│   ├── deployment.yaml     # Despliegue para la versión "blue" (v1)
│   ├── deployment-v2.yaml  # Despliegue para la versión "green" (v2)
│   ├── service.yaml        # Servicio para exponer la versión "blue"
│   └── service-v2.yaml     # Servicio para exponer la versión "green"
│
├── Manifests-canary/       # Manifiestos de Kubernetes para el despliegue Canary
│   ├── deployment.yaml     # Despliegue principal (v1)
│   ├── deployment-v2.yaml  # Despliegue "canary" (v2)
│   ├── service.yaml        # Servicio para el despliegue principal
│   ├── service-v2.yaml     # Servicio para el despliegue "canary"
│   └── ingress.yaml        # Ingress para distribuir el tráfico entre las versiones
│
├── cloudbuild-blue-green.yaml # Pipeline de Cloud Build para la estrategia Blue-Green
└── cloudbuild-canary.yaml     # Pipeline de Cloud Build para la estrategia Canary
```

---

## Prerrequisitos

Antes de comenzar, asegúrate de tener lo siguiente:

1.  **Proyecto de Google Cloud:** Un proyecto activo con la facturación habilitada.
2.  **SDK de Google Cloud (`gcloud`):** Instalado y autenticado en tu máquina local.
3.  **APIs Habilitadas:** Asegúrate de que las siguientes APIs estén habilitadas en tu proyecto:
    *   Google Kubernetes Engine (GKE) API
    *   Cloud Build API
    *   Artifact Registry API
4.  **Repositorio en Artifact Registry:** Un repositorio de tipo Docker para almacenar tus imágenes. 
5.  **Clúster de GKE:** Un clúster de GKE funcional.
6.  **Permisos:** La cuenta de servicio de Cloud Build (`[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`) debe tener los roles necesarios para interactuar con GKE (`Kubernetes Engine Developer`) y Artifact Registry (`Artifact Registry Writer`).
7.  **(Solo para Canary) Ingress Controller:** Un controlador de Ingress como NGINX debe estar instalado en tu clúster de GKE para que el manifiesto `ingress.yaml` funcione.

---

## Configuración

Ambos archivos `cloudbuild-*.yaml` contienen variables de sustitución que debes adaptar a tu entorno. Modifica las siguientes variables al principio de cada archivo:

-   `_REGION`: La región de tu repositorio de Artifact Registry (ej. `us-central1`).
-   `_REPO`: El nombre de tu repositorio en Artifact Registry.
-   `_CLUSTER`: El nombre de tu clúster de GKE.
-   `_ZONE`: La zona en la que se encuentra tu clúster de GKE (ej. `us-central1-c`).

## Estrategias de Despliegue

A continuación se detalla cómo ejecutar cada pipeline de despliegue.

### 1. Despliegue Blue-Green

**Concepto:** Esta estrategia reduce el riesgo y el tiempo de inactividad al mantener dos entornos de producción idénticos: "Blue" (la versión estable actual) y "Green" (la nueva versión). El tráfico se dirige al entorno Blue. Una vez que el entorno Green ha sido probado y verificado, el tráfico se conmuta del entorno Blue al Green. Esto hace que la reversión (rollback) sea tan simple como volver a dirigir el tráfico al entorno Blue.

**Pipeline (`cloudbuild-blue-green.yaml`):**

1.  **Construye la Imagen:** Crea la imagen Docker de la aplicación a partir del `Dockerfile`.
2.  **Publica la Imagen:** Sube la imagen a tu repositorio de Artifact Registry.
3.  **Actualiza Manifiestos:** Reemplaza el placeholder `IMAGE_URL` en `deployment.yaml` y `deployment-v2.yaml` con la URL de la imagen recién construida.
4.  **Despliega Ambas Versiones:**
    *   Aplica `deployment.yaml` y `service.yaml` para crear el entorno **Blue** (v1).
    *   Aplica `deployment-v2.yaml` y `service-v2.yaml` para crear el entorno **Green** (v2).

**Ejecución:**

Para iniciar el pipeline de Blue-Green, ejecuta el siguiente comando desde la raíz del repositorio:

```bash
gcloud builds submit --config cloudbuild-blue-green.yaml .
```

**Verificación:**

Después de la ejecución, obtén las IPs externas de ambos servicios:

```bash
kubectl get services
```

Verás dos servicios con IPs de LoadBalancer diferentes, `flask-app` (Blue) y `flask-app-v2` (Green). Puedes acceder a ambas para verificar que funcionan correctamente. Para completar el "switch", normalmente se modificaría el servicio principal para que apunte a los pods de la versión v2.

### 2. Despliegue Canary

**Concepto:** Esta estrategia consiste en liberar una nueva versión de la aplicación a un pequeño subconjunto de usuarios antes de liberarla para todos. Esto permite probar la nueva versión en un entorno de producción real con un impacto limitado en caso de errores.

**Pipeline (`cloudbuild-canary.yaml`):**

1.  **Construye y Publica la Imagen:** Similar al pipeline anterior.
2.  **Actualiza Manifiestos:** Reemplaza `IMAGE_URL` en ambos archivos de despliegue.
3.  **Despliega Ambas Versiones:** Aplica los despliegues y servicios para la v1 y la v2 (canary).
4.  **Aplica el Ingress:** Despliega el manifiesto `ingress.yaml`. Este recurso está configurado para dirigir la mayor parte del tráfico (ej. 80%) a la versión estable y una pequeña porción (ej. 20%) a la versión canary.

**Ejecución:**

Para iniciar el pipeline de Canary, ejecuta:

```bash
gcloud builds submit --config cloudbuild-canary.yaml .
```

**Verificación:**

1.  Obtén la dirección IP del Ingress:

    ```bash
    kubectl get ingress
    ```

2.  Accede a la dirección IP del Ingress varias veces desde tu navegador (o usando `curl`). Notarás que a veces ves la versión `v1.0.0` y otras veces la `v2.0.0`, según la distribución de peso configurada en `ingress.yaml`.

Para aumentar gradualmente el tráfico a la versión canary, puedes modificar el valor de `canary-weight` en `Manifests-canary/ingress.yaml` y volver a aplicar el manifiesto con `kubectl apply -f Manifests-canary/ingress.yaml`.
