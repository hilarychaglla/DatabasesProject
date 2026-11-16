-- =====================================================================
-- Datos de ejemplo para afdb (sastrería / arreglos de ropa)
-- Orden de carga respeta las FK:
--   cliente -> prenda -> servicio -> precio_servicio -> pedido
--   -> detalle_pedido -> pago
-- Todos los datos son ficticios (cédulas, RUC, teléfonos y correos).
-- =====================================================================

SET NAMES utf8mb4;
USE `afdb`;

-- ---------------------------------------------------------------------
-- (Opcional) Reiniciar las tablas antes de volver a cargar.
-- Descomenta solo si quieres borrar todo y empezar de cero.
-- ---------------------------------------------------------------------
-- SET FOREIGN_KEY_CHECKS = 0;
-- TRUNCATE TABLE `pago`;
-- TRUNCATE TABLE `detalle_pedido`;
-- TRUNCATE TABLE `pedido`;
-- TRUNCATE TABLE `precio_servicio`;
-- TRUNCATE TABLE `servicio`;
-- TRUNCATE TABLE `prenda`;
-- TRUNCATE TABLE `cliente`;
-- SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------
-- 1) cliente  (7 personas + 3 empresas)
--    - empresa: apellido NULL, identificación solo RUC (13 dígitos)
--    - persona: cédula (10 dígitos) o RUC (13 dígitos)
--    - algunos clientes sin identificación (campos opcionales)
-- ---------------------------------------------------------------------
INSERT INTO `cliente`
  (`id_cliente`, `tipo_cliente`, `nombre`, `apellido`, `tipo_identificacion`,
   `numero_identificacion`, `telefono`, `direccion`, `email`, `fecha_registro`)
VALUES
  (1,  'persona', 'María Fernanda', 'Cevallos Andrade', 'cedula', '1004567891',
       '0991234501', 'Av. Cristóbal de Troya y Bolívar, Ibarra', 'mf.cevallos@example.com', '2026-08-12'),
  (2,  'persona', 'Carlos Andrés',  'Pozo Villacís',    'cedula', '1712345678',
       '0987654302', 'Calle Sucre 12-45, Atuntaqui', 'carlos.pozo@example.com', '2026-08-30'),
  (3,  'persona', 'Luisa',          'Narváez',          'cedula', '1003456782',
       '0998877603', NULL, NULL, '2026-09-05'),
  (4,  'persona', 'José Luis',      'Quilumbaquí',      'RUC',    '1712345679001',
       '0969988704', 'Av. Quiroga y Bolívar, Otavalo', 'jl.quilumbaqui@example.com', '2026-09-18'),
  (5,  'persona', 'Ana Lucía',      'Tapia Rea',        NULL,     NULL,
       '0983344505', NULL, 'analucia.tapia@example.com', '2026-10-02'),
  (6,  'empresa', 'Uniformes Imbabura S.A.', NULL,      'RUC',    '1091234567001',
       '062900606', 'Panamericana Norte km 3, Atuntaqui', 'compras@uniformesimbabura.example.com', '2026-10-10'),
  (7,  'empresa', 'Hotel Hacienda Los Lagos Cía. Ltda.', NULL, 'RUC', '1791234568001',
       '022345607', 'Vía a San Pablo del Lago s/n, Otavalo', 'administracion@hotellagos.example.com', '2026-10-15'),
  (8,  'empresa', 'Colegio Particular San Gabriel', NULL, 'RUC',  '1091234568001',
       '062955508', 'Calle Rocafuerte 4-20, Ibarra', 'secretaria@sangabriel.example.com', '2026-10-21'),
  (9,  'persona', 'Diego',          'Proaño',           'cedula', '1005678903',
       '0995566709', 'Urb. Los Ceibos, Ibarra', NULL, '2026-11-01'),
  (10, 'persona', 'Gabriela',       'Maldonado Cruz',   'cedula', '1718765432',
       '0974433810', 'Calle Bolívar 8-33, Cotacachi', 'gaby.maldonado@example.com', '2026-11-08');

-- ---------------------------------------------------------------------
-- 2) prenda
-- ---------------------------------------------------------------------
INSERT INTO `prenda` (`id_prenda`, `tipo_prenda`, `descripcion`) VALUES
  (1, 'Pantalón', 'Pantalón de vestir, casual o jean'),
  (2, 'Chaqueta', 'Chaqueta, saco o blazer'),
  (3, 'Camisa',   'Camisa de manga corta o larga');

-- ---------------------------------------------------------------------
-- 3) servicio
-- ---------------------------------------------------------------------
INSERT INTO `servicio` (`id_servicio`, `nombre_servicio`, `descripcion`) VALUES
  (1, 'Ajuste de medidas',  'Entallar, acortar o modificar medidas de la prenda'),
  (2, 'Dobladillo',         'Bota o bajo de la prenda'),
  (3, 'Cambio de cierre',   'Reemplazo de cierre dañado'),
  (4, 'Remiendo',           'Reparación de rotos, desgarros o costuras abiertas'),
  (5, 'Cambio de botones',  'Reposición o cambio de botones'),
  (6, 'Cambio de forro',    'Reemplazo del forro interior');

-- ---------------------------------------------------------------------
-- 4) precio_servicio  (0 < precio_minimo <= precio_maximo)
--    Son precios de EJEMPLO; reemplázalos por tu catálogo real (CSV).
-- ---------------------------------------------------------------------
INSERT INTO `precio_servicio`
  (`id_precio`, `id_servicio`, `id_prenda`, `descripcion_arreglo`, `precio_minimo`, `precio_maximo`)
VALUES
  -- Pantalón (1)
  (1,  2, 1, 'Bota de pantalón simple',           3.00,  5.00),
  (2,  2, 1, 'Bota de pantalón con puño',         4.00,  6.00),
  (3,  1, 1, 'Entallar cintura',                  5.00,  8.00),
  (4,  1, 1, 'Entallar piernas',                  6.00, 10.00),
  (5,  3, 1, 'Cambio de cierre',                  4.00,  6.00),
  (6,  4, 1, 'Remiendo en rodilla',               3.00,  7.00),
  -- Chaqueta (2)
  (7,  1, 2, 'Entallar costados',                10.00, 18.00),
  (8,  1, 2, 'Acortar mangas',                    8.00, 14.00),
  (9,  6, 2, 'Cambio de forro completo',         20.00, 35.00),
  (10, 3, 2, 'Cambio de cierre frontal',          6.00, 10.00),
  (11, 5, 2, 'Cambio de botones (por unidad)',    0.50,  1.50),
  -- Camisa (3)
  (12, 1, 3, 'Entallar costados',                 5.00,  9.00),
  (13, 1, 3, 'Acortar mangas',                    4.00,  7.00),
  (14, 5, 3, 'Cambio de botones (por unidad)',    0.50,  1.50),
  (15, 4, 3, 'Remiendo de codo',                  3.00,  6.00),
  (16, 2, 3, 'Dobladillo bajo de camisa',         3.00,  5.00);

-- ---------------------------------------------------------------------
-- 5) pedido
--    - 6 pedidos entregados (1-6) y 4 activos (7-10)
--    - fecha_entrega_estimada >= fecha de recepción
--    - entregada => fecha_hora_entrega_real NOT NULL; activa => NULL
--    - descuento: 0, o entre 5 y 10
--    - pedido 4: entregado con deuda (18.00) => lleva motivo de excepción
-- ---------------------------------------------------------------------
INSERT INTO `pedido`
  (`id_pedido`, `id_cliente`, `fecha_hora_recepcion`, `fecha_entrega_estimada`,
   `fecha_hora_entrega_real`, `estado`, `descuento_porcentaje`, `observaciones`,
   `motivo_excepcion_entrega`)
VALUES
  (1,  1,  '2026-10-20 09:15:00', '2026-10-23', '2026-10-23 16:40:00', 'entregada',  0.00,
       'Usar hilo azul marino', NULL),
  (2,  2,  '2026-10-22 11:30:00', '2026-10-27', '2026-10-27 10:05:00', 'entregada',  5.00,
       NULL, NULL),
  (3,  6,  '2026-10-28 08:30:00', '2026-11-04', '2026-11-04 15:20:00', 'entregada', 10.00,
       'Camisas de uniforme del personal', NULL),
  (4,  3,  '2026-11-02 14:10:00', '2026-11-06', '2026-11-07 09:30:00', 'entregada',  0.00,
       NULL, 'Clienta retiró la prenda por viaje urgente; se compromete a pagar el saldo la próxima semana'),
  (5,  4,  '2026-11-05 10:00:00', '2026-11-09', '2026-11-09 12:15:00', 'entregada',  0.00,
       NULL, NULL),
  (6,  5,  '2026-11-09 16:45:00', '2026-11-13', '2026-11-14 11:00:00', 'entregada',  0.00,
       'Entrega con un día de retraso por falta de hilo', NULL),
  (7,  7,  '2026-11-10 09:00:00', '2026-11-18', NULL,                  'activa',     5.00,
       'Uniformes de recepción del hotel', NULL),
  (8,  8,  '2026-11-11 08:20:00', '2026-11-20', NULL,                  'activa',    10.00,
       'Pantalones de uniforme de bachillerato', NULL),
  (9,  9,  '2026-11-13 15:30:00', '2026-11-17', NULL,                  'activa',     0.00,
       NULL, NULL),
  (10, 10, '2026-11-16 10:30:00', '2026-11-20', NULL,                  'activa',     0.00,
       'Necesita la prenda antes del sábado 21', NULL);

-- ---------------------------------------------------------------------
-- 6) detalle_pedido  (precio_acordado > 0, dentro del rango min/max)
--    usa_repuesto = true cuando el taller pone el repuesto (cierre, botón)
-- ---------------------------------------------------------------------
INSERT INTO `detalle_pedido`
  (`id_detalle`, `id_precio`, `id_pedido`, `precio_acordado`, `usa_repuesto`, `notas`)
VALUES
  -- Pedido 1 (total 9.00)
  (1,  1,  1,  4.00, false, 'Pantalón azul marino, tela gabardina'),
  (2,  5,  1,  5.00, true,  'Cierre negro de 18 cm'),
  -- Pedido 2 (total 27.00 - 5% = 25.65)
  (3,  8,  2, 12.00, false, 'Chaqueta gris a cuadros'),
  (4,  7,  2, 15.00, false, 'Chaqueta gris a cuadros, cuidar el calce del patrón'),
  -- Pedido 3 (total 19.00 - 10% = 17.10)
  (5,  13, 3,  5.50, false, 'Camisa blanca talla M'),
  (6,  13, 3,  5.50, false, 'Camisa blanca talla L'),
  (7,  14, 3,  1.00, true,  'Reposición de 1 botón blanco, camisa celeste'),
  (8,  12, 3,  7.00, false, 'Camisa blanca talla S'),
  -- Pedido 4 (total 38.00, se pagó 20.00 => deuda 18.00)
  (9,  9,  4, 30.00, false, 'Chaqueta negra, forro satinado color vino'),
  (10, 10, 4,  8.00, true,  'Cierre metálico negro de 60 cm'),
  -- Pedido 5 (total 10.50)
  (11, 3,  5,  7.00, false, 'Pantalón de vestir negro'),
  (12, 1,  5,  3.50, false, 'Pantalón de vestir negro'),
  -- Pedido 6 (total 10.00)
  (13, 12, 6,  6.00, false, 'Camisa rosada'),
  (14, 15, 6,  4.00, false, 'Camisa a cuadros, codo izquierdo'),
  -- Pedido 7 (total 31.00 - 5% = 29.45)
  (15, 7,  7, 16.00, false, 'Chaqueta azul marino, uniforme de recepción'),
  (16, 8,  7, 10.00, false, 'Chaqueta azul marino, uniforme de recepción'),
  (17, 2,  7,  5.00, false, 'Pantalón azul marino con puño'),
  -- Pedido 8 (total 12.00 - 10% = 10.80)
  (18, 1,  8,  3.50, false, 'Pantalón azul, talla 34'),
  (19, 1,  8,  3.50, false, 'Pantalón azul, talla 36'),
  (20, 5,  8,  5.00, true,  'Cierre azul de 16 cm'),
  -- Pedido 9 (total 13.00)
  (21, 4,  9,  8.00, false, 'Jean azul oscuro'),
  (22, 6,  9,  5.00, false, 'Jean azul oscuro, rotura de 5 cm'),
  -- Pedido 10 (total 15.50)
  (23, 7,  10, 14.00, false, 'Blazer beige'),
  (24, 11, 10,  1.50, false, 'Botón dorado de 22 mm, lo trae la clienta');

-- ---------------------------------------------------------------------
-- 7) pago  (monto > 0; tipo: adelanto | saldo_final;
--           método: efectivo | transferencia | cheque)
-- ---------------------------------------------------------------------
INSERT INTO `pago`
  (`id_pago`, `id_pedido`, `monto`, `fecha_hora_pago`, `tipo_pago`, `metodo_pago`)
VALUES
  (1,  1,  4.00,  '2026-10-20 09:20:00', 'adelanto',    'efectivo'),
  (2,  1,  5.00,  '2026-10-23 16:35:00', 'saldo_final', 'efectivo'),
  (3,  2,  10.00, '2026-10-22 11:40:00', 'adelanto',    'transferencia'),
  (4,  2,  15.65, '2026-10-27 10:00:00', 'saldo_final', 'transferencia'),
  (5,  3,  8.00,  '2026-10-28 08:45:00', 'adelanto',    'cheque'),
  (6,  3,  9.10,  '2026-11-04 15:15:00', 'saldo_final', 'transferencia'),
  (7,  4,  20.00, '2026-11-02 14:20:00', 'adelanto',    'efectivo'),
  (8,  5,  5.00,  '2026-11-05 10:05:00', 'adelanto',    'efectivo'),
  (9,  5,  5.50,  '2026-11-09 12:10:00', 'saldo_final', 'efectivo'),
  (10, 6,  3.00,  '2026-11-09 16:50:00', 'adelanto',    'efectivo'),
  (11, 6,  7.00,  '2026-11-14 10:55:00', 'saldo_final', 'transferencia'),
  (12, 7,  15.00, '2026-11-10 09:10:00', 'adelanto',    'transferencia'),
  (13, 8,  5.00,  '2026-11-11 08:30:00', 'adelanto',    'cheque'),
  (14, 9,  6.50,  '2026-11-13 15:40:00', 'adelanto',    'efectivo'),
  (15, 10, 5.00,  '2026-11-16 10:35:00', 'adelanto',    'efectivo');

-- ---------------------------------------------------------------------
-- Verificación rápida (opcional)
-- ---------------------------------------------------------------------
-- SELECT 'cliente' AS tabla, COUNT(*) AS filas FROM cliente
-- UNION ALL SELECT 'prenda', COUNT(*) FROM prenda
-- UNION ALL SELECT 'servicio', COUNT(*) FROM servicio
-- UNION ALL SELECT 'precio_servicio', COUNT(*) FROM precio_servicio
-- UNION ALL SELECT 'pedido', COUNT(*) FROM pedido
-- UNION ALL SELECT 'detalle_pedido', COUNT(*) FROM detalle_pedido
-- UNION ALL SELECT 'pago', COUNT(*) FROM pago;
--
-- SELECT * FROM v_pedido_resumen;
-- SELECT * FROM v_cliente_saldo;   -- debería salir solo Luisa Narváez con 18.00
