-- ============================================================
--  Schema principal -- Sistema de Analisis Estadistico UMG
--  Estadistica II -- Ingenieria en Sistemas -- Campus Coban
--  Ejecutar en: Supabase Dashboard > SQL Editor > New query
-- ============================================================

-- ── 1. Tabla de encuestas recolectadas ──────────────────────
CREATE TABLE IF NOT EXISTS encuestas (
    id                    BIGSERIAL PRIMARY KEY,
    edad                  INTEGER        NOT NULL CHECK (edad BETWEEN 18 AND 110),
    grupo_etario          VARCHAR(20)    NOT NULL,
    genero                VARCHAR(20)    NOT NULL,
    ocupacion             VARCHAR(30)    NOT NULL,
    ingreso_mensual       VARCHAR(30)    NOT NULL,
    metodo_pago_preferido VARCHAR(30)    NOT NULL,
    frecuencia_efectivo   VARCHAR(20)    NOT NULL,
    frecuencia_digital    VARCHAR(20)    NOT NULL,
    tipo_comercio         VARCHAR(30)    NOT NULL,
    gasto_semanal         DECIMAL(10,2)  NOT NULL CHECK (gasto_semanal >= 0),
    razon_metodo          VARCHAR(30)    NOT NULL,
    uso_billetera_digital BOOLEAN        NOT NULL,
    confianza_digital     INTEGER        NOT NULL CHECK (confianza_digital BETWEEN 1 AND 5),
    fecha_registro        TIMESTAMP      DEFAULT NOW(),
    user_id               UUID           REFERENCES auth.users(id) ON DELETE SET NULL
);

-- ── 2. Tabla de analisis ejecutados ─────────────────────────
CREATE TABLE IF NOT EXISTS analisis (
    id               BIGSERIAL PRIMARY KEY,
    user_id          UUID           REFERENCES auth.users(id) ON DELETE SET NULL,
    nombre           VARCHAR(100),
    descripcion      TEXT,
    total_registros  INTEGER,
    alpha            DECIMAL(3,2)   DEFAULT 0.05,
    fecha_ejecucion  TIMESTAMP      DEFAULT NOW()
);

-- ── 3. Tabla de resultados de pruebas estadisticas ──────────
CREATE TABLE IF NOT EXISTS resultados_pruebas (
    id            BIGSERIAL PRIMARY KEY,
    analisis_id   BIGINT         NOT NULL REFERENCES analisis(id) ON DELETE CASCADE,
    tipo_prueba   VARCHAR(50)    NOT NULL,
    estadistico   DECIMAL(10,4),
    p_valor       DECIMAL(10,6),
    grados_libertad INTEGER,
    rechaza_h0    BOOLEAN,
    detalles      JSONB
);

-- ── 4. Tabla de decisiones empresariales generadas ──────────
CREATE TABLE IF NOT EXISTS decisiones_generadas (
    id             BIGSERIAL PRIMARY KEY,
    analisis_id    BIGINT       NOT NULL REFERENCES analisis(id) ON DELETE CASCADE,
    decision       TEXT         NOT NULL,
    conclusion     TEXT         NOT NULL,
    recomendacion  TEXT         NOT NULL,
    nivel_alerta   VARCHAR(10)  CHECK (nivel_alerta IN ('alto', 'medio', 'bajo')),
    fecha_creacion TIMESTAMP    DEFAULT NOW()
);

-- ── Indices para consultas frecuentes ───────────────────────
CREATE INDEX IF NOT EXISTS idx_encuestas_user_id       ON encuestas(user_id);
CREATE INDEX IF NOT EXISTS idx_analisis_user_id        ON analisis(user_id);
CREATE INDEX IF NOT EXISTS idx_resultados_analisis_id  ON resultados_pruebas(analisis_id);
CREATE INDEX IF NOT EXISTS idx_decisiones_analisis_id  ON decisiones_generadas(analisis_id);
