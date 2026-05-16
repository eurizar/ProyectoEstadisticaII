# Sistema de Análisis Estadístico — UMG Cobán

> **Análisis de hábitos de pago y brecha generacional en la adopción de métodos digitales**
> Cobán, Alta Verapaz · Estadística II · Ingeniería en Sistemas · Universidad Mariano Gálvez

---

## Integrantes — Grupo

| # | Nombre completo | Carnet | Rol en el proyecto |
|---|----------------|--------|--------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |

**Campus:** Cobán, Alta Verapaz · **Ciclo:** 2026

---

## Descripción

Sistema web interactivo desarrollado con **Python + Streamlit** que analiza los hábitos de pago de consumidores de Cobán mediante tres pruebas estadísticas inferenciales. Genera visualizaciones, decisiones empresariales automáticas y reportes PDF exportables. Incluye modo visitante público para consulta sin credenciales.

---

## Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| **Login** | Autenticación con Supabase Auth · sesión persistente con cookie + localStorage |
| **Modo visitante** | Acceso público sin cuenta · solo lectura de resultados y dashboard |
| **Dashboard** | KPIs en tiempo real · gráficas de distribución · indicadores de adopción digital |
| **Cargar Datos** | Importar encuestas desde CSV o Excel · validación automática de estructura |
| **Nuevo Análisis** | Ejecutar las 3 pruebas estadísticas con nivel α configurable (0.01 / 0.05 / 0.10) |
| **Resultados** | Visualización completa · 14 gráficas interactivas · tablas de frecuencia |
| **Histórico** | Registro de todos los análisis ejecutados · carga de resultados anteriores |
| **Exportar PDF** | Reporte completo descargable con pruebas, gráficas y decisiones |

### Pruebas estadísticas implementadas

| Prueba | Hipótesis nula | Hipótesis alternativa |
|--------|---------------|----------------------|
| **Prueba t** | μ_efectivo = μ_digital | μ_efectivo ≠ μ_digital |
| **Chi-cuadrado** | Grupo etario ⊥ Método de pago | Existe relación significativa |
| **Z para proporción** | p ≤ 0.40 (adopción digital) | p > 0.40 |

---

## Stack tecnológico

```
┌─────────────────────────────────────────────┐
│  PRESENTACIÓN                               │
│  ├─ Streamlit 1.37+  (interfaz web)         │
│  └─ Plotly           (gráficas interactivas)│
├─────────────────────────────────────────────┤
│  LÓGICA                                     │
│  ├─ Pandas           (manipulación datos)   │
│  ├─ NumPy            (cálculos numéricos)   │
│  └─ SciPy            (pruebas estadísticas) │
├─────────────────────────────────────────────┤
│  DATOS & AUTH                               │
│  ├─ Supabase         (PostgreSQL + Auth)    │
│  └─ python-dotenv    (variables entorno)    │
├─────────────────────────────────────────────┤
│  SALIDA                                     │
│  └─ ReportLab        (exportación PDF)      │
└─────────────────────────────────────────────┘
```

---

## Estructura del proyecto

```
ProyectoEstaditicall/
├── app.py                      # Punto de entrada · Login y modo visitante
├── requirements.txt            # Dependencias Python
├── .env                        # Credenciales Supabase (NO subir a Git)
├── .env.example                # Plantilla de variables de entorno
├── .gitignore
├── start_server.bat            # Inicio rápido en Windows (doble clic)
│
├── pages/                      # Páginas Streamlit (multipágina)
│   ├── 1_Dashboard.py          # KPIs e indicadores generales
│   ├── 2_Cargar_Datos.py       # Importar CSV / Excel
│   ├── 3_Nuevo_Analisis.py     # Ejecutar pruebas estadísticas
│   ├── 4_Resultados.py         # Visualizaciones y decisiones
│   ├── 5_Historico.py          # Historial de análisis
│   └── 6_Exportar.py           # Generar reporte PDF
│
├── modules/                    # Lógica de negocio
│   ├── auth.py                 # Autenticación Supabase · sesión persistente
│   ├── db.py                   # Operaciones con base de datos
│   ├── carga_datos.py          # Validación y carga de archivos
│   ├── pruebas.py              # Prueba t· Chi-cuadrado · Z proporción
│   ├── decisiones.py           # Motor de decisiones empresariales automáticas
│   ├── graficas.py             # 14+ visualizaciones con Plotly
│   ├── exportar.py             # Generación de PDF con ReportLab
│   └── ui_helpers.py           # Componentes UI compartidos · sidebar
│
├── assets/
│   └── style.css               # Estilos globales (diseño Navy + Gold)
│
├── sql/
│   ├── 01_schema.sql           # Creación de tablas e índices
│   └── 02_rls.sql              # Políticas RLS: usuarios autenticados + visitantes
│
└── data/
    └── encuesta_ejemplo.csv    # Dataset de ejemplo (50 registros)
```

---

## Instalación y configuración

### Requisito: Python 3.12

Este proyecto requiere **Python 3.12**. Python 3.13+ no tiene soporte completo para todas las dependencias aún.

```powershell
# Instalar Python 3.12 (si no está instalado)
winget install Python.Python.3.12

# Verificar
py -3.12 --version
```

### 1. Clonar y preparar entorno

```powershell
# Clonar repositorio
git clone <url-del-repositorio>
cd ProyectoEstadisticaII

# Permitir scripts en PowerShell (solo primera vez)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Crear entorno virtual con Python 3.12
py -3.12 -m venv venv312

# Activar entorno virtual
venv312\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```powershell
copy .env.example .env
```

Editar `.env` con tus credenciales de Supabase:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
```

### 3. Configurar base de datos en Supabase

Ejecutar los SQL en orden desde **Supabase Dashboard → SQL Editor → New Query**:

```
1. sql/01_schema.sql   →  Crea las 4 tablas e índices
2. sql/02_rls.sql      →  Aplica todas las políticas de seguridad (RLS)
```

> `02_rls.sql` es idempotente — usar `DROP IF EXISTS` antes de cada `CREATE`, por lo que puede re-ejecutarse sin errores.

### 4. Ejecutar la aplicación

```powershell
streamlit run app.py
```

O en Windows, doble clic en `start_server.bat`.

---

## Uso del sistema

### Acceso como usuario registrado

1. Ingresar con correo y contraseña institucional (`@umg.edu.gt`)
2. **Cargar Datos** → subir `data/encuesta_ejemplo.csv` o el archivo Excel.xlsx o bien el CSV propio
3. **Nuevo Análisis** → seleccionar α y ejecutar las 3 pruebas
4. **Resultados** → explorar 14 gráficas y las decisiones empresariales generadas
5. **Histórico** → consultar análisis anteriores
6. **Exportar** → descargar reporte PDF completo

### Acceso como visitante (modo público)

1. En la pantalla de login, marcar **"Acceder como visitante"**
2. Presionar **"Ver resultados como visitante →"**
3. El sistema carga automáticamente el último análisis guardado
4. Dashboard y Resultados disponibles en solo lectura
5. Secciones de carga, análisis e historial permanecen deshabilitadas


---

## Base de datos — Tablas

| Tabla | Descripción |
|-------|-------------|
| `encuestas` | Registros individuales de la encuesta (13 variables por persona) |
| `analisis` | Cabecera de cada ejecución (nombre, α, total registros, fecha) |
| `resultados_pruebas` | Estadístico, p-valor y detalles de cada prueba por análisis |
| `decisiones_generadas` | Conclusiones y recomendaciones empresariales automáticas |

### Políticas de seguridad (RLS)

| Política | Alcance | Operación |
|----------|---------|-----------|
| Usuarios autenticados | Solo sus propios datos (`user_id = auth.uid()`) | SELECT · INSERT |
| Visitantes anónimos | Todos los registros (lectura pública) | SELECT |

---

## Variables de la encuesta

| # | Variable | Tipo |
|---|----------|------|
| 1 | Edad | Cuantitativa continua |
| 2 | Grupo etario | Cualitativa ordinal (18-25 / 26-35 / 36-50 / 51+) |
| 3 | Género | Cualitativa nominal |
| 4 | Ocupación | Cualitativa nominal |
| 5 | Ingreso mensual | Cualitativa ordinal (rangos en Q) |
| 6 | Método de pago preferido | Cualitativa nominal |
| 7 | Frecuencia de uso — efectivo | Cualitativa ordinal |
| 8 | Frecuencia de uso — digital | Cualitativa ordinal |
| 9 | Tipo de comercio | Cualitativa nominal |
| 10 | Gasto semanal (Q) | Cuantitativa continua |
| 11 | Razón para elegir método | Cualitativa nominal |
| 12 | ¿Ha usado billetera digital? | Cualitativa dicotómica |
| 13 | Confianza en pagos digitales | Ordinal escala 1–5 |

---

## Seguridad

- `.env` excluido de Git mediante `.gitignore` — las credenciales nunca se suben al repositorio
- Autenticación manejada por Supabase Auth (JWT)
- Sesión persistente vía cookie segura (max-age 30 días para usuarios, 24 h para visitantes)
- RLS activo en todas las tablas — cada usuario accede únicamente a sus datos

---

## Referencias

- [Streamlit Docs](https://docs.streamlit.io)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [SciPy Stats](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Plotly Python](https://plotly.com/python)
- [Pandas](https://pandas.pydata.org/docs)
- [ReportLab](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

**Estadística II · Ingeniería en Sistemas · UMG Campus Cobán · 2026**
