<script setup lang="ts">
import { ref } from 'vue'
import Card from 'primevue/card'
import Accordion from 'primevue/accordion'
import AccordionPanel from 'primevue/accordionpanel'
import AccordionHeader from 'primevue/accordionheader'
import AccordionContent from 'primevue/accordioncontent'
import Tag from 'primevue/tag'

const accordionValue = ref<string[]>([])
</script>

<template>
  <div class="manual">
    <header class="manual-hero">
      <div class="manual-hero-badge">
        <i class="pi pi-book" />
        <span>Documentación</span>
      </div>
      <h1 class="manual-title">Sistema Cuponera Salchimonster</h1>
      <p class="manual-intro">
        Guía detallada de funcionamiento, módulos, reglas y consideraciones para gestionar descuentos, cuponeras y canje de cupones. Consulte esta guía siempre que tenga dudas.
      </p>
    </header>

    <nav class="manual-toc">
      <h2><i class="pi pi-list" /> Contenido</h2>
      <ol class="toc-list">
        <li><a href="#intro">Introducción</a></li>
        <li><a href="#flujo">Flujo típico de uso</a></li>
        <li><a href="#carpetas">Carpetas</a>
          <ul>
            <li><a href="#carpetas-que">Qué son y para qué sirven</a></li>
            <li><a href="#carpetas-crud">Crear, editar y eliminar</a></li>
          </ul>
        </li>
        <li><a href="#descuentos">Descuentos</a>
          <ul>
            <li><a href="#descuentos-nombre">Nombre obligatorio</a></li>
            <li><a href="#descuentos-tipos">Tipos de descuento</a></li>
            <li><a href="#descuentos-scope">Scope y sedes</a></li>
            <li><a href="#descuentos-ejemplo">Ejemplo con productos reales</a></li>
          </ul>
        </li>
        <li><a href="#cuponeras">Cuponeras</a>
          <ul>
            <li><a href="#cuponeras-que">Qué es una cuponera</a></li>
            <li><a href="#cuponeras-vigencia">Vigencia (inicio y fin)</a></li>
            <li><a href="#cuponeras-calendario">Calendario por día</a></li>
            <li><a href="#cuponeras-usuarios">Usuarios y códigos</a></li>
          </ul>
        </li>
        <li><a href="#consultar">Consultar cupón</a>
          <ul>
            <li><a href="#consultar-uso">Uso en caja</a></li>
            <li><a href="#consultar-mensajes">Mensajes y respuestas</a></li>
          </ul>
        </li>
        <li><a href="#consideraciones">Consideraciones y buenas prácticas</a></li>
      </ol>
    </nav>

    <!-- INTRO -->
    <section id="intro" class="manual-section">
      <h2><i class="pi pi-info-circle" /> Introducción</h2>
      <Card class="manual-card">
        <template #content>
          <p>
            El sistema permite definir <strong>descuentos</strong> (reglas de promoción), agruparlos en <strong>cuponeras</strong> con un calendario por día, y asignar <strong>usuarios</strong> con un código único. Los clientes canjean su código en <strong>Consultar cupón</strong> para ver los descuentos del día.
          </p>
          <p>
            Todo se organiza opcionalmente en <strong>carpetas</strong> (para descuentos y cuponeras). Las sedes y los productos/categorías se obtienen del backend de Salchimonster; solo se usan sedes con zona horaria <code>America/Bogota</code>, visibles en web (<code>show_on_web = true</code>) y se excluye la sede 32.
          </p>
          <div class="callout callout-info">
            <strong><i class="pi pi-info-circle" /> Dato técnico</strong>
            <p>Los menús y categorías se sincronizan periódicamente desde el backend. Los descuentos se validan contra esos menús al guardar.</p>
          </div>
        </template>
      </Card>
    </section>

    <!-- FLUJO TÍPICO -->
    <section id="flujo" class="manual-section">
      <h2><i class="pi pi-sitemap" /> Flujo típico de uso</h2>
      <Card class="manual-card">
        <template #content>
          <p>Orden recomendado para poner en marcha una promoción:</p>
          <ol class="manual-steps">
            <li><strong>Opcional:</strong> Crear una <a href="#carpetas">carpeta</a> (ej. "Promos Febrero") para agrupar descuentos y cuponeras.</li>
            <li><strong>Crear descuentos</strong> en la sección Descuentos: nombre obligatorio, tipo, scope, sedes y parámetros según el tipo.</li>
            <li><strong>Crear una cuponera</strong> en Cuponeras: definir vigencia (inicio/fin), usos por día por usuario y, en el calendario, asignar qué descuentos aplican cada día.</li>
            <li><strong>Registrar usuarios</strong> en la cuponera (nombre, teléfono, correo, y opcionalmente un código; si no se pone código, el sistema lo genera).</li>
            <li>En <strong>Consultar cupón</strong>, el cliente o caja ingresa el código (y opcionalmente la fecha) y elige "Consultar" o "Consultar y registrar uso" para ver los descuentos del día.</li>
          </ol>
        </template>
      </Card>
    </section>

    <!-- CARPETAS -->
    <section id="carpetas" class="manual-section">
      <h2><i class="pi pi-folder" /> Carpetas</h2>

      <h3 id="carpetas-que" class="manual-h3">Qué son y para qué sirven</h3>
      <Card class="manual-card">
        <template #content>
          <p>
            Las carpetas sirven para <strong>agrupar</strong> descuentos y cuponeras en la lista (por ejemplo: "Promos Febrero", "Black Friday"). <strong>No afectan la lógica de canje</strong>; solo la organización en pantalla y el filtrado en los listados.
          </p>
        </template>
      </Card>

      <h3 id="carpetas-crud" class="manual-h3">Crear, editar y eliminar</h3>
      <Card class="manual-card">
        <template #content>
          <ul>
            <li><strong>Crear:</strong> Nombre obligatorio. Descripción y orden son opcionales.</li>
            <li><strong>Editar:</strong> Puede cambiar nombre, descripción y orden en cualquier momento.</li>
            <li><strong>Eliminar:</strong> Al borrar una carpeta se aplica <strong>cascade</strong>: todos los descuentos y cuponeras que usaban esa carpeta quedan <em>sin carpeta</em> (campo vacío). <strong>No se borran</strong> los descuentos ni las cuponeras.</li>
          </ul>
          <div class="callout callout-warning">
            <strong><i class="pi pi-exclamation-triangle" /> Importante</strong>
            <p>Si no desea que ítems queden "sueltos", cambie antes la carpeta de esos descuentos/cuponeras a otra carpeta o déjela en "Sin carpeta" y luego elimine la carpeta vacía.</p>
          </div>
          <p><strong>Uso en formularios:</strong> En Descuentos y Cuponeras hay un campo <strong>Carpeta</strong> con un desplegable que lista las carpetas existentes. Si no elige ninguna, queda "Sin carpeta". Los listados permiten filtrar por carpeta y se muestran agrupados por carpeta.</p>
        </template>
      </Card>
    </section>

    <!-- DESCUENTOS -->
    <section id="descuentos" class="manual-section">
      <h2><i class="pi pi-percentage" /> Descuentos</h2>

      <h3 id="descuentos-nombre" class="manual-h3">Nombre obligatorio</h3>
      <Card class="manual-card highlight-card">
        <template #content>
          <p>
            <strong>Es obligatorio asignar un nombre al descuento antes de crearlo o guardar cambios.</strong> El nombre es un identificador interno para listados y reportes. En el formulario:
          </p>
          <ul>
            <li>Si deja el nombre vacío, el botón <strong>Guardar</strong> permanece deshabilitado.</li>
            <li>Debajo del campo aparece el mensaje <em>"El nombre es obligatorio."</em></li>
            <li>El backend también valida: si se envía un nombre vacío, la petición falla con error de validación.</li>
          </ul>
          <div class="callout callout-tip">
            <strong><i class="pi pi-check-circle" /> Consejo</strong>
            <p>Use nombres claros y descriptivos, por ejemplo: "10% carrito febrero", "2x1 perros", "Lleva 3 paga 2 hamburguesas".</p>
          </div>
        </template>
      </Card>

      <h3 id="descuentos-tipos" class="manual-h3">Tipos de descuento</h3>
      <Card class="manual-card">
        <template #content>
          <p>Debajo del selector de tipo verá una descripción del tipo elegido y, en muchos campos, iconos de información con tooltips. Resumen por tipo:</p>
          <div class="table-wrap">
            <table class="manual-table">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Descripción breve</th>
                  <th>Scope / parámetros clave</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><Tag value="% carrito" severity="info" /> CART_PERCENT_OFF</td>
                  <td>Porcentaje sobre el total del carrito.</td>
                  <td>No se seleccionan productos ni categorías. Opcional: tope en COP, compra mínima.</td>
                </tr>
                <tr>
                  <td><Tag value="Valor fijo" severity="info" /> CART_AMOUNT_OFF</td>
                  <td>Valor fijo en COP de descuento sobre el carrito.</td>
                  <td>Sin scope. Opcional: compra mínima.</td>
                </tr>
                <tr>
                  <td><Tag value="Producto gratis" severity="success" /> FREE_ITEM</td>
                  <td>Regala uno o más productos (más barato del scope o producto específico).</td>
                  <td>Scope: todos/categorías/productos. Requisito de compra opcional: ninguno, subtotal mín., cantidad mín. o "compra X unidades". Cantidad gratis máx.</td>
                </tr>
                <tr>
                  <td><Tag value="M x N" severity="warn" /> BUY_M_PAY_N</td>
                  <td>Lleva M paga N: por cada M unidades del <strong>mismo producto</strong>, paga N.</td>
                  <td>Scope: todos/categorías/productos. Parámetros M y N. Máx. grupos. No se mezclan productos.</td>
                </tr>
                <tr>
                  <td><Tag value="% categoría" severity="info" /> CATEGORY_PERCENT_OFF</td>
                  <td>Descuento en % solo sobre productos de ciertas categorías.</td>
                  <td>Debe elegir categorías en el scope. Opcional: tope COP, cantidad o subtotal mínimo.</td>
                </tr>
                <tr>
                  <td><Tag value="Compra X obtén Y %" severity="warn" /> BUY_X_GET_Y_PERCENT_OFF</td>
                  <td>Compra X lleva Y del <strong>mismo producto</strong> con % de descuento.</td>
                  <td>Scope: todos/categorías/productos. Parámetros X, Y, Y_discount_pct. Máx. grupos.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="callout callout-warning">
            <strong><i class="pi pi-exclamation-triangle" /> M x N y Compra X obtén Y %</strong>
            <p>Estas promociones aplican <strong>solo por el mismo producto</strong>: no se mezclan productos (3 de un artículo + 2 de otro no forman un grupo). Cada producto participa por separado.</p>
          </div>
        </template>
      </Card>

      <h3 id="descuentos-scope" class="manual-h3">Scope, sedes, prioridad y carpeta</h3>
      <Card class="manual-card">
        <template #content>
          <p><strong>Scope (a qué aplica):</strong> Para tipos que no son "todo el carrito" puede elegir: <strong>Todos los ítems</strong>, <strong>Categorías</strong> o <strong>Productos</strong>. Las categorías y productos se cargan desde el backend (menús de las sedes permitidas). Los IDs se validan contra esos menús al guardar.</p>
          <p><strong>Sedes:</strong> Si no elige ninguna, el descuento aplica en todas las sedes permitidas; si elige una o más, solo aplica en esas. En el listado se muestra "Todas" o la cantidad de sedes seleccionadas.</p>
          <p><strong>Prioridad:</strong> Cuando hay varios descuentos aplicables, se usa este número para ordenar (mayor = se evalúa antes).</p>
          <p><strong>Carpeta:</strong> Opcional, para agrupar en listados.</p>
        </template>
      </Card>

      <h3 id="descuentos-ejemplo" class="manual-h3">Ejemplo con productos reales</h3>
      <Card class="manual-card">
        <template #content>
          <p>
            Debajo del bloque de scope, si ha elegido categorías o productos, verá un <strong>recuadro de ejemplo</strong> con el texto del tipo de promoción usando los nombres reales de los ítems seleccionados, por ejemplo: <em>"Ej: Lleva 3 paga 2 en: Perro caliente, Hamburguesa clásica, …"</em>. Sirve para verificar que el descuento aplica a los productos correctos.
          </p>
        </template>
      </Card>
    </section>

    <!-- CUPONERAS -->
    <section id="cuponeras" class="manual-section">
      <h2><i class="pi pi-calendar" /> Cuponeras</h2>

      <h3 id="cuponeras-que" class="manual-h3">Qué es una cuponera</h3>
      <Card class="manual-card">
        <template #content>
          <p>
            Una cuponera es un "cuadernillo" de promociones por día: tiene un <strong>calendario</strong> donde cada fecha puede tener uno o más descuentos asignados. Los <strong>usuarios</strong> de la cuponera reciben un código; con ese código se consultan los descuentos del día (y opcionalmente se registra un uso en caja).
          </p>
        </template>
      </Card>

      <h3 id="cuponeras-vigencia" class="manual-h3">Vigencia (inicio y fin)</h3>
      <Card class="manual-card">
        <template #content>
          <p>Puede definir <strong>fecha de inicio</strong> y <strong>fecha de fin</strong> de vigencia con el selector de fecha (DatePicker). Si no los define, la cuponera no tiene límite de fechas. Si los define:</p>
          <ul>
            <li>Al <strong>consultar</strong> un código, si la fecha está fuera de vigencia, se muestra un mensaje (ej. "La cuponera ya finalizó. Vigencia hasta el …" o "La cuponera aún no ha comenzado.").</li>
            <li>En el <strong>calendario</strong> de la cuponera, solo puede asignar descuentos a días que caigan dentro de la vigencia; los días fuera aparecen bloqueados (no se puede hacer clic).</li>
          </ul>
        </template>
      </Card>

      <h3 id="cuponeras-calendario" class="manual-h3">Calendario: descuentos por día</h3>
      <Card class="manual-card">
        <template #content>
          <p>En el diálogo de crear/editar cuponera hay un calendario mensual. Haga clic en un día <em>dentro de la vigencia</em> para abrir un panel y elegir qué descuentos aplican ese día. Puede asignar varios descuentos por día. Los días con descuentos se marcan visualmente y muestran la cantidad asignada.</p>
          <p><strong>Usos por día por usuario:</strong> Valor numérico que indica cuántas veces puede cada usuario canjear/registrar uso por día (por defecto 1). Al elegir "Consultar y registrar uso" en Consultar cupón, se consume una de esas veces.</p>
        </template>
      </Card>

      <h3 id="cuponeras-usuarios" class="manual-h3">Usuarios y códigos</h3>
      <Card class="manual-card">
        <template #content>
          <p>Desde la lista de cuponeras puede entrar a <strong>Usuarios</strong> de una cuponera. Ahí puede:</p>
          <ul>
            <li><strong>Registrar usuario:</strong> nombre, teléfono, correo, dirección (opcional). El campo <strong>Código</strong> puede dejarse vacío (el sistema lo genera automáticamente) o escribirlo a mano.</li>
            <li><strong>Regla de códigos:</strong> No se permiten códigos duplicados en cuponeras <em>vigentes</em>. Si un código ya está usado en otra cuponera que sigue vigente, no podrá usarlo. En cambio, si el cliente tuvo ese código en una cuponera ya finalizada, puede <strong>reutilizar el mismo código</strong> en una cuponera nueva (renovar al cliente).</li>
            <li>Al <strong>consultar</strong> un código, si el cliente está en varias cuponeras (pasadas y vigente), el sistema devuelve siempre la <strong>cuponera vigente</strong>.</li>
          </ul>
          <div class="callout callout-tip">
            <strong><i class="pi pi-check-circle" /> Renovación de clientes</strong>
            <p>Puede crear una nueva cuponera para el siguiente período y asignar a los mismos clientes con su mismo código; el sistema permite reutilizar el código una vez la cuponera anterior haya terminado.</p>
          </div>
        </template>
      </Card>
    </section>

    <!-- CONSULTAR CUPÓN -->
    <section id="consultar" class="manual-section">
      <h2><i class="pi pi-ticket" /> Consultar cupón</h2>

      <h3 id="consultar-uso" class="manual-h3">Uso en caja</h3>
      <Card class="manual-card">
        <template #content>
          <p>En esta pantalla se ingresa el <strong>código</strong> del usuario. Por defecto se usa la fecha de hoy para ver los descuentos del día (puede cambiar la fecha si necesita consultar otro día).</p>
          <ul>
            <li><strong>Consultar:</strong> Solo muestra los descuentos del día y los usos restantes; <strong>no registra uso</strong>. Útil para que el cliente vea qué promos tiene.</li>
            <li><strong>Consultar y registrar uso:</strong> Además de mostrar, <strong>consume una</strong> de las veces permitidas por día para ese código. Úselo en caja cuando aplique el descuento al cliente.</li>
          </ul>
        </template>
      </Card>

      <h3 id="consultar-mensajes" class="manual-h3">Mensajes y respuestas</h3>
      <Card class="manual-card">
        <template #content>
          <p>Posibles respuestas del sistema:</p>
          <div class="table-wrap">
            <table class="manual-table">
              <thead>
                <tr>
                  <th>Situación</th>
                  <th>Mensaje / comportamiento</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Éxito</td>
                  <td>Lista de descuentos del día y usos restantes.</td>
                </tr>
                <tr>
                  <td>Sin descuentos para esa fecha</td>
                  <td>"No hay descuentos configurados para esta fecha".</td>
                </tr>
                <tr>
                  <td>Código no encontrado</td>
                  <td>"Código no válido".</td>
                </tr>
                <tr>
                  <td>Cuponera no activa</td>
                  <td>Mensaje indicando que la cuponera no está activa.</td>
                </tr>
                <tr>
                  <td>Fuera de vigencia (aún no empieza)</td>
                  <td>Mensaje tipo "La cuponera aún no ha comenzado." (vigencia inicio en el futuro).</td>
                </tr>
                <tr>
                  <td>Fuera de vigencia (ya terminó)</td>
                  <td>Mensaje tipo "La cuponera ya finalizó. Vigencia hasta el …".</td>
                </tr>
                <tr>
                  <td>Código solo en cuponeras pasadas</td>
                  <td>"No hay cuponera vigente para este código". El código existe pero solo en cuponeras ya finalizadas; puede renovar al cliente en una cuponera vigente con el mismo código.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </Card>
    </section>

    <!-- CONSIDERACIONES -->
    <section id="consideraciones" class="manual-section">
      <h2><i class="pi pi-exclamation-triangle" /> Consideraciones y buenas prácticas</h2>
      <Accordion v-model:value="accordionValue" multiple class="manual-accordion">
        <AccordionPanel value="0">
          <AccordionHeader>Sedes y menús</AccordionHeader>
          <AccordionContent>
            <p class="m-0">Solo se usan sedes con <code>time_zone = "America/Bogota"</code>, <code>show_on_web = true</code> y se excluye <code>site_id = 32</code>. Los productos y categorías de los descuentos se validan contra los menús de esas sedes. La sincronización de menús es periódica (cada 10 minutos).</p>
          </AccordionContent>
        </AccordionPanel>
        <AccordionPanel value="1">
          <AccordionHeader>Nombre del descuento</AccordionHeader>
          <AccordionContent>
            <p class="m-0">El nombre del descuento es <strong>obligatorio</strong> tanto en el frontend como en el backend. Asígnele siempre un nombre claro antes de guardar (por ejemplo: "10% carrito febrero", "2x1 perros").</p>
          </AccordionContent>
        </AccordionPanel>
        <AccordionPanel value="2">
          <AccordionHeader>M x N y Compra X obtén Y %</AccordionHeader>
          <AccordionContent>
            <p class="m-0">Estas promociones aplican <strong>por el mismo producto</strong>: no se mezclan productos (3 uvas + 2 manzanas no forman un grupo). Cada producto/categoría participa por separado.</p>
          </AccordionContent>
        </AccordionPanel>
        <AccordionPanel value="3">
          <AccordionHeader>Códigos y renovación</AccordionHeader>
          <AccordionContent>
            <p class="m-0">Puede reutilizar un código que ya no esté en una cuponera vigente. Así puede "renovar" al cliente en una nueva cuponera manteniendo su código. Al consultar, siempre se devuelve la cuponera vigente si hay varias.</p>
          </AccordionContent>
        </AccordionPanel>
        <AccordionPanel value="4">
          <AccordionHeader>Vigencia de cuponeras</AccordionHeader>
          <AccordionContent>
            <p class="m-0">Definir inicio y fin de vigencia evita que se canjee fuera de fecha y deja claro el período de la promoción. En el calendario de la cuponera solo se pueden asignar descuentos a días dentro de esa vigencia.</p>
          </AccordionContent>
        </AccordionPanel>
        <AccordionPanel value="5">
          <AccordionHeader>Carpetas y cascade</AccordionHeader>
          <AccordionContent>
            <p class="m-0">Al eliminar una carpeta con cascade, los descuentos y cuponeras que la usaban quedan sin carpeta; no se borran. Si no desea eso, cambie antes la carpeta de esos ítems a otra o déjela vacía.</p>
          </AccordionContent>
        </AccordionPanel>
        <AccordionPanel value="6">
          <AccordionHeader>Tooltips e información en formularios</AccordionHeader>
          <AccordionContent>
            <p class="m-0">En el formulario de descuentos hay iconos de información (ℹ) junto a muchas etiquetas; al pasar el cursor aparece un tooltip con la explicación del campo (por ejemplo: "Cantidad gratis máx.", "Máx. grupos"). Use estos tooltips para rellenar correctamente cada tipo de descuento.</p>
          </AccordionContent>
        </AccordionPanel>
      </Accordion>
    </section>

    <footer class="manual-footer">
      <p><i class="pi pi-heart-fill" /> Cuponera Salchimonster — Documentación del sistema. Consulte esta guía siempre que tenga dudas sobre el funcionamiento.</p>
    </footer>
  </div>
</template>

<style scoped>
.manual {
  max-width: 56rem;
  margin: 0 auto;
  padding: 0 1rem 3rem;
}
.manual-hero {
  text-align: center;
  padding: 2.5rem 1.5rem 3rem;
  background: linear-gradient(145deg, #ff6200 0%, #cc4e00 50%, #993b00 100%);
  color: #fff;
  border-radius: 20px;
  margin-bottom: 2rem;
  box-shadow: 0 12px 32px rgba(0,0,0,0.2);
}
.manual-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.9;
  margin-bottom: 1rem;
}
.manual-hero-badge i { font-size: 1rem; }
.manual-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  letter-spacing: -0.02em;
}
.manual-intro {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.65;
  opacity: 0.92;
  max-width: 36rem;
  margin-left: auto;
  margin-right: auto;
}
.manual-toc {
  background: #fff;
  border-radius: 14px;
  padding: 1.5rem 1.75rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid #e9ecef;
}
.manual-toc h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  font-size: 1.15rem;
  color: #333;
}
.manual-toc h2 i { color: #ff6200; }
.toc-list { margin: 0; padding-left: 1.5rem; }
.toc-list > li { margin-bottom: 0.5rem; }
.toc-list ul { margin: 0.25rem 0 0.5rem 0; padding-left: 1.25rem; list-style: none; }
.toc-list ul li { margin-bottom: 0.25rem; }
.toc-list a { color: #ff6200; text-decoration: none; }
.toc-list a:hover { text-decoration: underline; }
.manual-section {
  margin-bottom: 2.5rem;
  scroll-margin-top: 1rem;
}
.manual-section h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  color: #1a1a2e;
  margin: 0 0 1.25rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid #ff6200;
}
.manual-section h2 i { color: #ff6200; }
.manual-h3 {
  font-size: 1.2rem;
  color: #333;
  margin: 1.5rem 0 0.75rem 0;
  padding-left: 0.5rem;
  border-left: 4px solid #ff6200;
}
.manual-card {
  margin-bottom: 1rem;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  border: 1px solid #e9ecef;
}
.manual-card.highlight-card {
  border-color: #ff6200;
  box-shadow: 0 2px 12px rgba(255, 98, 0, 0.2);
}
.manual-card :deep(.p-card-body) { padding: 1.35rem 1.75rem; }
.manual-card :deep(.p-card-content) { padding: 0; }
.manual-card h3 { font-size: 1.05rem; color: #333; margin: 0 0 0.5rem 0; }
.manual-card p { margin: 0 0 0.75rem 0; line-height: 1.65; color: #495057; }
.manual-card p:last-child { margin-bottom: 0; }
.manual-card ul, .manual-card ol { margin: 0 0 0.75rem 0; padding-left: 1.35rem; color: #495057; line-height: 1.65; }
.manual-card li { margin-bottom: 0.35rem; }
.manual-card code { background: #f1f3f5; padding: 0.2rem 0.45rem; border-radius: 6px; font-size: 0.9em; color: #333; }
.manual-steps { list-style: none; padding-left: 0; counter-reset: step; }
.manual-steps li { position: relative; padding-left: 2rem; margin-bottom: 0.75rem; }
.manual-steps li::before {
  counter-increment: step;
  content: counter(step);
  position: absolute;
  left: 0;
  top: 0;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: #c41e3a;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1.5;
}
.callout {
  margin: 1rem 0 0;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  border-left: 4px solid #0d6efd;
}
.callout p { margin: 0.35rem 0 0; }
.callout p:first-of-type { margin-top: 0.25rem; }
.callout strong { display: flex; align-items: center; gap: 0.4rem; }
.callout-info { background: #e7f1ff; border-color: #0d6efd; color: #0c3d6b; }
.callout-tip { background: #e8f5e9; border-color: #2e7d32; color: #1b5e20; }
.callout-warning { background: #fff8e1; border-color: #f57c00; color: #e65100; }
.table-wrap { overflow-x: auto; margin: 1rem 0 0; }
.manual-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}
.manual-table th, .manual-table td {
  padding: 0.65rem 0.85rem;
  text-align: left;
  border: 1px solid #dee2e6;
}
.manual-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}
.manual-table tbody tr:nth-child(even) { background: #fafbfc; }
.manual-table :deep(.p-tag) { font-size: 0.8rem; }
.manual-accordion { margin-top: 0.5rem; }
.manual-accordion :deep(.p-accordion-header-link) { padding: 0.85rem 1.1rem; font-weight: 600; }
.manual-accordion :deep(.p-accordion-content) { padding: 1rem; }
.manual-footer {
  text-align: center;
  padding: 2rem 1rem;
  color: #6c757d;
  font-size: 0.95rem;
  border-top: 2px solid #dee2e6;
  margin-top: 2.5rem;
}
.manual-footer p { margin: 0; display: flex; align-items: center; justify-content: center; gap: 0.4rem; }
.manual-footer i { color: #ff6200; }
</style>

<style>
/* Modo oscuro: documentación */
html.theme-dark .manual .manual-hero {
  background: linear-gradient(145deg, #2d2d2d 0%, #1a1a1a 50%, #0d0d0d 100%);
  box-shadow: 0 12px 32px rgba(0,0,0,0.5);
}
html.theme-dark .manual .manual-toc {
  background: #252525;
  border-color: #404040;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
html.theme-dark .manual .manual-toc h2 {
  color: #e0e0e0;
}
html.theme-dark .manual .manual-toc h2 i {
  color: #ff6200;
}
html.theme-dark .manual .toc-list a {
  color: #ff9040;
}
html.theme-dark .manual .toc-list a:hover {
  color: #ffb380;
}
html.theme-dark .manual .manual-section h2 {
  color: #e8e8e8;
  border-bottom-color: #ff6200;
}
html.theme-dark .manual .manual-section h2 i {
  color: #ff6200;
}
html.theme-dark .manual .manual-h3 {
  color: #d0d0d0;
  border-left-color: #ff6200;
}
html.theme-dark .manual .manual-card,
html.theme-dark .manual .manual-card .p-card-body {
  background: #252525 !important;
  border-color: #404040 !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
}
html.theme-dark .manual .manual-card.highlight-card {
  border-color: #ff6200 !important;
  box-shadow: 0 2px 12px rgba(255, 98, 0, 0.25) !important;
}
html.theme-dark .manual .manual-card h3,
html.theme-dark .manual .manual-card p,
html.theme-dark .manual .manual-card ul,
html.theme-dark .manual .manual-card ol,
html.theme-dark .manual .manual-card li {
  color: #c8c8c8 !important;
}
html.theme-dark .manual .manual-card code {
  background: #1a1a1a !important;
  color: #e0e0e0 !important;
  border: 1px solid #404040;
}
html.theme-dark .manual .manual-steps li::before {
  background: #ff6200;
}
html.theme-dark .manual .callout-info {
  background: #1e2a3a;
  border-color: #3b82f6;
  color: #93c5fd;
}
html.theme-dark .manual .callout-info p {
  color: #93c5fd !important;
}
html.theme-dark .manual .callout-tip {
  background: #1a2e1a;
  border-color: #22c55e;
  color: #86efac;
}
html.theme-dark .manual .callout-tip p {
  color: #86efac !important;
}
html.theme-dark .manual .callout-warning {
  background: #2e251a;
  border-color: #f59e0b;
  color: #fcd34d;
}
html.theme-dark .manual .callout-warning p {
  color: #fcd34d !important;
}
html.theme-dark .manual .manual-table th,
html.theme-dark .manual .manual-table td {
  border-color: #404040 !important;
}
html.theme-dark .manual .manual-table th {
  background: #1a1a1a !important;
  color: #e0e0e0 !important;
}
html.theme-dark .manual .manual-table td {
  color: #c8c8c8 !important;
}
html.theme-dark .manual .manual-table tbody tr:nth-child(even) {
  background: #2d2d2d !important;
}
html.theme-dark .manual .manual-table tbody tr:nth-child(odd) {
  background: #252525 !important;
}
html.theme-dark .manual .manual-footer {
  border-top-color: #404040 !important;
  color: #9ca3af !important;
}
html.theme-dark .manual .manual-footer p {
  color: #9ca3af !important;
}
html.theme-dark .manual .manual-footer i {
  color: #ff6200;
}
/* Accordion PrimeVue dentro del manual en modo oscuro */
html.theme-dark .manual .manual-accordion .p-accordion-header-link {
  background: #252525 !important;
  border-color: #404040 !important;
  color: #e0e0e0 !important;
}
html.theme-dark .manual .manual-accordion .p-accordion-content {
  background: #1e1e1e !important;
  border-color: #404040 !important;
  color: #c8c8c8 !important;
}
</style>
