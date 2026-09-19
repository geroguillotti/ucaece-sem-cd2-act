# Actividad Formativa — Unidad 1

Texto de referencia completo de la actividad, copiado del documento oficial de cátedra.

**CARRERA:** Licenciatura en Ciencia de Datos
**MATERIA:** Seminario de Ciencia de Datos II
**CUATRIMESTRE Y AÑO:** 2do Cuatrimestre 2026
**PROFESOR/A:** Miguel Méndez Garabetti, Eduardo Piray
**UNIDAD N° 1:** Temas Avanzados en Construcción de Modelos con Técnicas de Ciencia de Datos
**ACTIVIDAD FORMATIVA:** Trabajo Práctico Individual. Diseño y justificación técnica de
una solución basada en Foundation Models.

**REQUISITOS FORMALES:** formato Word o PDF, Arial 11, interlineado 1,5, alineación
justificada, márgenes estándar, citas en formato APA. Entrega individual. Extensión
sugerida: entre 3 y 5 páginas (sin contar portada ni bibliografía).

**CRITERIOS DE EVALUACIÓN:**
- Comprensión e interpretación de la consigna formulada.
- Dominio adecuado de los temas abordados.
- Aplicación de la teoría a situaciones prácticas.
- Manejo del vocabulario específico.
- Pertinencia y claridad en la redacción.
- Estilo académico, correcta construcción gramatical, puntuación y acentuación.
- Cumplimiento de las pautas de presentación de trabajos escritos.

**Nota:** el bloque 1.2 (Modelos Generativos Avanzados) no se evalúa mediante esta
actividad; su tratamiento corresponde a la instancia teórica de la unidad.

---

## CONSIGNAS (texto original de cátedra, sin modificar)

**1.** Elegir un caso de uso real o hipotético que pueda resolverse con un Foundation
Model (por ejemplo: un asistente de atención al cliente, un sistema de generación de
resúmenes, un generador de imágenes para marketing, un asistente de análisis de datos,
etc.) y describirlo brevemente: el problema a resolver, los usuarios destinatarios y las
principales restricciones del contexto (presupuesto, privacidad de los datos, latencia
requerida, etc.).

**2.** Seleccionar un Foundation Model apropiado para el caso, justificando la elección
entre un modelo cerrado (por ejemplo GPT-4, Gemini o Claude, accesibles mediante API) y
un modelo de pesos abiertos (por ejemplo LLaMA o Mistral), considerando explícitamente
costos, privacidad de los datos y capacidad de personalización.

**3.** Definir y justificar la estrategia de adaptación del modelo al caso de uso elegido
(full fine-tuning, técnicas PEFT como LoRA o QLoRA, o prompt engineering avanzado como
chain-of-thought o few-shot prompting), explicando por qué esa estrategia resulta más
adecuada que las alternativas para este caso en particular.

**4.** Especificar y justificar la infraestructura de hardware necesaria (GPU, TPU, NPU o
entrenamiento distribuido, según corresponda) para ajustar y desplegar la solución
propuesta, estimando de forma aproximada el orden de magnitud de los recursos requeridos.

**5.** Elaborar un esquema o diagrama (puede ser textual) que sintetice el flujo completo
de la solución propuesta, desde la entrada del usuario hasta la respuesta generada por el
sistema.

---

## COMPONENTE PRÁCTICO (agregado, consignas 6 a 10)

Implementación ejecutable y verificable del diseño de las consignas 1 a 5. Entorno
gratuito en todos los casos (GitHub Codespaces, Groq API, Gemini API, Google Colab); no
requiere hardware propio de alta capacidad.

**6. Preparación del entorno de trabajo**
a. Crear un repositorio en GitHub para la actividad (puede partir de la plantilla de la
   cátedra vía "Use this template").
b. Abrir el repositorio en GitHub Codespaces (Code → Codespaces → Create codespace on
   main).
c. Verificar que Python esté disponible (`python3 --version`).

**7. Obtención de la API key**
a. Modelo cerrado (consigna 2) → API key gratuita de Google AI Studio (Gemini API).
b. Modelo de pesos abiertos (consigna 2) → API key gratuita de Groq (console.groq.com).
c. Guardar la clave en `.env`, excluido del control de versiones vía `.gitignore`. Nunca
   subir la API key al repositorio.

**8. Instalación de dependencias**
Instalar únicamente lo necesario según la rama elegida (`python-dotenv` + `groq` o
`google-generativeai`), registrado en `requirements.txt`.

**9. Implementación de la estrategia de adaptación (consigna 3)**
a. **Prompt engineering avanzado:** script `main.py` que invoque la API elegida aplicando
   la técnica justificada (few-shot / chain-of-thought), ejecutado con al menos 3
   consultas de ejemplo distintas, documentadas en `evidencias.md`.
b. **PEFT (LoRA/QLoRA):** notebook en Google Colab (GPU T4 gratuita) que cargue un modelo
   abierto pequeño (ej. GPT-2 o Gemma 2B), aplique el ajuste sobre ejemplos propios del
   caso de uso, y reporte una comparación antes/después. Subir el `.ipynb` al mismo
   repositorio.
c. **Full fine-tuning:** excede el hardware gratuito disponible (conclusión relevante del
   bloque 1.3). Implementar en su lugar la demostración PEFT del punto (b) como
   aproximación factible, dejando esa limitación explicitada en el informe.

**10. Registro y entrega**
a. Commits del código, notebook y evidencias.
b. `README.md` breve: caso de uso, modelo elegido, estrategia de adaptación, cómo
   ejecutar.
c. Incluir en el documento entregado el enlace al repositorio y capturas de una ejecución
   exitosa.

---

## CALIFICACIÓN DE LA ACTIVIDAD (actualizada — 5 puntos teoría + 5 puntos práctica = 10)

| Bloque | Consigna | Puntos |
|---|---|---|
| Teoría | 1. Caso de uso | 1 |
| Teoría | 2. Selección y justificación del Foundation Model | 1 |
| Teoría | 3. Estrategia de adaptación | 1,5 |
| Teoría | 4. Infraestructura de hardware | 1 |
| Teoría | 5. Esquema del flujo | 0,5 |
| Práctica | 6. Preparación del entorno (Codespaces) | 0,5 |
| Práctica | 7. Obtención de API key (manejo seguro) | 0,5 |
| Práctica | 8. Instalación de dependencias | 0,5 |
| Práctica | 9. Implementación de la estrategia elegida | 2,5 |
| Práctica | 10. Registro, README y entrega del enlace | 1 |
| **Total** | | **10** (mínimo de aprobación: 4) |
