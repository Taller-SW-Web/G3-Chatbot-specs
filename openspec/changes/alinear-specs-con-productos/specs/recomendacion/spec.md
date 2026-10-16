## MODIFIED Requirements

### Requirement: Recomendaciones veraces y disponibles
El sistema DEBE (SHALL) recomendar únicamente productos activos que no estén `AGOTADO` (con `INDETERMINADO` se puede recomendar sin afirmar que hay stock) y DEBE generar las justificaciones solo a partir de los atributos devueltos por Productos.

*Trazabilidad: SPEC-07 · Requisito 2.*

#### Scenario: Producto recomendado sin stock
- **DADO** que un candidato tiene todos sus SKU en `AGOTADO`
- **CUANDO** se arma la recomendación
- **ENTONCES** se excluye y se reemplaza por el siguiente candidato

#### Scenario: No hay productos que cumplan
- **DADO** un presupuesto de S/ 30 para zapatillas
- **CUANDO** no existe ninguna opción
- **ENTONCES** se informa con honestidad ("No tengo zapatillas en ese presupuesto; las más económicas cuestan S/ 149") y se ofrece ver esas opciones o accesorios dentro del presupuesto
