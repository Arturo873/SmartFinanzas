-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 04-11-2026 a las 20:02:23
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
-- Estructura de tabla para la tabla `appweb_empresa`
--

CREATE TABLE `appweb_empresa` (
  `id` bigint(20) NOT NULL,
  `rut` varchar(12) NOT NULL,
  `nombre` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `appweb_estadocarga`
--

CREATE TABLE `appweb_estadocarga` (
  `id` bigint(20) NOT NULL,
  `ruta_csv` varchar(500) DEFAULT NULL,
  `actualizado_en` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `appweb_estadocarga`
--

INSERT INTO `appweb_estadocarga` (`id`, `ruta_csv`, `actualizado_en`) VALUES
(1, NULL, '2026-11-04 01:31:32.114471');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `appweb_historialprediccion`
--

CREATE TABLE `appweb_historialprediccion` (
  `id` bigint(20) NOT NULL,
  `fecha_prediccion` datetime(6) NOT NULL,
  `score` double NOT NULL,
  `riesgo` varchar(20) NOT NULL,
  `razon_corriente` double DEFAULT NULL,
  `prueba_acuda` double DEFAULT NULL,
  `empresa_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `appweb_perfilusuario`
--

CREATE TABLE `appweb_perfilusuario` (
  `id` bigint(20) NOT NULL,
  `rol` varchar(20) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `appweb_perfilusuario`
--

INSERT INTO `appweb_perfilusuario` (`id`, `rol`, `user_id`) VALUES
(1, 'Administrador', 1),
(2, 'Administrador', 2),
(3, 'Administrador', 3),
(4, 'Administrador', 4),
(5, 'Administrador', 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add empresa', 7, 'add_empresa'),
(26, 'Can change empresa', 7, 'change_empresa'),
(27, 'Can delete empresa', 7, 'delete_empresa'),
(28, 'Can view empresa', 7, 'view_empresa'),
(29, 'Can add historial prediccion', 8, 'add_historialprediccion'),
(30, 'Can change historial prediccion', 8, 'change_historialprediccion'),
(31, 'Can delete historial prediccion', 8, 'delete_historialprediccion'),
(32, 'Can view historial prediccion', 8, 'view_historialprediccion'),
(33, 'Can add estado carga', 9, 'add_estadocarga'),
(34, 'Can change estado carga', 9, 'change_estadocarga'),
(35, 'Can delete estado carga', 9, 'delete_estadocarga'),
(36, 'Can view estado carga', 9, 'view_estadocarga'),
(37, 'Can add perfil usuario', 10, 'add_perfilusuario'),
(38, 'Can change perfil usuario', 10, 'change_perfilusuario'),
(39, 'Can delete perfil usuario', 10, 'delete_perfilusuario'),
(40, 'Can view perfil usuario', 10, 'view_perfilusuario'),
(41, 'Can add Configuración de Empresa', 11, 'add_configuracionempresa'),
(42, 'Can change Configuración de Empresa', 11, 'change_configuracionempresa'),
(43, 'Can delete Configuración de Empresa', 11, 'delete_configuracionempresa'),
(44, 'Can view Configuración de Empresa', 11, 'view_configuracionempresa'),
(45, 'Can add Rol', 12, 'add_rol'),
(46, 'Can change Rol', 12, 'change_rol'),
(47, 'Can delete Rol', 12, 'delete_rol'),
(48, 'Can view Rol', 12, 'view_rol'),
(49, 'Can add Usuario', 13, 'add_usuario'),
(50, 'Can change Usuario', 13, 'change_usuario'),
(51, 'Can delete Usuario', 13, 'delete_usuario'),
(52, 'Can view Usuario', 13, 'view_usuario'),
(53, 'Can add Método de Pago', 14, 'add_metodopago'),
(54, 'Can change Método de Pago', 14, 'change_metodopago'),
(55, 'Can delete Método de Pago', 14, 'delete_metodopago'),
(56, 'Can view Método de Pago', 14, 'view_metodopago'),
(57, 'Can add Cierre de Caja', 15, 'add_cierrecaja'),
(58, 'Can change Cierre de Caja', 15, 'change_cierrecaja'),
(59, 'Can delete Cierre de Caja', 15, 'delete_cierrecaja'),
(60, 'Can view Cierre de Caja', 15, 'view_cierrecaja'),
(61, 'Can add Detalle de Cierre por Método', 16, 'add_detallecierrepormetodo'),
(62, 'Can change Detalle de Cierre por Método', 16, 'change_detallecierrepormetodo'),
(63, 'Can delete Detalle de Cierre por Método', 16, 'delete_detallecierrepormetodo'),
(64, 'Can view Detalle de Cierre por Método', 16, 'view_detallecierrepormetodo'),
(65, 'Can add Retiro de Caja Chica', 17, 'add_retirocajachica'),
(66, 'Can change Retiro de Caja Chica', 17, 'change_retirocajachica'),
(67, 'Can delete Retiro de Caja Chica', 17, 'delete_retirocajachica'),
(68, 'Can view Retiro de Caja Chica', 17, 'view_retirocajachica'),
(69, 'Can add Venta', 18, 'add_venta'),
(70, 'Can change Venta', 18, 'change_venta'),
(71, 'Can delete Venta', 18, 'delete_venta'),
(72, 'Can view Venta', 18, 'view_venta'),
(73, 'Can add Carga Financiera', 19, 'add_cargafinanciera'),
(74, 'Can change Carga Financiera', 19, 'change_cargafinanciera'),
(75, 'Can delete Carga Financiera', 19, 'delete_cargafinanciera'),
(76, 'Can view Carga Financiera', 19, 'view_cargafinanciera'),
(77, 'Can add Ratio Financiero', 20, 'add_ratiofinanciero'),
(78, 'Can change Ratio Financiero', 20, 'change_ratiofinanciero'),
(79, 'Can delete Ratio Financiero', 20, 'delete_ratiofinanciero'),
(80, 'Can view Ratio Financiero', 20, 'view_ratiofinanciero'),
(81, 'Can add Predicción de Riesgo', 21, 'add_prediccionriesgo'),
(82, 'Can change Predicción de Riesgo', 21, 'change_prediccionriesgo'),
(83, 'Can delete Predicción de Riesgo', 21, 'delete_prediccionriesgo'),
(84, 'Can view Predicción de Riesgo', 21, 'view_prediccionriesgo'),
(85, 'Can add Informe PDF', 22, 'add_informepdf'),
(86, 'Can change Informe PDF', 22, 'change_informepdf'),
(87, 'Can delete Informe PDF', 22, 'delete_informepdf'),
(88, 'Can view Informe PDF', 22, 'view_informepdf'),
(89, 'Can add Recomendación', 23, 'add_recomendacion'),
(90, 'Can change Recomendación', 23, 'change_recomendacion'),
(91, 'Can delete Recomendación', 23, 'delete_recomendacion'),
(92, 'Can view Recomendación', 23, 'view_recomendacion');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, '', '2026-11-04 01:45:30.138361', 0, 'test', '', '', 'test1@test.cl', 0, 1, '2026-11-04 01:31:24.903471'),
(2, '', '2026-11-04 18:46:55.166769', 0, 'admin', '', '', 'admin@admin.cl', 0, 1, '2026-11-04 02:05:52.738838'),
(3, '', '2026-11-04 18:50:07.153948', 0, 'test2', '', '', 'test2@test.cl', 0, 1, '2026-11-04 02:09:14.486806'),
(4, '', '2026-11-04 18:50:32.309317', 0, 'test3', '', '', 'test3@test.cl', 0, 1, '2026-11-04 18:50:32.123754'),
(5, '', '2026-11-04 19:01:12.437274', 0, 'test1', '', '', 'test1@test.cl', 0, 1, '2026-11-04 18:55:48.391435');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cargafinanciera`
--

CREATE TABLE `cargafinanciera` (
  `id` bigint(20) NOT NULL,
  `fecha_carga` datetime(6) DEFAULT NULL,
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
  `errores_detectados` longtext DEFAULT NULL,
  `usuario_id` bigint(20) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cierrecaja`
--

CREATE TABLE `cierrecaja` (
  `id` bigint(20) NOT NULL,
  `fecha` date NOT NULL,
  `estado` varchar(15) DEFAULT NULL,
  `total_sistema` decimal(12,2) DEFAULT NULL,
  `total_retiros` decimal(12,2) DEFAULT NULL,
  `total_arqueo` decimal(12,2) DEFAULT NULL,
  `descuadre_total` decimal(12,2) DEFAULT NULL,
  `fecha_confirmacion` datetime(6) DEFAULT NULL,
  `fecha_revision` datetime(6) DEFAULT NULL,
  `cerrado_por_usuario_id` bigint(20) DEFAULT NULL,
  `revisado_por_usuario_id` bigint(20) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detallecierrepormetodo`
--

CREATE TABLE `detallecierrepormetodo` (
  `id` bigint(20) NOT NULL,
  `total_sistema` decimal(12,2) DEFAULT NULL,
  `total_arqueo` decimal(12,2) DEFAULT NULL,
  `descuadre` decimal(10,2) DEFAULT NULL,
  `justificacion` longtext DEFAULT NULL,
  `cierre_id` bigint(20) NOT NULL,
  `metodo_pago_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(7, 'AppWeb', 'empresa'),
(9, 'AppWeb', 'estadocarga'),
(8, 'AppWeb', 'historialprediccion'),
(10, 'AppWeb', 'perfilusuario'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(22, 'capaAnalitica', 'informepdf'),
(21, 'capaAnalitica', 'prediccionriesgo'),
(23, 'capaAnalitica', 'recomendacion'),
(5, 'contenttypes', 'contenttype'),
(19, 'moduloETL', 'cargafinanciera'),
(20, 'moduloETL', 'ratiofinanciero'),
(15, 'moduloTransaccional', 'cierrecaja'),
(16, 'moduloTransaccional', 'detallecierrepormetodo'),
(14, 'moduloTransaccional', 'metodopago'),
(17, 'moduloTransaccional', 'retirocajachica'),
(18, 'moduloTransaccional', 'venta'),
(6, 'sessions', 'session'),
(11, 'usuarios', 'configuracionempresa'),
(12, 'usuarios', 'rol'),
(13, 'usuarios', 'usuario');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-11-04 01:12:00.959087'),
(2, 'auth', '0001_initial', '2026-11-04 01:12:13.364847'),
(3, 'AppWeb', '0001_initial', '2026-11-04 01:12:16.349079'),
(4, 'AppWeb', '0002_estadocarga_perfilusuario', '2026-11-04 01:12:17.706755'),
(5, 'AppWeb', '0003_quitar_capm', '2026-11-04 01:12:19.522143'),
(6, 'admin', '0001_initial', '2026-11-04 01:12:22.412651'),
(7, 'admin', '0002_logentry_remove_auto_add', '2026-11-04 01:12:22.504061'),
(8, 'admin', '0003_logentry_add_action_flag_choices', '2026-11-04 01:12:22.612047'),
(9, 'contenttypes', '0002_remove_content_type_name', '2026-11-04 01:12:23.395236'),
(10, 'auth', '0002_alter_permission_name_max_length', '2026-11-04 01:12:24.849526'),
(11, 'auth', '0003_alter_user_email_max_length', '2026-11-04 01:12:25.028004'),
(12, 'auth', '0004_alter_user_username_opts', '2026-11-04 01:12:25.101180'),
(13, 'auth', '0005_alter_user_last_login_null', '2026-11-04 01:12:25.743001'),
(14, 'auth', '0006_require_contenttypes_0002', '2026-11-04 01:12:25.789102'),
(15, 'auth', '0007_alter_validators_add_error_messages', '2026-11-04 01:12:25.866127'),
(16, 'auth', '0008_alter_user_username_max_length', '2026-11-04 01:12:26.040771'),
(17, 'auth', '0009_alter_user_last_name_max_length', '2026-11-04 01:12:26.174797'),
(18, 'auth', '0010_alter_group_name_max_length', '2026-11-04 01:12:26.505312'),
(19, 'auth', '0011_update_proxy_permissions', '2026-11-04 01:12:26.598869'),
(20, 'auth', '0012_alter_user_first_name_max_length', '2026-11-04 01:12:26.872865'),
(21, 'usuarios', '0001_initial', '2026-11-04 01:12:30.299779'),
(22, 'moduloETL', '0001_initial', '2026-11-04 01:12:33.759619'),
(23, 'capaAnalitica', '0001_initial', '2026-11-04 01:12:40.272131'),
(24, 'moduloTransaccional', '0001_initial', '2026-11-04 01:12:52.551544'),
(25, 'sessions', '0001_initial', '2026-11-04 01:12:53.321978');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresa`
--

CREATE TABLE `empresa` (
  `id` bigint(20) NOT NULL,
  `razon_social` varchar(200) NOT NULL,
  `rut` varchar(15) NOT NULL,
  `giro` varchar(150) DEFAULT NULL,
  `comision_debito_pct` decimal(5,2) DEFAULT NULL,
  `comision_credito_pct` decimal(5,2) DEFAULT NULL,
  `fecha_actualizacion` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empresa`
--

INSERT INTO `empresa` (`id`, `razon_social`, `rut`, `giro`, `comision_debito_pct`, `comision_credito_pct`, `fecha_actualizacion`) VALUES
(1, 'Nstock Importaciones', '76.123.456-7', 'Distribuidora e importadora mayorista', 1.75, 2.35, '2026-11-03 12:25:42.000000'),
(2, 'TestEmpresa1', '11.111.111-1', 'Distribuidora e importadora ', 1.85, 2.45, '2026-11-03 12:25:42.000000');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informepdf`
--

CREATE TABLE `informepdf` (
  `id` bigint(20) NOT NULL,
  `fecha_generacion` datetime(6) DEFAULT NULL,
  `ruta_archivo` varchar(500) DEFAULT NULL,
  `usuario_id` bigint(20) DEFAULT NULL,
  `prediccion_id` bigint(20) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodopago`
--

CREATE TABLE `metodopago` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `comision_porcentaje` decimal(5,2) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `metodopago`
--

INSERT INTO `metodopago` (`id`, `nombre`, `comision_porcentaje`, `activo`, `empresa_id`) VALUES
(1, 'Efectivo', 0.00, 1, NULL),
(2, 'Débito', 1.75, 1, NULL),
(3, 'Crédito', 2.35, 1, NULL),
(4, 'Transferencia', 0.00, 1, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prediccionriesgo`
--

CREATE TABLE `prediccionriesgo` (
  `id` bigint(20) NOT NULL,
  `fecha_prediccion` datetime(6) DEFAULT NULL,
  `score_riesgo` decimal(5,2) DEFAULT NULL,
  `nivel_semaforo` varchar(10) DEFAULT NULL,
  `variables_influyentes` longtext DEFAULT NULL,
  `impacto_variables` longtext DEFAULT NULL,
  `version_modelo` varchar(20) DEFAULT NULL,
  `tiempo_inferencia_ms` int(11) DEFAULT NULL,
  `ejecutado_por_usuario_id` bigint(20) DEFAULT NULL,
  `ratio_id` bigint(20) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ratiofinanciero`
--

CREATE TABLE `ratiofinanciero` (
  `id` bigint(20) NOT NULL,
  `periodo` varchar(20) DEFAULT NULL,
  `fecha_calculo` datetime(6) DEFAULT NULL,
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
  `fecha_validacion` datetime(6) DEFAULT NULL,
  `carga_id` bigint(20) DEFAULT NULL,
  `validado_por_usuario_id` bigint(20) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recomendacion`
--

CREATE TABLE `recomendacion` (
  `id` bigint(20) NOT NULL,
  `variable_origen` varchar(50) DEFAULT NULL,
  `grupo_riesgo` varchar(40) DEFAULT NULL,
  `texto` longtext DEFAULT NULL,
  `prioridad` varchar(10) DEFAULT NULL,
  `prediccion_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `retirocajachica`
--

CREATE TABLE `retirocajachica` (
  `id` bigint(20) NOT NULL,
  `fecha` datetime(6) DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `responsable` varchar(100) DEFAULT NULL,
  `cierre_id` bigint(20) DEFAULT NULL,
  `usuario_id` bigint(20) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--

CREATE TABLE `rol` (
  `id` bigint(20) NOT NULL,
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
  `id` bigint(20) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime(6) DEFAULT NULL,
  `ultima_sesion` datetime(6) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL,
  `rol_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `username`, `email`, `password_hash`, `activo`, `fecha_creacion`, `ultima_sesion`, `empresa_id`, `rol_id`) VALUES
(1, 'Alexis', 'admin@nstock.cl', 'pbkdf2_sha256$600000$KbtTH8eCRccGACC1MWekWR$Pryx8YSzQ+L4HzBWwbu2OYMi9kL+gHX/s8jxv9Vk8Y8=', 1, '2026-11-03 12:25:42.000000', NULL, 1, 4),
(2, 'admin', 'admin@admin.cl', 'pbkdf2_sha256$600000$YeAOLQCylZseIX7LFNquCZ$mOzLcdNeAzW8HfTp7phi2spAdsvR5LpS1oE/tpFDp4k=', 1, '2026-11-03 12:25:42.000000', '2026-11-04 18:46:55.074005', 2, 4),
(7, 'test1', 'test1@test.cl', 'pbkdf2_sha256$600000$kIudPsIDeg9akKAxQhLMPS$La+HJop9usfYk2SXnQxMRSF5vKPdRs82WJKvQldWW40=', 1, '2026-11-04 18:55:47.053246', '2026-11-04 19:01:12.299878', 2, 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `venta`
--

CREATE TABLE `venta` (
  `id` bigint(20) NOT NULL,
  `fecha` datetime(6) DEFAULT NULL,
  `total_bruto` decimal(10,2) DEFAULT NULL,
  `descuento_tipo` varchar(10) DEFAULT NULL,
  `descuento_monto` decimal(10,2) DEFAULT NULL,
  `total_cobrado` decimal(10,2) DEFAULT NULL,
  `comision_aplicada` decimal(10,2) DEFAULT NULL,
  `ingreso_real` decimal(10,2) DEFAULT NULL,
  `cierre_id` bigint(20) DEFAULT NULL,
  `metodo_pago_id` bigint(20) DEFAULT NULL,
  `usuario_id` bigint(20) DEFAULT NULL,
  `empresa_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `appweb_empresa`
--
ALTER TABLE `appweb_empresa`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `rut` (`rut`);

--
-- Indices de la tabla `appweb_estadocarga`
--
ALTER TABLE `appweb_estadocarga`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `appweb_historialprediccion`
--
ALTER TABLE `appweb_historialprediccion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `AppWeb_historialpred_empresa_id_84334eda_fk_AppWeb_em` (`empresa_id`);

--
-- Indices de la tabla `appweb_perfilusuario`
--
ALTER TABLE `appweb_perfilusuario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indices de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indices de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indices de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `cargafinanciera`
--
ALTER TABLE `cargafinanciera`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cargafinanciera_usuario_id_6e2bde4c_fk_usuario_id` (`usuario_id`),
  ADD KEY `fk_cargafinanciera_empresa` (`empresa_id`);

--
-- Indices de la tabla `cierrecaja`
--
ALTER TABLE `cierrecaja`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `fecha` (`fecha`),
  ADD KEY `cierrecaja_cerrado_por_usuario_id_16dfc446_fk_usuario_id` (`cerrado_por_usuario_id`),
  ADD KEY `cierrecaja_revisado_por_usuario_id_2a6a9c23_fk_usuario_id` (`revisado_por_usuario_id`),
  ADD KEY `fk_cierrecaja_empresa` (`empresa_id`);

--
-- Indices de la tabla `detallecierrepormetodo`
--
ALTER TABLE `detallecierrepormetodo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `detallecierrepormetodo_cierre_id_8f932810_fk_cierrecaja_id` (`cierre_id`),
  ADD KEY `detallecierrepormetodo_metodo_pago_id_43d3d145_fk_metodopago_id` (`metodo_pago_id`);

--
-- Indices de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indices de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indices de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indices de la tabla `empresa`
--
ALTER TABLE `empresa`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `rut` (`rut`);

--
-- Indices de la tabla `informepdf`
--
ALTER TABLE `informepdf`
  ADD PRIMARY KEY (`id`),
  ADD KEY `informepdf_usuario_id_0dd6e5c3_fk_usuario_id` (`usuario_id`),
  ADD KEY `informepdf_prediccion_id_c9fc5c3c_fk_prediccionriesgo_id` (`prediccion_id`),
  ADD KEY `fk_informepdf_empresa` (`empresa_id`);

--
-- Indices de la tabla `metodopago`
--
ALTER TABLE `metodopago`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_metodopago_empresa` (`empresa_id`);

--
-- Indices de la tabla `prediccionriesgo`
--
ALTER TABLE `prediccionriesgo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `prediccionriesgo_ejecutada_por_usuario_id_d6e62fbb_fk_usuario_id` (`ejecutado_por_usuario_id`),
  ADD KEY `prediccionriesgo_ratio_id_f55c8748_fk_ratiofinanciero_id` (`ratio_id`),
  ADD KEY `fk_prediccionriesgo_empresa` (`empresa_id`);

--
-- Indices de la tabla `ratiofinanciero`
--
ALTER TABLE `ratiofinanciero`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ratiofinanciero_carga_id_6930236a_fk_cargafinanciera_id` (`carga_id`),
  ADD KEY `ratiofinanciero_validado_por_usuario_id_7679b4cf_fk_usuario_id` (`validado_por_usuario_id`),
  ADD KEY `fk_ratiofinanciero_empresa` (`empresa_id`);

--
-- Indices de la tabla `recomendacion`
--
ALTER TABLE `recomendacion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `recomendacion_prediccion_id_91b1545c_fk_prediccionriesgo_id` (`prediccion_id`);

--
-- Indices de la tabla `retirocajachica`
--
ALTER TABLE `retirocajachica`
  ADD PRIMARY KEY (`id`),
  ADD KEY `retirocajachica_cierre_id_641ed47a_fk_cierrecaja_id` (`cierre_id`),
  ADD KEY `retirocajachica_usuario_id_51fbe447_fk_usuario_id` (`usuario_id`),
  ADD KEY `fk_retirocajachica_empresa` (`empresa_id`);

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
  ADD KEY `usuario_empresa_id_b7a13193_fk_configuracionempresa_id` (`empresa_id`),
  ADD KEY `usuario_rol_id_ac58b608_fk_rol_id` (`rol_id`);

--
-- Indices de la tabla `venta`
--
ALTER TABLE `venta`
  ADD PRIMARY KEY (`id`),
  ADD KEY `venta_cierre_id_482c6e37_fk_cierrecaja_id` (`cierre_id`),
  ADD KEY `venta_metodo_pago_id_fb1402b9_fk_metodopago_id` (`metodo_pago_id`),
  ADD KEY `venta_usuario_id_32b9f91d_fk_usuario_id` (`usuario_id`),
  ADD KEY `fk_venta_empresa` (`empresa_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `appweb_empresa`
--
ALTER TABLE `appweb_empresa`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `appweb_estadocarga`
--
ALTER TABLE `appweb_estadocarga`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `appweb_historialprediccion`
--
ALTER TABLE `appweb_historialprediccion`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `appweb_perfilusuario`
--
ALTER TABLE `appweb_perfilusuario`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=93;

--
-- AUTO_INCREMENT de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cargafinanciera`
--
ALTER TABLE `cargafinanciera`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cierrecaja`
--
ALTER TABLE `cierrecaja`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detallecierrepormetodo`
--
ALTER TABLE `detallecierrepormetodo`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT de la tabla `empresa`
--
ALTER TABLE `empresa`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `informepdf`
--
ALTER TABLE `informepdf`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `metodopago`
--
ALTER TABLE `metodopago`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `prediccionriesgo`
--
ALTER TABLE `prediccionriesgo`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ratiofinanciero`
--
ALTER TABLE `ratiofinanciero`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `recomendacion`
--
ALTER TABLE `recomendacion`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `retirocajachica`
--
ALTER TABLE `retirocajachica`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `rol`
--
ALTER TABLE `rol`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `venta`
--
ALTER TABLE `venta`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `appweb_historialprediccion`
--
ALTER TABLE `appweb_historialprediccion`
  ADD CONSTRAINT `AppWeb_historialpred_empresa_id_84334eda_fk_AppWeb_em` FOREIGN KEY (`empresa_id`) REFERENCES `appweb_empresa` (`id`);

--
-- Filtros para la tabla `appweb_perfilusuario`
--
ALTER TABLE `appweb_perfilusuario`
  ADD CONSTRAINT `AppWeb_perfilusuario_user_id_ddbec2b8_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Filtros para la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `cargafinanciera`
--
ALTER TABLE `cargafinanciera`
  ADD CONSTRAINT `cargafinanciera_usuario_id_6e2bde4c_fk_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `fk_cargafinanciera_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `cierrecaja`
--
ALTER TABLE `cierrecaja`
  ADD CONSTRAINT `cierrecaja_cerrado_por_usuario_id_16dfc446_fk_usuario_id` FOREIGN KEY (`cerrado_por_usuario_id`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `cierrecaja_revisado_por_usuario_id_2a6a9c23_fk_usuario_id` FOREIGN KEY (`revisado_por_usuario_id`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `fk_cierrecaja_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `detallecierrepormetodo`
--
ALTER TABLE `detallecierrepormetodo`
  ADD CONSTRAINT `detallecierrepormetodo_cierre_id_8f932810_fk_cierrecaja_id` FOREIGN KEY (`cierre_id`) REFERENCES `cierrecaja` (`id`),
  ADD CONSTRAINT `detallecierrepormetodo_metodo_pago_id_43d3d145_fk_metodopago_id` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodopago` (`id`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `informepdf`
--
ALTER TABLE `informepdf`
  ADD CONSTRAINT `fk_informepdf_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `informepdf_prediccion_id_c9fc5c3c_fk_prediccionriesgo_id` FOREIGN KEY (`prediccion_id`) REFERENCES `prediccionriesgo` (`id`),
  ADD CONSTRAINT `informepdf_usuario_id_0dd6e5c3_fk_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `metodopago`
--
ALTER TABLE `metodopago`
  ADD CONSTRAINT `fk_metodopago_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `prediccionriesgo`
--
ALTER TABLE `prediccionriesgo`
  ADD CONSTRAINT `fk_prediccionriesgo_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `prediccionriesgo_ejecutada_por_usuario_id_d6e62fbb_fk_usuario_id` FOREIGN KEY (`ejecutado_por_usuario_id`) REFERENCES `usuario` (`id`),
  ADD CONSTRAINT `prediccionriesgo_ratio_id_f55c8748_fk_ratiofinanciero_id` FOREIGN KEY (`ratio_id`) REFERENCES `ratiofinanciero` (`id`);

--
-- Filtros para la tabla `ratiofinanciero`
--
ALTER TABLE `ratiofinanciero`
  ADD CONSTRAINT `fk_ratiofinanciero_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `ratiofinanciero_carga_id_6930236a_fk_cargafinanciera_id` FOREIGN KEY (`carga_id`) REFERENCES `cargafinanciera` (`id`),
  ADD CONSTRAINT `ratiofinanciero_validado_por_usuario_id_7679b4cf_fk_usuario_id` FOREIGN KEY (`validado_por_usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `recomendacion`
--
ALTER TABLE `recomendacion`
  ADD CONSTRAINT `recomendacion_prediccion_id_91b1545c_fk_prediccionriesgo_id` FOREIGN KEY (`prediccion_id`) REFERENCES `prediccionriesgo` (`id`);

--
-- Filtros para la tabla `retirocajachica`
--
ALTER TABLE `retirocajachica`
  ADD CONSTRAINT `fk_retirocajachica_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `retirocajachica_cierre_id_641ed47a_fk_cierrecaja_id` FOREIGN KEY (`cierre_id`) REFERENCES `cierrecaja` (`id`),
  ADD CONSTRAINT `retirocajachica_usuario_id_51fbe447_fk_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_empresa_id_b7a13193_fk_configuracionempresa_id` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`),
  ADD CONSTRAINT `usuario_rol_id_ac58b608_fk_rol_id` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`);

--
-- Filtros para la tabla `venta`
--
ALTER TABLE `venta`
  ADD CONSTRAINT `fk_venta_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `venta_cierre_id_482c6e37_fk_cierrecaja_id` FOREIGN KEY (`cierre_id`) REFERENCES `cierrecaja` (`id`),
  ADD CONSTRAINT `venta_metodo_pago_id_fb1402b9_fk_metodopago_id` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodopago` (`id`),
  ADD CONSTRAINT `venta_usuario_id_32b9f91d_fk_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
