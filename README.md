# AI for Finance — Recursos CFA Society México

Repositorio de recursos sobre IA aplicada a finanzas para los miembros del grupo de práctica de **CFA Society México**. Nace de la sesión *"AI for Finance: Construyendo Agentes Financieros en Producción"* y está pensado para crecer con el tiempo gracias a la colaboración de otros miembros.

> El plugin financiero y las skills del grupo viven en repos aparte — este repositorio es solo la sección de recursos.

## Contenido

| Carpeta | Qué encontrarás |
|---|---|
| [`/recursos`](./recursos) | El two-pager de la sesión: conectores, cómo crear skills, y una guía de GitHub para no programadores. |
| [`/instrucciones`](./instrucciones) | Plantilla de instrucciones personalizadas para usar Claude/ChatGPT en tareas de análisis financiero como CFA charterholder. |

## ¿Por dónde empezar?

1. Lee el PDF en [`/recursos`](./recursos/AI-for-Finance-Recursos-CFA.pdf) — cubre el contexto completo de la sesión.
2. Copia la plantilla de [`/instrucciones`](./instrucciones/custom-instructions-template.md) a tu configuración de Claude (Configuración → Perfil → Instrucciones personalizadas) o ChatGPT (Configuración → Personalización).
3. Si tienes GitHub CLI instalado y autenticado (`gh auth login`), puedes pedirle a un agente (Claude Code, Codex, etc.) que trabaje directamente sobre este repo en lenguaje natural — ver ejemplos abajo.

## Guía rápida de GitHub (para no programadores)

- **Repositorio ("repo")**: carpeta de un proyecto con archivos e historial de cambios.
- **Clonar vs. Fork**: clonar descarga una copia local; fork crea una copia en tu propia cuenta para proponer cambios sin permiso de escritura sobre el original.
- **Branch ("rama")**: línea de trabajo paralela dentro del mismo repo, para probar cambios sin tocar `main`.
- **Commit**: guardar un cambio concreto con una nota de qué y por qué.
- **Issue**: reporte de error o idea de mejora, en texto libre, sin tocar código.
- **Pull request ("PR")**: propuesta formal de incorporar los commits de una rama al repo principal, para revisión del grupo.
- **README**: documento de bienvenida de una carpeta, pensado para personas.
- **SKILLS.md / AGENTS.md**: instrucciones equivalentes, pero dirigidas al agente de IA.

### Ejemplos de "asks" a un agente — de lo simple a lo ambicioso

1. "Clona el repo y muéstrame qué hay en `/recursos`."
2. "Crea una rama nueva y ajusta el README con este dato actualizado."
3. "Abre un pull request con este cambio para que el grupo lo revise."
4. "Arma la estructura para un proyecto de valuación DCF: `/data`, `/notebooks`, `/src`, `/tests`, README y `.gitignore`. Súbelo como repo nuevo."
5. "Crea un Jupyter Notebook que descargue precios históricos, calcule retornos y grafique el drawdown."
6. "Convierte ese notebook en un dashboard de Streamlit con filtros por ticker y rango de fechas."

## Cómo contribuir

Este repo crece con los aportes del grupo. Para agregar un recurso:

1. Haz un **fork** de este repositorio (o pide acceso de colaborador).
2. Crea una **rama** con un nombre descriptivo (`docs/agrega-guia-rag`, por ejemplo).
3. Agrega tu recurso en la carpeta que corresponda (o crea una nueva si hace falta).
4. Abre un **pull request** describiendo qué agregas y por qué.
5. El grupo revisa y aprueba el merge a `main`.

¿Dudas o ideas? Abre un **issue** describiéndolo en texto libre — no hace falta tocar código.
