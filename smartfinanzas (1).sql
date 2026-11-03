-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 03-11-2026 a las 16:27:26
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `smartfinanzas`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cargafinanciera`
--

CREATE TABLE `cargafinanciera` (
  `id` int(11) NOT NULL,
  `fecha_carga` datetime DEFAULT NULL,
  `periodo` varchar(20) DEFAULT NULL,
  `archivo_origen` varchar(255) DEFAULT NULL,
  `tipo_carga` varchar(20) DEFAULT NULL,
  `activo_corriente` decimal(14,2) DEFAULT NULL,
  `pasivo_corriente` decimal(14,2) DEFAULT NULL,
  `activo_total` decimal(14,2) DEFAULT NULL,
  `pasivo_total` decimal(14,2) DEFAULT NULL,
  `patrimonio` decimal(14,2) DEFAULT NULL,
  `ingresos_netos` decimal(14,2) DEFAULT NULL,
  `ebit` decimal(14,2) DEFAULT NULL,
  `utilidades_retenidas` decimal(14,2) DEFAULT NULL,
  `utilidad_neta` decimal(14,2) DEFAULT NULL,
  `inventarios` decimal(14,2) DEFAULT NULL,
  `efectivo_equivalentes` decimal(14,2) DEFAULT NULL,
  `estado` varchar(30) DEFAULT NULL,
  `errores_detectados` text DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cierrecaja`
--

CREATE TABLE `cierrecaja` (
  `id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `estado` varchar(15) DEFAULT NULL,
  `total_sistema` decimal(12,2) DEFAULT NULL,
  `total_retiros` decimal(12,2) DEFAULT NULL,
  `total_arqueo` decimal(12,2) DEFAULT NULL,
  `descuadre_total` decimal(12,2) DEFAULT NULL,
  `cerrado_por_usuario_id` int(11) DEFAULT NULL,
  `fecha_confirmacion` datetime DEFAULT NULL,
  `revisado_por_usuario_id` int(11) DEFAULT NULL,
  `fecha_revision` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracionempresa`
--

CREATE TABLE `configuracionempresa` (
  `id` int(11) NOT NULL,
  `razon_social` varchar(200) NOT NULL,
  `rut` varchar(15) NOT NULL,
  `giro` varchar(150) DEFAULT NULL,
  `comision_debito_pct` decimal(5,2) DEFAULT NULL,
  `comision_credito_pct` decimal(5,2) DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `configuracionempresa`
--

INSERT INTO `configuracionempresa` (`id`, `razon_social`, `rut`, `giro`, `comision_debito_pct`, `comision_credito_pct`, `fecha_actualizacion`) VALUES
(1, 'Nstock Importaciones', '76.123.456-7', 'Distribuidora e importadora mayorista', 1.75, 2.35, '2026-11-03 12:25:42');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detallecierrepormetodo`
--

CREATE TABLE `detallecierrepormetodo` (
  `id` int(11) NOT NULL,
  `cierre_id` int(11) NOT NULL,
  `metodo_pago_id` int(11) NOT NULL,
  `total_sistema` decimal(12,2) DEFAULT NULL,
  `total_arqueo` decimal(12,2) DEFAULT NULL,
  `descuadre` decimal(10,2) DEFAULT NULL,
  `justificacion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informepdf`
--

CREATE TABLE `informepdf` (
  `id` int(11) NOT NULL,
  `prediccion_id` int(11) DEFAULT NULL,
  `fecha_generacion` datetime DEFAULT NULL,
  `ruta_archivo` varchar(500) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodopago`
--

CREATE TABLE `metodopago` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `comision_porcentaje` decimal(5,2) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `metodopago`
--

INSERT INTO `metodopago` (`id`, `nombre`, `comision_porcentaje`, `activo`) VALUES
(1, 'Efectivo', 0.00, 1),
(2, 'Débito', 1.75, 1),
(3, 'Crédito', 2.35, 1),
(4, 'Transferencia', 0.00, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prediccionriesgo`
--

CREATE TABLE `prediccionriesgo` (
  `id` int(11) NOT NULL,
  `ratio_id` int(11) DEFAULT NULL,
  `fecha_prediccion` datetime DEFAULT NULL,
  `score_riesgo` decimal(5,2) DEFAULT NULL,
  `nivel_semaforo` varchar(10) DEFAULT NULL,
  `variables_influyentes` text DEFAULT NULL,
  `impacto_variables` text DEFAULT NULL,
  `version_modelo` varchar(20) DEFAULT NULL,
  `tiempo_inferencia_ms` int(11) DEFAULT NULL,
  `ejecutada_por_usuario_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ratiofinanciero`
--

CREATE TABLE `ratiofinanciero` (
  `id` int(11) NOT NULL,
  `carga_id` int(11) DEFAULT NULL,
  `periodo` varchar(20) DEFAULT NULL,
  `fecha_calculo` datetime DEFAULT NULL,
  `v1_razon_corriente` decimal(8,4) DEFAULT NULL,
  `v2_capital_trabajo_activos` decimal(8,4) DEFAULT NULL,
  `v3_leverage_total` decimal(8,4) DEFAULT NULL,
  `v4_roa_operacional` decimal(8,4) DEFAULT NULL,
  `v5_margen_operacional` decimal(8,4) DEFAULT NULL,
  `v6_rotacion_activos` decimal(8,4) DEFAULT NULL,
  `v7_volatilidad_flujo` decimal(8,4) DEFAULT NULL,
  `cierres_confirmados_count` int(11) DEFAULT NULL,
  `usa_volatilidad_neutra` tinyint(1) DEFAULT NULL,
  `ref_prueba_acida` decimal(8,4) DEFAULT NULL,
  `ref_razon_caja` decimal(8,4) DEFAULT NULL,
  `ref_cobertura_operacional` decimal(8,4) DEFAULT NULL,
  `ref_z_altman` decimal(8,4) DEFAULT NULL,
  `validado` tinyint(1) DEFAULT NULL,
  `validado_por_usuario_id` int(11) DEFAULT NULL,
  `fecha_validacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recomendacion`
--

CREATE TABLE `recomendacion` (
  `id` int(11) NOT NULL,
  `prediccion_id` int(11) NOT NULL,
  `variable_origen` varchar(50) DEFAULT NULL,
  `grupo_riesgo` varchar(40) DEFAULT NULL,
  `texto` text DEFAULT NULL,
  `prioridad` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `retirocajachica`
--

CREATE TABLE `retirocajachica` (
  `id` int(11) NOT NULL,
  `fecha` datetime DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `responsable` varchar(100) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `cierre_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--

CREATE TABLE `rol` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `rol`
--

INSERT INTO `rol` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Dueño', 'Gerencia, visualización de dashboard, registro de retiros de caja chica y cuadratura diaria'),
(2, 'Contador', 'Carga de planillas ETL, ejecución de predicciones y revisión de cierres'),
(3, 'Trabajador', 'Registro de ventas operativas con método de pago y descuentos diarios'),
(4, 'Administrador', 'Gestión técnica de usuarios, roles y permisos de la plataforma');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `rol_id` int(11) DEFAULT NULL,
  `empresa_id` int(11) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `ultima_sesion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `username`, `email`, `password_hash`, `rol_id`, `empresa_id`, `activo`, `fecha_creacion`, `ultima_sesion`) VALUES
(1, 'Alexis', 'admin@nstock.cl', 'pbkdf2_sha256$260000$dummyhashparainiciar', 4, 1, 1, '2026-11-03 12:25:42', NULL),
(2, 'admin', 'admin@admin.cl', 'pbkdf2_sha256$260000$dummyhashparainiciar', 4, NULL, 1, '2026-11-03 12:25:42', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `venta`
--

CREATE TABLE `venta` (
  `id` int(11) NOT NULL,
  `fecha` datetime DEFAULT NULL,
  `metodo_pago_id` int(11) DEFAULT NULL,
  `total_bruto` decimal(10,2) DEFAULT NULL,
  `descuento_tipo` varchar(10) DEFAULT NULL,
  `descuento_monto` decimal(10,2) DEFAULT NULL,
  `total_cobrado` decimal(10,2) DEFAULT NULL,
  `comision_aplicada` decimal(10,2) DEFAULT NULL,
  `ingreso_real` decimal(10,2) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `cierre_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cargafinanciera`
--
ALTER TABLE `cargafinanciera`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `cierrecaja`
--
ALTER TABLE `cierrecaja`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `fecha` (`fecha`),
  ADD KEY `cerrado_por_usuario_id` (`cerrado_por_usuario_id`),
  ADD KEY `revisado_por_usuario_id` (`revisado_por_usuario_id`);

--
-- Indices de la tabla `configuracionempresa`
--
ALTER TABLE `configuracionempresa`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `rut` (`rut`);

--
-- Indices de la tabla `detallecierrepormetodo`
--
ALTER TABLE `detallecierrepormetodo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cierre_id` (`cierre_id`),
  ADD KEY `metodo_pago_id` (`metodo_pago_id`);

--
-- Indices de la tabla `informepdf`
--
ALTER TABLE `informepdf`
  ADD PRIMARY KEY (`id`),
  ADD KEY `prediccion_id` (`prediccion_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `metodopago`
--
ALTER TABLE `metodopago`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `prediccionriesgo`
--
ALTER TABLE `prediccionriesgo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ratio_id` (`ratio_id`),
  ADD KEY `ejecutada_por_usuario_id` (`ejecutada_por_usuario_id`);

--
-- Indices de la tabla `ratiofinanciero`
--
ALTER TABLE `ratiofinanciero`
  ADD PRIMARY KEY (`id`),
  ADD KEY `carga_id` (`carga_id`),
  ADD KEY `validado_por_usuario_id` (`validado_por_usuario_id`);

--
-- Indices de la tabla `recomendacion`
--
ALTER TABLE `recomendacion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `prediccion_id` (`prediccion_id`);

--
-- Indices de la tabla `retirocajachica`
--
ALTER TABLE `retirocajachica`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `cierre_id` (`cierre_id`);

--
-- Indices de la tabla `rol`
--
ALTER TABLE `rol`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `rol_id` (`rol_id`),
  ADD KEY `usuario_ibfk_2` (`empresa_id`);

--
-- Indices de la tabla `venta`
--
ALTER TABLE `venta`
  ADD PRIMARY KEY (`id`),
  ADD KEY `metodo_pago_id` (`metodo_pago_id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `cierre_id` (`cierre_id`);

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `cargafinanciera`
--
ALTER TABLE `cargafinanciera`
  ADD CONSTRAINT `cargafinanciera_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `cierrecaja`
--
ALTER TABLE `cierrecaja`
  ADD CONSTRAINT `cierrecaja_ibfk_1` FOREIGN KEY (`cerrado_por_usuario_id`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `cierrecaja_ibfk_2` FOREIGN KEY (`revisado_por_usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `detallecierrepormetodo`
--
ALTER TABLE `detallecierrepormetodo`
  ADD CONSTRAINT `detallecierrepormetodo_ibfk_1` FOREIGN KEY (`cierre_id`) REFERENCES `cierrecaja` (`id`),
  ADD CONSTRAINT `detallecierrepormetodo_ibfk_2` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodopago` (`id`);

--
-- Filtros para la tabla `informepdf`
--
ALTER TABLE `informepdf`
  ADD CONSTRAINT `informepdf_ibfk_1` FOREIGN KEY (`prediccion_id`) REFERENCES `prediccionriesgo` (`id`),
  ADD CONSTRAINT `informepdf_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `prediccionriesgo`
--
ALTER TABLE `prediccionriesgo`
  ADD CONSTRAINT `prediccionriesgo_ibfk_1` FOREIGN KEY (`ratio_id`) REFERENCES `ratiofinanciero` (`id`),
  ADD CONSTRAINT `prediccionriesgo_ibfk_2` FOREIGN KEY (`ejecutada_por_usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `ratiofinanciero`
--
ALTER TABLE `ratiofinanciero`
  ADD CONSTRAINT `ratiofinanciero_ibfk_1` FOREIGN KEY (`carga_id`) REFERENCES `cargafinanciera` (`id`),
  ADD CONSTRAINT `ratiofinanciero_ibfk_2` FOREIGN KEY (`validado_por_usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `recomendacion`
--
ALTER TABLE `recomendacion`
  ADD CONSTRAINT `recomendacion_ibfk_1` FOREIGN KEY (`prediccion_id`) REFERENCES `prediccionriesgo` (`id`);

--
-- Filtros para la tabla `retirocajachica`
--
ALTER TABLE `retirocajachica`
  ADD CONSTRAINT `retirocajachica_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `retirocajachica_ibfk_2` FOREIGN KEY (`cierre_id`) REFERENCES `cierrecaja` (`id`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`),
  ADD CONSTRAINT `usuario_ibfk_2` FOREIGN KEY (`empresa_id`) REFERENCES `configuracionempresa` (`id`);

--
-- Filtros para la tabla `venta`
--
ALTER TABLE `venta`
  ADD CONSTRAINT `venta_ibfk_1` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodopago` (`id`),
  ADD CONSTRAINT `venta_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `venta_ibfk_3` FOREIGN KEY (`cierre_id`) REFERENCES `cierrecaja` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
