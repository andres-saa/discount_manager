# Backend - FastAPI (Cuponera Salchimonster)

API para gestión de descuentos, cuponeras y canje de códigos. **Archivos JSON locales** en `data/` como almacenamiento; sedes y menús se sincronizan cada 10 minutos desde el API externo.

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Configuración

Los datos se almacenan en `data/*.json`. Las sedes y menús se sincronizan desde el API externo. No es necesaria configuración adicional para desarrollo.

## Ejecución

```bash
uvicorn main:app --reload
```

La API estará en `http://127.0.0.1:8000`. Documentación interactiva en `/docs`.

## Datos (JSON local)

Archivos en `data/`: `sites.json`, `menus/site_*.json`, `discounts.json`, `folders.json`, `cuponeras.json`, `cuponera_usage.json`, `cuponera_users.json`. Sedes y menús se sincronizan cada 10 min desde `https://backend.salchimonster.com/...`.

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /sites | Lista sedes |
| GET | /menus/site/{site_id} | Menú de una sede |
| GET/POST/PATCH/DELETE | /discounts, /discounts/{id} | CRUD descuentos (validación de scope vs menús) |
| GET/POST/PATCH/DELETE | /cuponeras, /cuponeras/{id} | CRUD cuponeras |
| GET/POST/DELETE | /cuponeras/{id}/users | Usuarios de una cuponera (código generado al registrar) |
| GET | /redeem?code=XXX&date=YYYY-MM-DD&record_use=true | Canjear código: devuelve descuentos del día y opcionalmente registra un uso |

## Cuponera

- Una cuponera tiene **calendario**: cada fecha (YYYY-MM-DD) tiene uno o más descuentos.
- **uses_per_day**: cuántas veces puede cada usuario usar el cupón por día (p. ej. 1).
- Usuarios se registran con nombre, teléfono, correo y opcionalmente dirección; se les asigna un **código** único.
- Con **código + fecha** se obtienen los descuentos de ese día; con `record_use=true` se consume un uso.
