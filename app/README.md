# Aplicación Flask para Fines Educativos

Esta es una simple aplicación Flask creada para fines educativos. La aplicación muestra una página web con información sobre el contenedor y el pod donde se está ejecutando.

## Prerrequisitos

* Docker

## Cómo Utilizar

1.  **Construir la imagen de Docker:**

    ```bash
    docker build -t flask-app .
    ```

2.  **Ejecutar el contenedor de Docker:**

    ```bash
    docker run -p 8080:8080 --name flask-app-container flask-app
    ```

3.  **Acceder a la aplicación:**

    Abra su navegador web y vaya a `http://localhost:8080`.

## Variables de Entorno

La aplicación utiliza las siguientes variables de entorno para mostrar información sobre el entorno de ejecución:

*   `IMAGE_NAME`: El nombre de la imagen de Docker.
*   `TAG_NAME`: El tag de la imagen de Docker.
*   `POD_NAME`: El nombre del pod de Kubernetes.

Puede establecer estas variables de entorno al ejecutar el contenedor de Docker. Por ejemplo:

```bash
docker run -p 8080:8080 --name flask-app-container -e IMAGE_NAME=flask-app -e TAG_NAME=latest -e POD_NAME=flask-app-pod flask-app
```

## Kubernetes

Esta aplicación está diseñada para ser desplegada en Kubernetes. Puede utilizar la imagen de Docker que ha creado para desplegar la aplicación en un clúster de Kubernetes.
