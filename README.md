# ViajesAventuraCFerrada
Proyecto ViajesAventura

Sistema modular en Python para la gestión de destinos, paquetes turísticos, usuarios con autenticación segura y reservas, organizado bajo una arquitectura en capas.

## Arquitectura del proyecto

* `src/domain/`: Modelos y reglas de entidad (`Destination`, `TravelPackage`, `User`, `Reservation`).
* `src/business/`: Reglas de negocio, validaciones, cálculo de costos y hashing de contraseñas (`pbkdf2_hmac`).
* `src/persistence/`: Acceso a datos parametrizado con soporte para SQLite (por defecto) y MySQL.
* `src/presentation/`: Interfaz de consola (`main.py`) con interacción en español.

## Requisitos y configuración

1. Tener Python 3.10+ instalado.
2. Copiar `.env.example` a `.env` y ajustar variables si se desea usar MySQL.
3. Si usas `DB_ENGINE=mysql`, instalar `mysql-connector-python`.

## Ejecución

Ejecuta siempre desde la carpeta raíz del proyecto:

```bash
python -m src.presentation.main
```