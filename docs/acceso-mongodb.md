# Acceso a MongoDB en NewsRadar

## El problema: `authSource`

El usuario de la app (`newsradar_app`) está creado en la base de datos `newsradar`, no en `admin`. Si no se especifica `authSource=newsradar`, MongoDB intenta autenticarlo contra `admin` y falla silenciosamente (devuelve una shell vacía sin colecciones).

**Mal** — autentica contra `admin`, no ve nada:
```bash
docker exec newsradar-mongodb mongosh --quiet \
  -u newsradar_app -p change_me_app_pwd \
  --eval "use newsradar; db.getCollectionNames()"
```

**Bien** — autentica contra `newsradar`, ve todo:
```bash
docker exec newsradar-mongodb mongosh \
  "mongodb://newsradar_app:change_me_app_pwd@localhost:27017/newsradar?authSource=newsradar" \
  --eval "..."
```

---

## Credenciales

| Usuario | Contraseña | authSource | Permisos |
|---|---|---|---|
| `newsradar_root` | `change_me_root_pwd` | `admin` | Root (todos los DBs) |
| `newsradar_app` | `change_me_app_pwd` | `newsradar` | Solo DB `newsradar` |

---

## Comandos útiles

### Ver todas las colecciones y su número de documentos
```bash
docker exec newsradar-mongodb mongosh \
  "mongodb://newsradar_app:change_me_app_pwd@localhost:27017/newsradar?authSource=newsradar" \
  --eval "db.getCollectionNames().forEach(c => print(c))"
```

### Ver documentos de una colección (ej: `alerts`)
```bash
docker exec newsradar-mongodb mongosh \
  "mongodb://newsradar_app:change_me_app_pwd@localhost:27017/newsradar?authSource=newsradar" \
  --eval "db.alerts.find().pretty()"
```

### Contar documentos de una colección
```bash
docker exec newsradar-mongodb mongosh \
  "mongodb://newsradar_app:change_me_app_pwd@localhost:27017/newsradar?authSource=newsradar" \
  --eval "db.alerts.countDocuments()"
```

### Entrar en shell interactiva
```bash
docker exec -it newsradar-mongodb mongosh \
  "mongodb://newsradar_app:change_me_app_pwd@localhost:27017/newsradar?authSource=newsradar"
```

### Con el usuario root (si necesitas ver todos los DBs)
```bash
docker exec -it newsradar-mongodb mongosh \
  -u newsradar_root -p change_me_root_pwd --authenticationDatabase admin
```

---

## Colecciones actuales

| Colección | Descripción |
|---|---|
| `users` | Usuarios registrados |
| `alerts` | Alertas configuradas por usuarios |
| `notifications` | Notificaciones generadas por alertas |
| `user_sessions` | Sesiones activas |
| `rss_entradas` | Artículos ingestados por el RSS worker |
| `rss_channels` | Canales RSS registrados |
| `rss_fuentes` | Fuentes RSS |
| `rss_categorias_iptc` | Categorías IPTC para clasificación |
| `information_sources` | Fuentes de información |
| `counters` | Contadores internos (IDs autoincrementales) |
