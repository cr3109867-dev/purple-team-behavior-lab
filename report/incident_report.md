# Informe de Incidente – Simulación de Comportamiento Malicioso
**Proyecto:** Purple Team Behavior Lab  
**Autor:** [Tu nombre]  
**Fecha:** 2026-01-15  
**Entorno:** Laboratorio controlado (datos ficticios)

---

## 1. Resumen Ejecutivo
Durante un ejercicio de laboratorio controlado, se identificó un comportamiento
anómalo simulado que presenta características asociadas a fases tempranas de
actividad maliciosa. Dicho comportamiento incluyó la enumeración automatizada
de archivos con nombres sensibles, la copia de estos archivos a una carpeta de
staging y la generación de múltiples eventos en un corto periodo de tiempo.

Aunque no se accedió ni exfiltró información real, el patrón observado es
representativo de técnicas utilizadas en incidentes de seguridad reales durante
etapas de reconocimiento y preparación de datos.

---

## 2. Alcance y Metodología
Este análisis fue realizado en un entorno de laboratorio completamente controlado,
utilizando archivos ficticios y scripts inofensivos con fines exclusivamente
educativos y profesionales.

La metodología aplicada fue la siguiente:
1. Simulación de comportamiento sospechoso
2. Generación de eventos y logs estructurados
3. Detección basada en reglas de comportamiento
4. Correlación de alertas
5. Análisis de riesgo y conclusiones

---

## 3. Línea de Tiempo del Incidente
Durante una única sesión de ejecución se observaron los siguientes eventos:

- Inicio de la simulación
- Enumeración de archivos en un directorio simulado como sensible
- Copia de archivos a una carpeta de staging
- Finalización de la actividad simulada

Todos los eventos fueron registrados con marcas de tiempo en formato UTC para
facilitar su análisis forense.

---

## 4. Detección y Evidencia
El motor de detección identificó las siguientes alertas:

### 4.1 Actividad en Ráfaga (Severidad Media)
Se detectó una alta concentración de eventos en una ventana de tiempo reducida,
lo cual sugiere un comportamiento automatizado no típico de un usuario humano.

### 4.2 Múltiples Copias a Staging (Severidad Media)
Se observaron múltiples operaciones de copiado hacia un directorio de staging
durante una misma sesión, lo cual podría indicar una fase de preparación previa
a una posible exfiltración de información.

### 4.3 Enumeración de Nombres Sensibles (Severidad Baja)
El proceso accedió a archivos cuyos nombres están comúnmente asociados a
información sensible, como credenciales, datos financieros y registros de clientes.