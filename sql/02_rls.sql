-- ============================================================
--  Row Level Security (RLS) — politicas completas
--  Sistema de Analisis Estadistico UMG · Estadistica II
--
--  Incluye:
--    · Politicas de usuarios autenticados (lectura e insercion)
--    · Politicas de lectura publica para modo visitante (anon)
--
--  Ejecutar DESPUES de 01_schema.sql
--  Ejecutar en: Supabase Dashboard > SQL Editor > New query
--  Es idempotente: usa DROP IF EXISTS antes de cada CREATE.
-- ============================================================

-- ── Habilitar RLS en todas las tablas ───────────────────────
ALTER TABLE encuestas            ENABLE ROW LEVEL SECURITY;
ALTER TABLE analisis             ENABLE ROW LEVEL SECURITY;
ALTER TABLE resultados_pruebas   ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisiones_generadas ENABLE ROW LEVEL SECURITY;


-- ============================================================
--  POLITICAS DE USUARIOS AUTENTICADOS
-- ============================================================

-- ── encuestas ────────────────────────────────────────────────
DROP POLICY IF EXISTS "usuario lee sus encuestas"     ON encuestas;
DROP POLICY IF EXISTS "usuario inserta sus encuestas" ON encuestas;

CREATE POLICY "usuario lee sus encuestas"
    ON encuestas FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "usuario inserta sus encuestas"
    ON encuestas FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ── analisis ─────────────────────────────────────────────────
DROP POLICY IF EXISTS "usuario lee sus analisis"     ON analisis;
DROP POLICY IF EXISTS "usuario inserta sus analisis" ON analisis;

CREATE POLICY "usuario lee sus analisis"
    ON analisis FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "usuario inserta sus analisis"
    ON analisis FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ── resultados_pruebas ───────────────────────────────────────
DROP POLICY IF EXISTS "usuario lee sus resultados"     ON resultados_pruebas;
DROP POLICY IF EXISTS "usuario inserta sus resultados" ON resultados_pruebas;

CREATE POLICY "usuario lee sus resultados"
    ON resultados_pruebas FOR SELECT
    USING (
        analisis_id IN (
            SELECT id FROM analisis WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "usuario inserta sus resultados"
    ON resultados_pruebas FOR INSERT
    WITH CHECK (
        analisis_id IN (
            SELECT id FROM analisis WHERE user_id = auth.uid()
        )
    );

-- ── decisiones_generadas ─────────────────────────────────────
DROP POLICY IF EXISTS "usuario lee sus decisiones"     ON decisiones_generadas;
DROP POLICY IF EXISTS "usuario inserta sus decisiones" ON decisiones_generadas;

CREATE POLICY "usuario lee sus decisiones"
    ON decisiones_generadas FOR SELECT
    USING (
        analisis_id IN (
            SELECT id FROM analisis WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "usuario inserta sus decisiones"
    ON decisiones_generadas FOR INSERT
    WITH CHECK (
        analisis_id IN (
            SELECT id FROM analisis WHERE user_id = auth.uid()
        )
    );


-- ============================================================
--  POLITICAS DE LECTURA PUBLICA (MODO VISITANTE)
--  Permite lectura anonima (sin sesion) para la vista publica.
--  Los datos de encuestas son anonimizados (sin PII).
-- ============================================================

DROP POLICY IF EXISTS "publico_lee_analisis"             ON analisis;
DROP POLICY IF EXISTS "publico_lee_resultados_pruebas"   ON resultados_pruebas;
DROP POLICY IF EXISTS "publico_lee_decisiones_generadas" ON decisiones_generadas;
DROP POLICY IF EXISTS "publico_lee_encuestas"            ON encuestas;

CREATE POLICY "publico_lee_analisis"
    ON analisis FOR SELECT TO anon
    USING (true);

CREATE POLICY "publico_lee_resultados_pruebas"
    ON resultados_pruebas FOR SELECT TO anon
    USING (true);

CREATE POLICY "publico_lee_decisiones_generadas"
    ON decisiones_generadas FOR SELECT TO anon
    USING (true);

CREATE POLICY "publico_lee_encuestas"
    ON encuestas FOR SELECT TO anon
    USING (true);
