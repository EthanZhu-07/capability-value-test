# Capability Value Test｜Validación del valor de una nueva capacidad

[English](README.md)｜[简体中文](README.zh-CN.md)｜[繁體中文](README.zh-TW.md)｜[日本語](README.ja.md)｜[한국어](README.ko.md)｜[Русский](README.ru.md)｜[हिन्दी](README.hi.md)｜**Español**｜[Français](README.fr.md)｜[Deutsch](README.de.md)｜[Português](README.pt.md)｜[العربية](README.ar.md)

> Hacer visible el uso de una nueva capacidad y medible el valor que genera.

Capability Value Test es un Skill general para agentes de IA. Verifica si una capacidad recién integrada (por ejemplo, un Skill, modelo, plugin, MCP Server, navegador, componente de código abierto o flujo de un agente) fue realmente utilizada y si crea valor medible frente al método anterior.

Diseña una prueba A/B justa entre el método anterior y el método habilitado por la nueva capacidad. Una persona revisa el diseño completo antes de ejecutar cualquiera de los dos métodos. Al finalizar, genera un informe HTML autónomo, visual y trazable.

## Las preguntas que responde

1. **¿La capacidad fue utilizada realmente y dónde está la evidencia?**
2. **¿Generó valor y se puede cuantificar?**
3. **¿Se pueden comprender visualmente el proceso de uso y el valor concreto?**

## Proceso

1. Definir la nueva capacidad y los métodos antes y después de integrarla.
2. Elegir una tarea real que ambos métodos puedan completar.
3. Alinear entradas, entorno, restricciones, alcance de la medición y criterios de evaluación.
4. Presentar el diseño completo para revisión humana; revisarlo si se rechaza.
5. Ejecutar ambos métodos únicamente tras la aprobación explícita y registrar resultados, métricas y evidencia.
6. Analizar las diferencias y generar el informe HTML.

El objetivo no es hacer ganar a la nueva capacidad, sino determinar qué cambió y si la evidencia respalda su adopción.

## Informe HTML

1. **Recomendación final**: adoptar, no adoptar o evidencia insuficiente; incluye escenarios adecuados e inadecuados.
2. **Valor y beneficios**: calidad, tiempo total, Token, coste, pasos, errores y reintentos.
3. **Prueba de uso**: la última sección conserva por separado comandos, llamadas a herramientas, entradas, salidas, registros, marcas de tiempo, IDs de tarea y estados.

Las métricas no disponibles se muestran como “No disponible”, nunca como cero. Los secretos deben eliminarse.

## Instalación

```bash
npx -y skills add EthanZhu-07/capability-value-test -g --all
```

O clona el repositorio y sigue la convención del directorio de Skills de tu agente:

```bash
git clone https://github.com/EthanZhu-07/capability-value-test.git
```

## Ejemplo de uso

```text
Usa Capability Value Test para comparar mi método actual de navegador con el método habilitado por Lightpanda. Muéstrame el diseño antes de ejecutarlo.
```

## Generar el informe manualmente

```bash
python3 scripts/render_report.py tests/sample-experiment.json --output report.html
```

El generador usa solo la biblioteca estándar de Python y crea un único HTML que funciona sin conexión.

La versión más reciente usa un formato de informe fijo y versionado. Todos los informes mantienen las mismas secciones y el mismo orden, con una explicación bajo cada encabezado principal. El idioma predeterminado es el idioma de conversación del usuario y puede cambiarse desde la esquina superior derecha. El análisis separa los resultados del experimento, la investigación externa con fuentes y la recomendación final, y describe cada escenario mediante una persona, una tarea y un entorno concretos.

## Límites

- Una ejecución por método aporta evidencia orientativa, no una garantía estadística.
- Ambos métodos deben poder completar la misma tarea representativa.
- Token y coste solo se comparan si el entorno los proporciona.
- Si no se puede verificar el uso, el resultado debe ser “Evidencia insuficiente”.
- La ejecución headless se presenta como un registro, no como una grabación en directo.

## Licencia

Actualmente no se incluye un archivo de licencia. Que el repositorio sea público no concede por sí solo permiso para copiar, modificar o redistribuir el proyecto.
