# Sonoff Remote Control

Codigo python para controlar un Sonoff Dual R2 de manera remota sin tener que implementar cambios de firmware. Este programa puede controlar un Sonoff Dual con version de firmware mayor a v2.0.1, lo cual puede ser verificado mediante la aplicacion oficial de Sonoff. Si el Sonoff Dual viene con el firmware v2.0.1 o menor, usar el el programa en la rama `master`.

Este software consiste de tres partes:
 * Configuracion: El script `sonoff_config.py` se encarga de configurar el Sonoff para dirigirlo a la red wi-fi.
 * Servidor: El servidor para controlar el dispositivo Sonoff se encuentra en `/node_server/index.js`. Este programa corre con Node.JS y abre un servidor WS y HTTP. Mediante un POST a `/state` se pude controlar el estado del Sonoff, el cual actua como un servidor Websockets para el server Node. Es necesario mantener corriendo este script para poder controlar el Sonoff, sin embargo se puede reiniciar para reconectar el dispositivo
 * Control: Este script contiene una clase, `SonoffController`, la cual se comunica con el servidor HTTP en la ruta `/state` para controlar los reles.

El script de configuracion y el servidor hacen uso del archivo de configuracion, `config_lan.json`. El contenido de este archivo es el siguiente:

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
        "IP": "<IP vacia>",
        "port": <Puerto vacio>
    }
}
```
Dentro de `server` es necesario poner una IP no asignada y un puerto arbitrario, pues se busca forzar el Sonoff a modo WLAN (donde no ha podido establecer comunicacion con ningun servidor Websockets).

## Configurar un Sonoff Dual

 1. Conectar Sonoff a corriente. No es necesario conectar las salidas aun.
 2. El Sonoff comenzara a parpader el LED azul. El patron sera ON - OFF (C) - ON - OFF(L). La C simboliza un tiempo corto y la L un tiempo largo.
 3. Dejar presionado el boton hasta que cambie el patron de parpadeo. Esto debiese demorar alrededor de 7 segundos. El patron nuevo sera ON - OFF (C) 3 veces, seguido de OFF (L).
 4. Volver a dejar presionado el boton hasta que cambie el patron de parpadeo. Esto debiese demorar alrededor de 7 segundos. El patron nuevo sera ON - OFF (C) continuamente. En este estado, el Sonoff inicia un AP Wifi con SSID `ITEAD_10000xxxxx` y clave `12345678`.
 5. Conectarse a AP Wifi.
 6. Ejecutar script de configuracion con `python sonoff_config.py`. El script realizará un GET para obtener el Device ID y API key y actualizará el archivo `config_lan.json`. Luego, enviará un POST para actualizar la configuracion del Sonoff, entregando la direccion vacia del servidor y las credenciales de la red wifi. Luego de recibir el segundo mensaje `REQA`, el Sonoff se encontrara configurado. Este ultimo mensaje deberá responder `{"error":0}` para confirmar que no tiene errores.
 7. El Sonoff volverá a parpadear con el mismo patron que en el paso 2 y cerrará el AP. Seguirá parpadeando con este patron hasta establecer una conexion con el servidor.

 ## Ejecutar servidor para Sonoff Dual
 1. Determinar IP del Sonoff en la red wifi a la cual se conecto. Cambiar `.device.IPwifi` en `config_lan.json`.
 2. Entrar a carpeta `/node_server` e instalar paquetes mediante `npm install`.
 3. Esperar 60 segundos antes de iniciar el servidor. Esto permite que el Sonoff entre a modo WLAN y pueda ser controlado por el node_server.
 4. Ejecutar `npm run start` o `node index.js`. Esto abrira un servidor HTTP y WS en el puerto especificado al comienzo del programa. El Sonoff se conectará pasado un tiempo (maximo 60 segundos) al servidor WS.
 5. El Sonoff permanecera parpadeando dos veces seguido de una pausa larga.

 ## Controlar el Sonoff Dual

Para controlar el Sonoff se puede usar el objeto `SonoffController` en el archivo `sonoff_control.py`. Un ejemplo de como usar esta clase se encuentra en `example.py`. No es recomendable activar y desactivar rapidamente y continuamente los reles, pues el Sonoff se sobrecalienta.

En caso de alejar el Sonoff de la red wifi a la cual se encuentre conectada, sera necesario reiniciar el servidor Node. No es necesario reinicar el Sonoff ni esperar, pues ya estara en modo WLAN.
