-- ============================================================
--  PequeMundo – Base de Datos PostgreSQL (Supabase)
--  Tablas en minúscula para compatibilidad con modelos Python
-- ============================================================

-- ── PRODUCTO ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS producto (
    id_producto   SERIAL PRIMARY KEY,
    nombre        VARCHAR(100)  NOT NULL,
    descripcion   VARCHAR(500),
    categoria     VARCHAR(50)   NOT NULL DEFAULT 'General',
    precio        INTEGER       NOT NULL,
    stock         INTEGER       NOT NULL DEFAULT 0,
    imagen        VARCHAR(200)  DEFAULT 'peque-mueble.webp',
    estado        VARCHAR(20)   NOT NULL DEFAULT 'Activo'
    -- estado: 'Activo' | 'Agotado' | 'Oculto'
);

-- ── USUARIOS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      SERIAL PRIMARY KEY,
    nombre_usuario  VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    telefono        VARCHAR(20),
    password_hash   VARCHAR(255) NOT NULL,
    rol             VARCHAR(20)  NOT NULL DEFAULT 'Cliente'
    -- rol: 'Admin' | 'Vendedor' | 'Cliente'
);

-- ── PEDIDO ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pedido (
    id                  SERIAL PRIMARY KEY,
    cliente             VARCHAR(100) NOT NULL,
    cliente_email       VARCHAR(100),
    total               FLOAT        NOT NULL,
    estado              VARCHAR(30)  NOT NULL DEFAULT 'Pendiente',
    vendedor_id         INTEGER      REFERENCES usuarios(id_usuario),
    mp_preference_id    VARCHAR(200),
    mp_payment_id       VARCHAR(200),
    mp_status           VARCHAR(50),
    items_json          TEXT
);

-- ── ORDEN ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orden (
    id_orden        SERIAL PRIMARY KEY,
    id_usuario      INTEGER      NOT NULL REFERENCES usuarios(id_usuario),
    estado          VARCHAR(30)  NOT NULL DEFAULT 'Pendiente',
    tipo_entrega    VARCHAR(30)  NOT NULL DEFAULT 'domicilio_rm',
    subtotal        INTEGER      NOT NULL,
    precio_envio    INTEGER      NOT NULL DEFAULT 0,
    total           INTEGER      NOT NULL,
    fecha_orden     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── DETALLE_ORDEN ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS detalle_orden (
    id_detalle      SERIAL PRIMARY KEY,
    id_orden        INTEGER NOT NULL REFERENCES orden(id_orden),
    id_producto     INTEGER NOT NULL REFERENCES producto(id_producto),
    cantidad        INTEGER NOT NULL,
    precio_unitario INTEGER NOT NULL,
    subtotal        INTEGER NOT NULL
);

-- ── DIRECCION_ENTREGA ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS direccion_entrega (
    id_direccion  SERIAL PRIMARY KEY,
    id_orden      INTEGER      NOT NULL REFERENCES orden(id_orden),
    destinatario  VARCHAR(120),
    calle         VARCHAR(200),
    numero        VARCHAR(20),
    depto         VARCHAR(50),
    comuna        VARCHAR(60),
    region        VARCHAR(60)
);

-- ── PAGO ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pago (
    id_pago             SERIAL PRIMARY KEY,
    id_orden            INTEGER      NOT NULL REFERENCES orden(id_orden),
    proveedor           VARCHAR(50)  NOT NULL DEFAULT 'MercadoPago',
    codigo_transaccion  VARCHAR(100),
    estado_pago         VARCHAR(30)  NOT NULL DEFAULT 'Pendiente',
    monto               INTEGER      NOT NULL,
    fecha_pago          TIMESTAMP
);

-- ── DESPACHO ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS despacho (
    id_despacho         SERIAL PRIMARY KEY,
    id_orden            INTEGER     NOT NULL REFERENCES orden(id_orden),
    empresa             VARCHAR(60),
    numero_seguimiento  VARCHAR(60),
    fecha_despacho      DATE,
    fecha_entrega       DATE
);

-- ── VENDEDOR ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vendedor (
    id_vendedor     SERIAL PRIMARY KEY,
    id_usuario      INTEGER      NOT NULL REFERENCES usuarios(id_usuario),
    nombre_vendedor VARCHAR(100)
);

-- ============================================================
--  DATOS DE PRUEBA
-- ============================================================

INSERT INTO usuarios (nombre_usuario, email, telefono, password_hash, rol) VALUES
('Admin',          'admin@pequemundo.cl', '+56912345678', 'admin123',   'Admin'),
('María González', 'cliente@test.cl',     '+56987654321', 'cliente123', 'Cliente');

-- Los productos ya NO se cargan por SQL directo: la única vía es la API
-- (POST /api/productos, servida por apis/productos_api.py contra esta misma BD).
-- Para poblar el catálogo de prueba, con la app corriendo, ejecuta:
--   python scripts/seed_productos.py