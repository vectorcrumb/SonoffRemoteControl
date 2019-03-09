# Sonoff Remote Control

Codigo python para controlar un Sonoff Dual R2 de manera remota sin tener que implementar cambios de firmware. El Sonoff debe contar con la version v2.0.1 del firwmare oficial, lo cual puede ser verificado mediante la aplicacion oficial de Sonoff. Las versiones de firmware mas recientes implementan verificacion del certificado SSL, por lo cual no es posible controlarlos sin un cambio de firmware.

Este software consiste de tres partes:
 * Configuracion: El script `sonoff_config.py` se encarga de configurar el Sonoff para dirigirlo al servidor.
 * Servidor: El servidor para controlar los dispositivos Sonoff se encuentra en `sonoff_server.py`. Este script abre un servidor HTTPS y WSS. El dispositivo Sonoff realize un request POST a `/dispatch/device` solicitando la direccion del servidor Websocket. Luego, establece una conexion WSS a `/api/ws`, mediante la cual se comunica, solicitando actualizaciones y enviando periodicamente su estado. Adicionalmente, mediante este canal se implementa el control del dispositivo. Es necesario mantener corriendo este script para poder controlar el Sonoff.
 * Control: Este script contiene una clase, `SonoffController`, la cual se comunica con el servidor HTTPS en la ruta `/state` para controlar los reles.

El script de configuracion y el servidor hacen uso del archivo de configuracion, `config.json`. El contenido de este archivo es el siguiente:

```json
{
    "device": {
        "IP": "10.10.7.1",
        "protocol": "http://"
    },
    "network": {
        "SSID": "<SSID DE RED WIFI AL CUAL CONECTAR EL SONOFF>",
        "password": "<CLAVE DE RED WIFI AL CUAL CONECTAR EL SONOFF>"
    },
    "server": {
        "IP": "<IP DE DISPOSITO DONDE SE EJECUTARA EL SERVIDOR WS Y HTTPS>",
        "port": <PUERTO DONDE ABRIR SERVIDOR WS Y HTTPS (int)>
    },
    "ssl": {
        "cert": "<UBICACION DE CERTIFICADO SSL CON RESPECTO AL SERVIDOR>",
        "key": "<UBICACION DE CLAVE SSL CON RESPECTO AL SERVIDOR>"
    }
}
```
Luego de ejecutar el archivo de configuracion 

## Configurar un Sonoff Dual

 1. Conectar Sonoff a corriente. No es necesario conectar las salidas aun.
 2. El Sonoff comenzara a parpader el LED azul. El patron sera ON - OFF (C) - ON - OFF(L). La C simboliza un tiempo corto y la L un tiempo largo.
 3. Dejar presionado el boton hasta que cambie el patron de parpadeo. Esto debiese demorar alrededor de 7 segundos. El patron nuevo sera ON - OFF (C) 3 veces, seguido de OFF (L).
 4. Volver a dejar presionado el boton hasta que cambie el patron de parpadeo. Esto debiese demorar alrededor de 7 segundos. El patron nuevo sera ON - OFF (C) continuamente. En este estado, el Sonoff inicia un AP Wifi con SSID `ITEAD_10000xxxxx` y clave `12345678`.
 5. Conectarse a AP Wifi.
 6. Ejecutar script de configuracion con `python sonoff_config.py`. El script realizará un GET para obtener el Device ID y API key y actualizará el archivo `config.json`. Luego, enviará un POST para actualizar la configuracion del Sonoff, entregando la direccion nueva del servidor. Luego de recibir el segundo mensaje `REQA`, el Sonoff se encontrara configurado.
 7. El Sonoff volverá a parpadear con el mismo patron que en el paso 2 y cerrará el AP. Seguira parpadeando con este patron hasta establecer una conexion con el servidor.

 ## Ejecutar servidor para Sonoff Dual

 1. (Opcional) Se deben crear certificados SSL para el servidor HTTPS. En Linux, eso se logra mediante el siguiente comando:
 ```bash
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
 ```
 Esto creara un certificado SSL valido por 1 año. Si se ejecuta el comando en el mismo directorio que `sonoff_server.py`, no es necesario actualizar `config.json`.
 2. Ejecutar `python sonoff_server.py`. Esto abrira un servidor HTTPS y WSS en el puerto especificado por `config.json`. El Sonoff se conectará pasado un tiempo (maximo 60 segundos) y luego de una transaccion HTTP para obtener informacion, se conectara al servidor WSS.
 3. El Sonoff pasara de parpadear a permanecer con su luz azul encendida. Esto indica que esta conectado al servidor.

 ## Controlar el Sonoff Dual

Para controlar el Sonoff se puede usar el objeto `SonoffController` en el archivo `sonoff_control.py`. Un ejemplo de como usar esta clase se encuentra en `example.py`. No es recomendable activar y desactivar rapidamente y continuamente los reles, pues el Sonoff se sobrecalienta.
