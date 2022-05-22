# Assignment 2

## MQTT

- I sensori pubblicano su `/seism/{nome_sensore}/raw` letture dall'accelerometro in sample di lunghezza fissata.
- Un nodo centrale pubblica su `/seism/{nome_sensore}/events` qualora un sisma venisse rilevato da precedenti letture ottenute dal topic appena descritto.
