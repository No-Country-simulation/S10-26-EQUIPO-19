<p align="left">
  <img src="https://hackmd.io/_uploads/rJit2jU3Gg.png" alt="OpenBridge" height="120">
</p>

# Health Score de repositorios

## 1. ¿Qué es el Health Score?

El **Health Score** es un indicador numérico que permite estimar el estado general de mantenimiento y actividad de un repositorio de software.

Su objetivo es facilitar la comparación y priorización de repositorios dentro del catálogo, utilizando información observable de GitHub, como la fecha del último commit de la rama principal, la cantidad de commits recientes, las estrellas y los forks.

El resultado se expresa en una escala de **0 a 100 puntos**:

- **0 puntos:** el repositorio no obtiene puntuación según los criterios definidos. Los repositorios archivados reciben este valor por regla explícita.
- **100 puntos:** alcanza la puntuación máxima posible según los criterios implementados.
- **Valores intermedios:** representan distintos niveles de mantenimiento, actividad y adopción.

El Health Score es una **heurística de evaluación**, no una medición absoluta de la calidad del software.

No garantiza que un repositorio sea seguro, que funcione correctamente, que tenga buena documentación o que sea adecuado para un caso de uso particular.

---

## 2. Componentes del cálculo

El indicador se construye a partir de cuatro componentes:

| Componente | Puntuación máxima sin normalizar | Qué evalúa |
|---|---:|---|
| Mantenimiento | 30 | Antigüedad del último commit de la rama principal. |
| Actividad de commits | 25 | Cantidad de commits realizados durante los últimos 90 días. |
| Popularidad | 15 | Cantidad de estrellas recibidas en GitHub. |
| Reutilización | 10 | Cantidad de forks del repositorio. |
| **Total** | **80** | **Puntuación máxima antes de normalizar.** |

La suma de los componentes produce una puntuación bruta de hasta 80 puntos. Para obtener el resultado final, se normaliza a una escala de 0 a 100.

Los componentes relacionados con estrellas y forks tienen rendimientos decrecientes: conseguir más estrellas o forks sigue sumando puntos, pero su impacto disminuye a medida que aumentan las cantidades.

### 2.1. Mantenimiento

**Puntuación máxima: 30 puntos.**

Este componente evalúa cuánto tiempo pasó desde el último commit de la rama principal del repositorio.

Para ello, se utiliza el campo `last_commit_at`: la fecha del último commit de la rama principal del repositorio. Es el mismo dato que usan el inventario de repositorios y las pruebas de QA.

El campo `pushed_at` de GitHub se conserva como información complementaria: registra pushes a cualquier rama (incluidas ramas automáticas de actualización de dependencias), por lo que puede indicar actividad aunque la rama principal no haya cambiado.

La puntuación se asigna según la antigüedad de esa fecha:

| Tiempo desde el último commit de la rama principal | Puntos |
|---|---:|
| Hasta 30 días | 30 |
| Más de 30 y hasta 90 días | 26 |
| Más de 90 y hasta 180 días | 20 |
| Más de 180 y hasta 365 días | 14 |
| Más de 365 y hasta 730 días | 7 |
| Más de 730 días | 2 |
| Fecha desconocida | 5 |
| Repositorio archivado | 0 |

**Justificación:** una actividad reciente suele ser una señal favorable de mantenimiento. A medida que aumenta el tiempo sin actividad, la puntuación disminuye.

La fecha desconocida recibe una puntuación limitada para distinguir la falta de información de una inactividad comprobada. Sin embargo, esos cinco puntos no deben interpretarse como evidencia de mantenimiento.

El campo `updated_at` de GitHub se conserva como información complementaria, pero no debe confundirse con `last_commit_at` ni con `pushed_at`: un repositorio puede actualizarse por motivos distintos de la publicación de cambios en el código.

### 2.2. Actividad de commits

**Puntuación máxima: 25 puntos.**

Este componente mide la actividad reciente del desarrollo mediante la cantidad de commits de los últimos 90 días.

Se utiliza el campo `commits_last_90_days`, siempre que los datos estén disponibles y sean válidos.

La puntuación se calcula mediante una transformación logarítmica:

```python
activity_points = min(
    25,
    int(log10(commits_last_90_days + 1) * 10)
)
```

La fórmula tiene dos objetivos:

1. Asignar más puntos a los repositorios con mayor actividad reciente.
2. Evitar que los proyectos con cantidades muy elevadas de commits dominen desproporcionadamente el resultado.

La función `log10` hace que los primeros incrementos de actividad tengan mayor impacto relativo que los incrementos posteriores.

Por ejemplo, pasar de pocos commits a una cantidad moderada puede aumentar la puntuación más significativamente que pasar de una cantidad elevada a otra todavía mayor.

**Tratamiento de datos no disponibles:** si GitHub no proporciona la actividad o el campo `commit_activity_status` vale `unavailable`, no se deben interpretar los datos faltantes como cero commits reales. Por eso, el componente no se calcula (queda como `null` en `health_score_details`) y el puntaje se normaliza sobre 55 puntos en lugar de 80 (sección 3).

Los campos `commits_last_30_days` y `commits_last_year` pueden utilizarse como información complementaria, aunque el componente descrito utiliza específicamente la ventana de 90 días.

### 2.3. Popularidad

**Puntuación máxima: 15 puntos.**

Este componente utiliza la cantidad de estrellas del repositorio, representada por `stars` en el catálogo y por `stargazers_count` en la API de GitHub.

La fórmula es:

```python
popularity = min(
    15,
    int(log10(stars + 1) * 3.5)
)
```

Las estrellas representan una señal de interés o reconocimiento de la comunidad.

Se aplica una transformación logarítmica para reducir el impacto de las diferencias extremas entre repositorios muy populares y repositorios con menos estrellas.

**Importante:** las estrellas no demuestran que un proyecto tenga buena calidad, seguridad, mantenimiento activo o compatibilidad con una tecnología determinada. Por ese motivo, su peso está limitado a 15 puntos de la puntuación bruta total.

### 2.4. Reutilización

**Puntuación máxima: 10 puntos.**

Este componente utiliza la cantidad de forks del repositorio, representada por `forks` en el catálogo y por `forks_count` en la API de GitHub.

La fórmula es:

```python
forks_points = min(
    10,
    int(log10(forks + 1) * 2.5)
)
```

Los forks pueden indicar que otras personas o equipos han copiado el repositorio para experimentar, contribuir o desarrollar variantes.

Al igual que las estrellas, se utiliza una transformación logarítmica para limitar el efecto de cantidades muy grandes.

**Importante:** un fork no necesariamente implica reutilización efectiva en producción ni que el proyecto derivado siga mantenido. Por eso, este componente representa una señal aproximada de reutilización potencial.

---

## 3. Fórmula del Health Score

La puntuación bruta se calcula sumando los cuatro componentes:

```python
raw_score = (
    maintenance
    + activity_points
    + popularity
    + forks_points
)
```

La puntuación bruta máxima es de 80 puntos.

Para expresar el resultado en una escala de 0 a 100, se aplica la siguiente normalización:

```python
health_score = round((raw_score / 80) * 100)
```

Si la actividad de commits no está disponible, se excluye ese componente y se normaliza sobre los 55 puntos restantes:

```python
# Actividad de commits no disponible
if commit_activity_status != "available":
    raw_score = maintenance + popularity + forks_points   # máximo 55
    health_score = round((raw_score / 55) * 100)
```

El resultado final es un entero entre 0 y 100.

### Ejemplo ilustrativo

Supongamos que un repositorio obtiene las siguientes puntuaciones:

| Componente | Puntos obtenidos |
|---|---:|
| Mantenimiento | 26/30 |
| Actividad de commits | 20/25 |
| Popularidad | 10/15 |
| Reutilización | 6/10 |
| **Total bruto** | **62/80** |

Aplicando la normalización:

```python
health_score = round((62 / 80) * 100)
```

El Health Score final sería **78/100**.

Este ejemplo es ilustrativo y no representa los resultados reales de un repositorio concreto.

---

## 4. Tratamiento de repositorios archivados

Los repositorios archivados reciben un tratamiento especial.

Cuando GitHub indica que un repositorio está archivado, el Health Score se establece directamente en cero:

```python
if archived:
    return 0, "Abandonado", {
        "maintenance": 0,
        "commit_activity": 0,
        "popularity": 0,
        "forks": 0,
    }
```

Esta regla prevalece sobre el cálculo ordinario de los componentes.

**Justificación:** un repositorio archivado está marcado por su propietario como no destinado a recibir cambios ordinarios. Puede seguir siendo útil como referencia o incluso contener código funcional, pero no debe presentarse como un proyecto activamente mantenido.

Por eso, el valor cero es una decisión explícita del indicador y no una afirmación de que el software carezca de utilidad o calidad.

---

## 5. Estado de mantenimiento

Además del Health Score numérico, el catálogo utiliza un estado descriptivo para comunicar la antigüedad de la actividad del repositorio.

Los estados son:

| Estado | Criterio |
|---|---|
| `Activo` | Último commit de la rama principal hace 90 días o menos. |
| `En riesgo` | Último commit de la rama principal hace más de 90 y hasta 180 días. |
| `Abandonado` | Último commit de la rama principal hace más de 180 días o repositorio archivado. |
| `null` (sin estado) | Fecha del último commit desconocida. La ficha muestra "Sin datos" y el repositorio no aparece en el filtro por nivel de mantenimiento. |

Estos estados se basan en la antigüedad del último commit de la rama principal y en el estado de archivado.

Si la fecha de actividad no está disponible, el sistema debe distinguir esa situación de una fecha conocida que supera los 180 días. No debe inventar una fecha ni afirmar que la inactividad está comprobada. Por eso el estado queda vacío (`null`).

### Diferencia entre Health Score y estado

El Health Score y el estado de mantenimiento son indicadores complementarios, no equivalentes.

- El **Health Score** combina cuatro señales y las expresa en una escala numérica.
- El **estado de mantenimiento** resume la antigüedad de la actividad y el archivado.

Por ejemplo, un repositorio puede tener muchas estrellas y forks, pero llevar más de 180 días sin actividad. En ese caso, puede conservar un puntaje numérico relativamente elevado y, al mismo tiempo, tener el estado `Abandonado`.

Esto no constituye necesariamente un error: significa que el repositorio conserva señales históricas de popularidad o reutilización, aunque su mantenimiento reciente sea desfavorable.

El estado no debe inferirse únicamente a partir del puntaje.

---

## 6. Diferencia entre mantenimiento y actividad de commits

Aunque ambos componentes están relacionados, miden aspectos diferentes.

**Mantenimiento:** evalúa cuánto tiempo pasó desde el último commit de la rama principal. Un repositorio con un cambio reciente puede obtener una puntuación alta en este componente, aunque solo haya recibido un commit.

**Actividad de commits:** evalúa cuántos commits se registraron durante los últimos 90 días. Un proyecto con muchos commits recientes puede obtener una puntuación alta en este componente.

Utilizar ambos permite distinguir entre:

- Un proyecto con actividad reciente, pero poco frecuente.
- Un proyecto con actividad frecuente durante los últimos meses.
- Un proyecto sin actividad reciente.
- Un proyecto cuyo historial de actividad no está disponible.

Ninguno de estos componentes, por separado, demuestra que los cambios sean útiles, que hayan superado pruebas o que mejoren el software.

---

## 7. Campo `maintainer_active`

El catálogo también puede incluir el campo `maintainer_active`, que representa una señal complementaria sobre la actividad reciente del proyecto.

Según el criterio definido para este catálogo, se considera activo cuando se cumplen las siguientes condiciones:

1. El repositorio no está archivado.
2. La actividad de commits de los últimos 90 días es positiva.
3. `commit_activity_status` vale `available` (los datos están disponibles).

Este campo es independiente del Health Score: **no añade ni resta puntos en la fórmula actual**.

Su propósito es ofrecer una señal fácil de interpretar sobre la actividad reciente del repositorio.

Debe entenderse como una heurística del catálogo, no como una confirmación de que exista un mantenedor asignado, que responda a los issues o que revise las contribuciones.

---

## 8. Datos que no forman parte del cálculo

Los siguientes datos pueden almacenarse y mostrarse en la ficha técnica del repositorio, pero no forman parte de la fórmula actual del Health Score:

- Licencia (`license`).
- Cantidad de issues abiertos (`open_issues`).
- Disponibilidad de issues de GitHub (`has_issues`).
- Lenguaje principal (`language`).
- Temas del repositorio (`topics`).
- Descripción del proyecto (`description` y `description_es`).
- Stack tecnológico detectado (`detected_stack`).
- Métodos sugeridos de integración (`integration_methods_suggested`).
- Ideas de integración asociadas (tabla `integrations`).

Estos campos son útiles para evaluar compatibilidad, documentación, integración y adecuación al caso de uso, pero no se utilizan para sumar puntos en el indicador actual.

En particular, `open_issues` no debe interpretarse como una medida directa de calidad o mantenimiento. Algunos proyectos gestionan sus incidencias en Jira, Trac u otros sistemas externos, mientras que otros no utilizan GitHub Issues. En esos casos, `has_issues` es falso y la ficha enlaza a `issues_url`.

---

## 9. Interpretación y limitaciones

El Health Score permite ordenar y comparar repositorios utilizando criterios consistentes, pero tiene limitaciones que deben quedar documentadas.

### Popularidad no equivale a calidad

Un repositorio puede tener muchas estrellas y forks y, aun así, estar desactualizado, tener vulnerabilidades o no cumplir con las necesidades del proyecto.

### Ausencia de datos no equivale a ausencia de actividad

Si GitHub no proporciona información sobre commits, el sistema no debe asumir que el repositorio no tuvo actividad. Debe registrar el estado de disponibilidad de esos datos.

### Los commits no indican la calidad de los cambios

La cantidad de commits no permite saber si los cambios son correctos, útiles, seguros o están suficientemente probados.

### El estado de mantenimiento no es una auditoría

Los estados `Activo`, `En riesgo` y `Abandonado` resumen reglas temporales del catálogo. No reemplazan una revisión del código, la documentación, la comunidad o la seguridad.

### No sustituye la evaluación de compatibilidad

Un repositorio con un Health Score alto no necesariamente es compatible con la arquitectura, el lenguaje o la infraestructura de un proyecto particular.

Por lo tanto, el Health Score debe utilizarse como una señal inicial de priorización y no como el único criterio para seleccionar una dependencia.

---

## 10. Almacenamiento de los resultados

El catálogo separa la información general del repositorio de los resultados de sus métricas.

La tabla `repositories` almacena los datos identificativos y descriptivos, como el nombre, la URL, la licencia, el lenguaje, las estrellas, los forks y las fechas de GitHub.

La tabla `metrics` almacena el resultado del cálculo del Health Score y las métricas de actividad.

Los campos principales de `metrics` son:

| Campo | Descripción |
|---|---|
| `repository_id` | Identificador del repositorio al que pertenece la métrica. |
| `health_score` | Puntaje normalizado entre 0 y 100. |
| `health_status` | Estado descriptivo de mantenimiento (`null` si la fecha del último commit es desconocida). |
| `health_score_details` | Desglose de los puntos obtenidos por componente (`null` en el componente que no se pudo calcular). |
| `commits_last_30_days` | Commits registrados en los últimos 30 días, si están disponibles. |
| `commits_last_90_days` | Commits registrados en los últimos 90 días, si están disponibles. |
| `commits_last_year` | Commits registrados durante el último año, si están disponibles. |
| `commit_activity_status` | Indica si los datos de actividad están disponibles: `available` o `unavailable`. |
| `measured_at` | Fecha y hora en que se calcularon las métricas. |

`health_score_details` permite consultar cómo se obtuvo el resultado sin tener que deducirlo a partir del valor final.

Por ejemplo:

```json
{
  "maintenance": 26,
  "commit_activity": 20,
  "popularity": 10,
  "forks": 6
}
```

Los valores de este ejemplo son ilustrativos.

La tabla `metrics` conserva solamente el resultado más reciente por repositorio. Cuando se recalculan las métricas, se actualiza el registro existente en lugar de crear un historial de mediciones.

La fecha `measured_at` indica cuándo se calcularon las métricas, mientras que `synced_at` en `repositories` indica cuándo se sincronizaron sus datos con GitHub. Ambas fechas pueden ser distintas.

---

## 11. Resumen del algoritmo

El procedimiento general de cálculo es el siguiente:

1. Obtener los datos del repositorio desde GitHub.
2. Comprobar si el repositorio está archivado.
3. Si está archivado, devolver un Health Score de cero, el estado `Abandonado` y los componentes en cero.
4. Calcular los puntos de mantenimiento según la antigüedad de `last_commit_at` (último commit de la rama principal).
5. Calcular los puntos de actividad según los commits de los últimos 90 días, cuando los datos estén disponibles. Si no lo están, el componente queda en `null`.
6. Calcular los puntos de popularidad a partir de las estrellas.
7. Calcular los puntos de reutilización a partir de los forks.
8. Sumar los componentes disponibles para obtener la puntuación bruta, cuyo máximo es 80 (o 55 si la actividad no está disponible).
9. Normalizar el resultado a una escala de 0 a 100.
10. Determinar el estado de mantenimiento según la antigüedad del último commit de la rama principal (o `null` si la fecha es desconocida).
11. Guardar el puntaje, el estado, el desglose de componentes y la fecha de medición.

## 12. Conclusión

El Health Score es un indicador heurístico que combina mantenimiento, actividad reciente, popularidad y reutilización potencial para facilitar la evaluación inicial de repositorios de software.

Su principal ventaja es que transforma distintas señales en una escala común y ofrece un desglose de los componentes que contribuyen al resultado.

Sin embargo, debe interpretarse junto con la ficha técnica, el estado de mantenimiento, la licencia, la documentación, las tecnologías utilizadas y los requisitos concretos del proyecto.

**Un puntaje alto no garantiza calidad ni seguridad, y un puntaje bajo no implica necesariamente que un repositorio carezca de utilidad.**
