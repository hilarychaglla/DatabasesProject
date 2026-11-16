"""Aguja Fina - Lab SQLAlchemy 02: sql01 + POST/PUT/DELETE y reglas de negocio."""
import os
from decimal import Decimal, ROUND_HALF_UP

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask.json.provider import DefaultJSONProvider
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

load_dotenv()  # lee el archivo .env (credenciales fuera del código, NFR-07)

CENT = Decimal("0.01")
# Nombre de la columna de deuda en la vista v_cliente_saldo (ajústalo al de tu DDL)
SALDO_COL = "saldo_pendiente"


class JSONProvider(DefaultJSONProvider):
    """Serializa Decimal como número y no escapa las tildes."""
    ensure_ascii = False

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


app = Flask(__name__)
app.json = JSONProvider(app)

app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    "mysql+pymysql",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ.get("DB_HOST", "127.0.0.1"),
    port=int(os.environ.get("DB_PORT", 3306)),
    database=os.environ["DB_NAME"],
    query={"charset": "utf8mb4"},
)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# ---------------------------------------------------------------
# MODELOS (las tablas ya existen por el DDL: NO se usa db.create_all())
# ---------------------------------------------------------------
FV = db.FetchedValue  # columnas con DEFAULT definido en MySQL


class Cliente(db.Model):
    __tablename__ = "cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    tipo_cliente = db.Column(db.String(7), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    apellido = db.Column(db.String(100))
    tipo_identificacion = db.Column(db.String(20))
    numero_identificacion = db.Column(db.String(20))
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200))
    email = db.Column(db.String(120))
    fecha_registro = db.Column(db.Date, nullable=False, server_default=FV())


class Prenda(db.Model):
    __tablename__ = "prenda"
    id_prenda = db.Column(db.Integer, primary_key=True)
    tipo_prenda = db.Column(db.String(60), nullable=False)
    descripcion = db.Column(db.String(200))


class Servicio(db.Model):
    __tablename__ = "servicio"
    id_servicio = db.Column(db.Integer, primary_key=True)
    nombre_servicio = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(200))


class PrecioServicio(db.Model):
    __tablename__ = "precio_servicio"
    id_precio = db.Column(db.Integer, primary_key=True)
    id_servicio = db.Column(db.Integer, db.ForeignKey("servicio.id_servicio"), nullable=False)
    id_prenda = db.Column(db.Integer, db.ForeignKey("prenda.id_prenda"), nullable=False)
    descripcion_arreglo = db.Column(db.String(120), nullable=False)
    precio_minimo = db.Column(db.Numeric(8, 2), nullable=False)
    precio_maximo = db.Column(db.Numeric(8, 2), nullable=False)


class Pedido(db.Model):
    __tablename__ = "pedido"
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"), nullable=False)
    fecha_hora_recepcion = db.Column(db.DateTime, nullable=False, server_default=FV())
    fecha_entrega_estimada = db.Column(db.Date, nullable=False)
    fecha_hora_entrega_real = db.Column(db.DateTime)
    estado = db.Column(db.String(10), nullable=False, server_default=FV())
    descuento_porcentaje = db.Column(db.Numeric(4, 2), nullable=False, server_default=FV())
    observaciones = db.Column(db.String(255))
    motivo_excepcion_entrega = db.Column(db.String(255))
    detalles = db.relationship("DetallePedido", backref="pedido")
    pagos = db.relationship("Pago", backref="pedido")


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_precio = db.Column(db.Integer, db.ForeignKey("precio_servicio.id_precio"), nullable=False)
    precio_acordado = db.Column(db.Numeric(8, 2), nullable=False)
    usa_repuesto = db.Column(db.Boolean, nullable=False, server_default=FV())
    notas = db.Column(db.String(255))


class Pago(db.Model):
    __tablename__ = "pago"
    id_pago = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_hora_pago = db.Column(db.DateTime, nullable=False, server_default=FV())
    tipo_pago = db.Column(db.String(12), nullable=False)
    metodo_pago = db.Column(db.String(15))


# ---------------------------------------------------------------
# ESQUEMAS MARSHMALLOW
# ---------------------------------------------------------------
class ClienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cliente
        dump_only = ("id_cliente", "fecha_registro")


class PrendaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Prenda
        dump_only = ("id_prenda",)


class ServicioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Servicio
        dump_only = ("id_servicio",)


class PrecioServicioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PrecioServicio
        include_fk = True
        dump_only = ("id_precio",)


class DetallePedidoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DetallePedido
        include_fk = True
        dump_only = ("id_detalle",)


class PagoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pago
        include_fk = True
        dump_only = ("id_pago", "fecha_hora_pago")


class PedidoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pedido
        include_fk = True
        dump_only = ("id_pedido", "fecha_hora_recepcion", "fecha_hora_entrega_real",
                     "estado", "motivo_excepcion_entrega")

    detalles = ma.Nested(DetallePedidoSchema, many=True, dump_only=True)
    pagos = ma.Nested(PagoSchema, many=True, dump_only=True)


cliente_schema = ClienteSchema()
prenda_schema = PrendaSchema()
servicio_schema = ServicioSchema()
precio_schema = PrecioServicioSchema()
pedido_schema = PedidoSchema()


# ---------------------------------------------------------------
# UTILIDADES Y MANEJO DE ERRORES
# ---------------------------------------------------------------
def calcular_resumen(pedido):
    """Totales derivados (nunca almacenados): subtotal, descuento, total, pagado y saldo."""
    subtotal = sum((d.precio_acordado for d in pedido.detalles), Decimal("0"))
    descuento = (subtotal * pedido.descuento_porcentaje / 100).quantize(CENT, ROUND_HALF_UP)
    total = subtotal - descuento
    pagado = sum((p.monto for p in pedido.pagos), Decimal("0"))
    return {"subtotal": subtotal, "descuento": descuento, "total": total,
            "pagado": pagado, "saldo": total - pagado}


@app.errorhandler(ValidationError)
def manejar_validacion(e):
    return jsonify({"error": "Datos inválidos", "detalle": e.messages}), 400


@app.errorhandler(IntegrityError)
def manejar_integridad(e):
    db.session.rollback()
    return jsonify({"error": "Restricción de la base de datos", "detalle": str(e.orig)}), 409


@app.errorhandler(HTTPException)
def manejar_http(e):
    return jsonify({"error": e.description}), e.code


# ---------------------------------------------------------------
# ENDPOINTS GET
# ---------------------------------------------------------------
# curl http://127.0.0.1:5000/health
@app.route("/health")
def health():
    db.session.execute(text("SELECT 1"))  # comprueba la conexión a MySQL
    return jsonify({"status": "ok", "db": "conectada"})


# curl "http://127.0.0.1:5000/clientes?q=0991"   (FR-02: busca por nombre o teléfono)
@app.route("/clientes", methods=["GET"])
def get_clientes():
    q = request.args.get("q", "").strip()
    consulta = db.select(Cliente)
    if q:
        like = f"%{q}%"
        consulta = consulta.where(db.or_(Cliente.nombre.ilike(like),
                                         Cliente.apellido.ilike(like),
                                         Cliente.telefono.like(like)))
    clientes = db.session.scalars(consulta.order_by(Cliente.nombre)).all()
    return jsonify({"clientes": ClienteSchema(many=True).dump(clientes)})


# curl http://127.0.0.1:5000/clientes/1
@app.route("/clientes/<int:id>", methods=["GET"])
def get_cliente(id):
    return jsonify(cliente_schema.dump(db.get_or_404(Cliente, id)))


# curl http://127.0.0.1:5000/clientes/1/saldo   (FR-03: alerta de deuda, usa la vista)
@app.route("/clientes/<int:id>/saldo", methods=["GET"])
def get_saldo_cliente(id):
    fila = db.session.execute(text("SELECT * FROM v_cliente_saldo WHERE id_cliente = :id"),
                              {"id": id}).mappings().first()
    if fila is None:
        return jsonify({"id_cliente": id, "mensaje": "Sin saldo registrado"})
    return jsonify(dict(fila))


# curl http://127.0.0.1:5000/prendas
@app.route("/prendas", methods=["GET"])
def get_prendas():
    prendas = db.session.scalars(db.select(Prenda).order_by(Prenda.tipo_prenda)).all()
    return jsonify({"prendas": PrendaSchema(many=True).dump(prendas)})


# curl http://127.0.0.1:5000/servicios
@app.route("/servicios", methods=["GET"])
def get_servicios():
    servicios = db.session.scalars(db.select(Servicio).order_by(Servicio.nombre_servicio)).all()
    return jsonify({"servicios": ServicioSchema(many=True).dump(servicios)})


# Cascada paso 2 (FR-05): servicios disponibles para una prenda
# curl http://127.0.0.1:5000/prendas/1/servicios
@app.route("/prendas/<int:id>/servicios", methods=["GET"])
def get_servicios_de_prenda(id):
    consulta = (db.select(Servicio).join(PrecioServicio,
                PrecioServicio.id_servicio == Servicio.id_servicio)
                .where(PrecioServicio.id_prenda == id).distinct()
                .order_by(Servicio.nombre_servicio))
    servicios = db.session.scalars(consulta).all()
    return jsonify({"servicios": ServicioSchema(many=True).dump(servicios)})


# Cascada paso 3: descripciones con precio mínimo y máximo
# curl "http://127.0.0.1:5000/precios?id_prenda=1&id_servicio=2"
@app.route("/precios", methods=["GET"])
def get_precios():
    consulta = db.select(PrecioServicio)
    if request.args.get("id_prenda"):
        consulta = consulta.where(PrecioServicio.id_prenda == request.args.get("id_prenda", type=int))
    if request.args.get("id_servicio"):
        consulta = consulta.where(PrecioServicio.id_servicio == request.args.get("id_servicio", type=int))
    precios = db.session.scalars(consulta.order_by(PrecioServicio.descripcion_arreglo)).all()
    return jsonify({"precios": PrecioServicioSchema(many=True).dump(precios)})


# curl "http://127.0.0.1:5000/pedidos?id_cliente=1&estado=activa"   (FR-12)
@app.route("/pedidos", methods=["GET"])
def get_pedidos():
    consulta = db.select(Pedido)
    if request.args.get("id_cliente"):
        consulta = consulta.where(Pedido.id_cliente == request.args.get("id_cliente", type=int))
    if request.args.get("estado"):
        consulta = consulta.where(Pedido.estado == request.args.get("estado"))
    pedidos = db.session.scalars(consulta.order_by(Pedido.fecha_hora_recepcion.desc())).all()
    esquema = PedidoSchema(many=True, exclude=("detalles", "pagos"))
    return jsonify({"pedidos": esquema.dump(pedidos)})


# curl http://127.0.0.1:5000/pedidos/1
@app.route("/pedidos/<int:id>", methods=["GET"])
def get_pedido(id):
    pedido = db.get_or_404(Pedido, id)
    return jsonify({**pedido_schema.dump(pedido), "resumen": calcular_resumen(pedido)})


# curl http://127.0.0.1:5000/pedidos/1/resumen   (FR-11)
@app.route("/pedidos/<int:id>/resumen", methods=["GET"])
def get_resumen_pedido(id):
    return jsonify(calcular_resumen(db.get_or_404(Pedido, id)))


# curl http://127.0.0.1:5000/reportes/clientes-con-saldo   (FR-19)
@app.route("/reportes/clientes-con-saldo", methods=["GET"])
def reporte_clientes_con_saldo():
    filas = db.session.execute(text(f"SELECT * FROM v_cliente_saldo WHERE {SALDO_COL} > 0")).mappings().all()
    return jsonify({"clientes": [dict(f) for f in filas]})


# ---------------------------------------------------------------
# LAB 02: CRUD GENÉRICO (cliente, prenda, servicio, precio_servicio)  -> FR-01, FR-16, FR-17
# ---------------------------------------------------------------
def crear(Model, schema):
    datos = schema.load(request.get_json(force=True))
    obj = Model(**datos)
    db.session.add(obj)
    db.session.commit()
    return jsonify(schema.dump(obj)), 201


def actualizar(Model, schema, id):
    obj = db.get_or_404(Model, id)
    datos = schema.load(request.get_json(force=True), partial=True)
    for campo, valor in datos.items():
        setattr(obj, campo, valor)
    db.session.commit()
    return jsonify(schema.dump(obj))


def eliminar(Model, id):
    obj = db.get_or_404(Model, id)
    db.session.delete(obj)  # ON DELETE RESTRICT -> 409 si tiene registros hijos
    db.session.commit()
    return jsonify({"message": f"{Model.__tablename__} {id} eliminado"})


def registrar_crud(ruta, Model, schema):
    app.add_url_rule(f"/{ruta}", f"crear_{ruta}", lambda: crear(Model, schema), methods=["POST"])
    app.add_url_rule(f"/{ruta}/<int:id>", f"actualizar_{ruta}",
                     lambda id: actualizar(Model, schema, id), methods=["PUT"])
    app.add_url_rule(f"/{ruta}/<int:id>", f"eliminar_{ruta}",
                     lambda id: eliminar(Model, id), methods=["DELETE"])


# curl -X POST -H "Content-Type: application/json" \
#   -d '{"tipo_cliente":"persona","nombre":"Ana","apellido":"Pérez","telefono":"0991234567"}' \
#   http://127.0.0.1:5000/clientes
# curl -X PUT -H "Content-Type: application/json" -d '{"direccion":"Ibarra"}' http://127.0.0.1:5000/clientes/1
# curl -X DELETE http://127.0.0.1:5000/clientes/1
registrar_crud("clientes", Cliente, cliente_schema)
registrar_crud("prendas", Prenda, prenda_schema)
registrar_crud("servicios", Servicio, servicio_schema)
registrar_crud("precios", PrecioServicio, precio_schema)


# ---------------------------------------------------------------
# REGLAS DE NEGOCIO: PEDIDOS, PAGOS Y ENTREGA
# ---------------------------------------------------------------
def a_decimal(valor, campo):
    try:
        return Decimal(str(valor))
    except Exception:
        raise ValidationError({campo: ["Debe ser un número."]})


# FR-04, FR-08, FR-09: pedido con una o más líneas y precio acordado dentro del rango
# curl -X POST -H "Content-Type: application/json" -d '{
#   "id_cliente": 1, "fecha_entrega_estimada": "2026-12-01", "descuento_porcentaje": 5,
#   "observaciones": "Urgente",
#   "detalles": [{"id_precio": 1, "precio_acordado": 3.50, "usa_repuesto": false, "notas": "azul"}]
# }' http://127.0.0.1:5000/pedidos
@app.route("/pedidos", methods=["POST"])
def crear_pedido():
    payload = request.get_json(force=True)
    lineas = payload.pop("detalles", None)
    if not lineas:
        raise ValidationError({"detalles": ["El pedido debe tener al menos una línea."]})

    datos = PedidoSchema(exclude=("detalles", "pagos")).load(payload)
    lineas = DetallePedidoSchema(many=True, exclude=("id_pedido",)).load(lineas)

    if db.session.get(Cliente, datos["id_cliente"]) is None:
        return jsonify({"error": "El cliente no existe"}), 404

    pedido = Pedido(**datos)
    for linea in lineas:
        precio = db.session.get(PrecioServicio, linea["id_precio"])
        if precio is None:
            return jsonify({"error": f"id_precio {linea['id_precio']} no existe"}), 400
        if not (precio.precio_minimo <= linea["precio_acordado"] <= precio.precio_maximo):
            return jsonify({"error": "Precio acordado fuera de rango",
                            "id_precio": precio.id_precio,
                            "minimo": precio.precio_minimo,
                            "maximo": precio.precio_maximo}), 400
        pedido.detalles.append(DetallePedido(**linea))

    db.session.add(pedido)
    db.session.commit()
    return jsonify({**pedido_schema.dump(pedido), "resumen": calcular_resumen(pedido)}), 201


# FR-10: registrar adelanto (el monto no puede superar el saldo)
# curl -X POST -H "Content-Type: application/json" -d '{"monto": 2, "metodo_pago": "efectivo"}' \
#   http://127.0.0.1:5000/pedidos/1/pagos
@app.route("/pedidos/<int:id>/pagos", methods=["POST"])
def registrar_pago(id):
    pedido = db.get_or_404(Pedido, id)
    if pedido.estado != "activa":
        return jsonify({"error": "El pedido ya fue entregado"}), 409

    payload = request.get_json(force=True)
    payload.setdefault("tipo_pago", "adelanto")
    datos = PagoSchema(exclude=("id_pedido",)).load(payload)

    saldo = calcular_resumen(pedido)["saldo"]
    if datos["monto"] > saldo:
        return jsonify({"error": "El monto supera el saldo pendiente", "saldo": saldo}), 400

    pago = Pago(id_pedido=id, **datos)
    db.session.add(pago)
    db.session.commit()
    db.session.refresh(pedido)
    return jsonify({"pago": PagoSchema().dump(pago), "resumen": calcular_resumen(pedido)}), 201


# FR-13, FR-14, FR-15: pago final + entrega (con deuda exige motivo)
# curl -X POST -H "Content-Type: application/json" \
#   -d '{"monto_final": 1.5, "metodo_pago": "efectivo"}' http://127.0.0.1:5000/pedidos/1/entregar
# curl -X POST -H "Content-Type: application/json" \
#   -d '{"motivo_excepcion_entrega": "Cliente frecuente, paga el lunes"}' http://127.0.0.1:5000/pedidos/1/entregar
@app.route("/pedidos/<int:id>/entregar", methods=["POST"])
def entregar_pedido(id):
    pedido = db.get_or_404(Pedido, id)
    if pedido.estado != "activa":
        return jsonify({"error": "El pedido ya fue entregado"}), 409

    datos = request.get_json(silent=True) or {}
    saldo = calcular_resumen(pedido)["saldo"]
    monto_final = a_decimal(datos.get("monto_final") or 0, "monto_final")
    if monto_final < 0 or monto_final > saldo:
        return jsonify({"error": "monto_final inválido", "saldo": saldo}), 400

    saldo_restante = saldo - monto_final
    motivo = (datos.get("motivo_excepcion_entrega") or "").strip()
    if saldo_restante > 0 and not motivo:
        return jsonify({"error": "Entrega con deuda pendiente: se requiere motivo_excepcion_entrega",
                        "saldo_restante": saldo_restante}), 400

    if monto_final > 0:
        db.session.add(Pago(id_pedido=id, monto=monto_final, tipo_pago="saldo_final",
                            metodo_pago=datos.get("metodo_pago")))
    pedido.estado = "entregada"
    pedido.fecha_hora_entrega_real = db.func.now()
    pedido.motivo_excepcion_entrega = motivo if saldo_restante > 0 else None
    db.session.commit()
    db.session.refresh(pedido)
    return jsonify({**pedido_schema.dump(pedido), "resumen": calcular_resumen(pedido)})


# ===== EJECUCIÓN =====
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
