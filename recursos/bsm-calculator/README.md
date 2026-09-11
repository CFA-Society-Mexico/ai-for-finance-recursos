# Black-Scholes-Merton — Explicador visual interactivo

**Autor: Eduardo Ramos, CFA** ([@EERamos](https://github.com/EERamos))
Repositorio original: <https://github.com/EERamos/bsm-calculator> · Demo en vivo: <https://eeramos.github.io/bsm-calculator/>
Licencia MIT — Copyright (c) 2026 Eduardo Ramos.

Recurso educativo sobre el modelo de Black-Scholes-Merton para el grupo de práctica de CFA Society México. Aportado por su autor para que el grupo lo tenga, lo use en sesiones y lo reutilice.

## Qué es

Un dashboard que corre en el navegador y valúa opciones europeas bajo Black-Scholes-Merton con dividendo continuo, mostrando en vivo todas las griegas de primer y segundo orden. Seis sliders controlan spot, strike, tasa libre de riesgo, tasa de dividendo, volatilidad y plazo. Cada gráfica se redibuja al instante.

La idea es que las sensibilidades se sientan tangibles. La fórmula cerrada es el punto de partida, no el destino: lo que un trader cubre y estresa son las derivadas parciales de ese precio.

## Griegas incluidas

| Griega | Símbolo | Qué mide |
|---|---|---|
| Delta | Δ | Sensibilidad al precio del subyacente |
| Gamma | Γ | Convexidad en el subyacente |
| Vega | V | Sensibilidad a la volatilidad |
| Theta | Θ | Decaimiento temporal |
| Rho | ρ | Sensibilidad a la tasa de interés |
| Vanna | ∂Δ/∂σ | Sensibilidad cruzada, spot y volatilidad |
| Volga | ∂V/∂σ | Convexidad en volatilidad |
| Charm | ∂Δ/∂t | Decaimiento de delta |

También trae diagramas de payoff, el valor de la opción contra el spot, curvas de decaimiento temporal y de sensibilidad a volatilidad, dos superficies 3D de precio sobre (spot, volatilidad), y un residual de paridad put-call en pantalla como verificación integrada.

## Cómo usarlo

**En el navegador.** Abre `index.html` con doble clic. No requiere instalación ni servidor. Plotly y MathJax se cargan por CDN, así que hace falta conexión a internet la primera vez.

**Desde Python.** Instala las dependencias y llama al módulo:

```bash
pip install -r requirements.txt
```

```python
from bsm_calculator import black_scholes

resultado = black_scholes(S=100, K=100, r=0.05, q=0.02, sigma=0.20, tau=1.0, option="call")
print(resultado.price, resultado.delta, resultado.gamma)
```

Todos los argumentos se difunden con las reglas de NumPy, así que acepta arreglos para valuar lotes de contratos de una sola vez.

## Referencia matemática

```
C = S · e^(-qτ) · N(d₁)  -  K · e^(-rτ) · N(d₂)
P = K · e^(-rτ) · N(-d₂) -  S · e^(-qτ) · N(-d₁)

d₁ = [ ln(S/K) + (r - q + ½σ²)τ ] / (σ√τ)
d₂ = d₁ - σ√τ
```

`N(·)` es la CDF normal estándar. El dashboard la implementa con la aproximación racional de Abramowitz & Stegun (1964), precisa a unas 6 cifras decimales.

## Atribución

El material se comparte bajo licencia MIT. Se puede copiar, modificar y redistribuir, incluso con fines comerciales, con una sola condición: conservar el aviso de copyright y la licencia en cualquier copia o versión derivada. Los archivos `index.html` y `bsm_calculator.py` llevan ese aviso incrustado para que sobreviva a las copias, y el dashboard muestra el crédito al autor en pantalla.

Si reutilizas este recurso en una presentación o publicación, cita a **Eduardo Ramos, CFA** y enlaza al repositorio original.
