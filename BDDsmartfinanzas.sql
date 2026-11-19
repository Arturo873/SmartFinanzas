-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 19-11-2026 a las 19:30:28
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
-- Base de datos: `smartfinanzasingles2`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `appweb_company`
--

CREATE TABLE `appweb_company` (
  `id` bigint(20) NOT NULL,
  `tax_id` varchar(12) NOT NULL,
  `name` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
(25, 'Can add company', 7, 'add_company'),
(26, 'Can change company', 7, 'change_company'),
(27, 'Can delete company', 7, 'delete_company'),
(28, 'Can view company', 7, 'view_company'),
(29, 'Can add upload state', 8, 'add_uploadstate'),
(30, 'Can change upload state', 8, 'change_uploadstate'),
(31, 'Can delete upload state', 8, 'delete_uploadstate'),
(32, 'Can view upload state', 8, 'view_uploadstate'),
(33, 'Can add user profile', 9, 'add_userprofile'),
(34, 'Can change user profile', 9, 'change_userprofile'),
(35, 'Can delete user profile', 9, 'delete_userprofile'),
(36, 'Can view user profile', 9, 'view_userprofile'),
(37, 'Can add prediction history', 10, 'add_predictionhistory'),
(38, 'Can change prediction history', 10, 'change_predictionhistory'),
(39, 'Can delete prediction history', 10, 'delete_predictionhistory'),
(40, 'Can view prediction history', 10, 'view_predictionhistory'),
(41, 'Can add Empresa', 11, 'add_company'),
(42, 'Can change Empresa', 11, 'change_company'),
(43, 'Can delete Empresa', 11, 'delete_company'),
(44, 'Can view Empresa', 11, 'view_company'),
(45, 'Can add Rol', 12, 'add_role'),
(46, 'Can change Rol', 12, 'change_role'),
(47, 'Can delete Rol', 12, 'delete_role'),
(48, 'Can view Rol', 12, 'view_role'),
(49, 'Can add Usuario', 13, 'add_user'),
(50, 'Can change Usuario', 13, 'change_user'),
(51, 'Can delete Usuario', 13, 'delete_user'),
(52, 'Can view Usuario', 13, 'view_user'),
(53, 'Can add Cierre de Caja', 14, 'add_cashregisterclosure'),
(54, 'Can change Cierre de Caja', 14, 'change_cashregisterclosure'),
(55, 'Can delete Cierre de Caja', 14, 'delete_cashregisterclosure'),
(56, 'Can view Cierre de Caja', 14, 'view_cashregisterclosure'),
(57, 'Can add Método de Pago', 15, 'add_paymentmethod'),
(58, 'Can change Método de Pago', 15, 'change_paymentmethod'),
(59, 'Can delete Método de Pago', 15, 'delete_paymentmethod'),
(60, 'Can view Método de Pago', 15, 'view_paymentmethod'),
(61, 'Can add Venta', 16, 'add_sale'),
(62, 'Can change Venta', 16, 'change_sale'),
(63, 'Can delete Venta', 16, 'delete_sale'),
(64, 'Can view Venta', 16, 'view_sale'),
(65, 'Can add Retiro de Caja Chica', 17, 'add_pettycashwithdrawal'),
(66, 'Can change Retiro de Caja Chica', 17, 'change_pettycashwithdrawal'),
(67, 'Can delete Retiro de Caja Chica', 17, 'delete_pettycashwithdrawal'),
(68, 'Can view Retiro de Caja Chica', 17, 'view_pettycashwithdrawal'),
(69, 'Can add Detalle de Cierre por Método', 18, 'add_closuremethoddetail'),
(70, 'Can change Detalle de Cierre por Método', 18, 'change_closuremethoddetail'),
(71, 'Can delete Detalle de Cierre por Método', 18, 'delete_closuremethoddetail'),
(72, 'Can view Detalle de Cierre por Método', 18, 'view_closuremethoddetail'),
(73, 'Can add Carga Financiera', 19, 'add_financialupload'),
(74, 'Can change Carga Financiera', 19, 'change_financialupload'),
(75, 'Can delete Carga Financiera', 19, 'delete_financialupload'),
(76, 'Can view Carga Financiera', 19, 'view_financialupload'),
(77, 'Can add Ratio Financiero', 20, 'add_financialratio'),
(78, 'Can change Ratio Financiero', 20, 'change_financialratio'),
(79, 'Can delete Ratio Financiero', 20, 'delete_financialratio'),
(80, 'Can view Ratio Financiero', 20, 'view_financialratio'),
(81, 'Can add Predicción de Riesgo', 21, 'add_riskprediction'),
(82, 'Can change Predicción de Riesgo', 21, 'change_riskprediction'),
(83, 'Can delete Predicción de Riesgo', 21, 'delete_riskprediction'),
(84, 'Can view Predicción de Riesgo', 21, 'view_riskprediction'),
(85, 'Can add Recomendación', 22, 'add_recommendation'),
(86, 'Can change Recomendación', 22, 'change_recommendation'),
(87, 'Can delete Recomendación', 22, 'delete_recommendation'),
(88, 'Can view Recomendación', 22, 'view_recommendation'),
(89, 'Can add Informe PDF', 23, 'add_pdfreport'),
(90, 'Can change Informe PDF', 23, 'change_pdfreport'),
(91, 'Can delete Informe PDF', 23, 'delete_pdfreport'),
(92, 'Can view Informe PDF', 23, 'view_pdfreport');

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
(5, '', '2026-11-18 02:10:07.592703', 0, 'test1', '', '', 'test1@test.cl', 0, 1, '2026-11-04 18:55:48.391435'),
(6, 'pbkdf2_sha256$600000$4BvFh1Ze9dahuXYQHZNWqS$jc/Ox1oyg1Qp+IUK4qIjvSrHIBGS4rBHH4Glgpsao3c=', '2026-11-12 15:20:28.920722', 0, 'coagra', '', '', 'coagra@test.cl', 0, 1, '2026-11-09 20:23:40.769559'),
(7, 'pbkdf2_sha256$600000$l3iIFKpVgBb33aIX4pK7jY$U0WQ6AXosS6yJTeo0+wVowmPkqdCbiym4jDtQ7/p9qo=', '2026-11-17 18:12:41.743623', 0, 'dueno_coagra', '', '', 'dueno@coagra.cl', 0, 1, '2026-11-17 17:03:16.309001'),
(8, 'pbkdf2_sha256$600000$QaStIYDH4MxpQV6R5Y2eWO$klm2dTpjtmxKCR99e4CF8lXqCpC7cYvZ3QgoB42j9KI=', '2026-11-17 18:17:20.005386', 0, 'contador_coagra', '', '', 'contador@coagra.cl', 0, 1, '2026-11-17 17:03:19.634498'),
(9, 'pbkdf2_sha256$600000$ZEO5D1zhfmMRCcuYWRrnWy$6Gfkvg8Q1xqf2mSoX5rGW1ONSrCFRL14fJ5rRFbmdyM=', '2026-11-17 18:13:09.162528', 0, 'trabajador_coagra', '', '', 'trabajador@coagra.cl', 0, 1, '2026-11-17 17:03:22.620789'),
(10, '', '2026-11-19 18:23:24.794887', 0, 'TestDueño', '', '', 'propietario@test.cl', 0, 1, '2026-11-19 18:23:24.663409'),
(11, '', '2026-11-19 18:24:34.239282', 0, 'TestContador', '', '', 'contador@test.cl', 0, 1, '2026-11-19 18:24:34.029694'),
(12, '', '2026-11-19 18:25:38.215865', 0, 'TestTrabajador', '', '', 'trabajador@test.cl', 0, 1, '2026-11-19 18:25:37.996137'),
(13, '', '2026-11-19 18:26:20.749187', 0, 'TestAdministrador', '', '', 'admin@test.cl', 0, 1, '2026-11-19 18:26:20.563556');

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
-- Estructura de tabla para la tabla `cash_register_closure`
--

CREATE TABLE `cash_register_closure` (
  `id` bigint(20) NOT NULL,
  `date` date NOT NULL,
  `status` varchar(15) DEFAULT NULL,
  `system_total` decimal(12,2) DEFAULT NULL,
  `withdrawals_total` decimal(12,2) DEFAULT NULL,
  `counted_total` decimal(12,2) DEFAULT NULL,
  `total_discrepancy` decimal(12,2) DEFAULT NULL,
  `confirmation_date` datetime(6) DEFAULT NULL,
  `review_date` datetime(6) DEFAULT NULL,
  `closed_by_user_id` bigint(20) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `reviewed_by_user_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cash_register_closure`
--

INSERT INTO `cash_register_closure` (`id`, `date`, `status`, `system_total`, `withdrawals_total`, `counted_total`, `total_discrepancy`, `confirmation_date`, `review_date`, `closed_by_user_id`, `company_id`, `reviewed_by_user_id`) VALUES
(1, '2026-11-12', 'Cuadrado', 81455.00, 0.00, 81455.00, 0.00, '2026-11-12 15:21:32.159189', NULL, 8, 3, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `closure_method_detail`
--

CREATE TABLE `closure_method_detail` (
  `id` bigint(20) NOT NULL,
  `system_total` decimal(12,2) DEFAULT NULL,
  `counted_total` decimal(12,2) DEFAULT NULL,
  `discrepancy` decimal(10,2) DEFAULT NULL,
  `justification` longtext DEFAULT NULL,
  `closure_id` bigint(20) NOT NULL,
  `payment_method_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `closure_method_detail`
--

INSERT INTO `closure_method_detail` (`id`, `system_total`, `counted_total`, `discrepancy`, `justification`, `closure_id`, `payment_method_id`) VALUES
(1, 8750.00, 8750.00, 0.00, NULL, 1, 1),
(2, 72705.00, 72705.00, 0.00, NULL, 1, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `company`
--

CREATE TABLE `company` (
  `id` bigint(20) NOT NULL,
  `business_name` varchar(200) NOT NULL,
  `tax_id` varchar(15) NOT NULL,
  `business_sector` varchar(150) DEFAULT NULL,
  `debit_commission_pct` decimal(5,2) DEFAULT NULL,
  `credit_commission_pct` decimal(5,2) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `company`
--

INSERT INTO `company` (`id`, `business_name`, `tax_id`, `business_sector`, `debit_commission_pct`, `credit_commission_pct`, `updated_at`) VALUES
(1, 'Nstock Importaciones', '76.123.456-7', 'Distribuidora e importadora mayorista', 1.75, 2.35, '2026-11-03 12:25:42.000000'),
(2, 'TestEmpresa1', '11.111.111-1', 'Distribuidora e importadora ', 1.85, 2.45, '2026-11-03 12:25:42.000000'),
(3, 'COAGRA S.A.', '96686870-K', 'Comercialización y distribución de insumos agrícolas y granos', 1.15, 2.10, '2026-11-09 17:20:39.445019'),
(4, 'COMERCIAL K SPA', '77137860-9', 'Importación y comercialización de revestimientos, cerámicas y baños', 1.15, 2.10, '2026-11-09 17:20:39.445019'),
(5, 'UNION EL GOLF S.A.', '96790570-5', 'Servicios recreativos, gastronómicos, deportivos y eventos sociales', 1.20, 2.25, '2026-11-09 17:20:39.445019'),
(6, 'FRUTICOLA VICONTO S.A.', '96512190-8', 'Producción, empaque y exportación de productos agrícolas y frutas', 1.15, 2.10, '2026-11-09 17:20:39.445019'),
(7, 'INTASA S.A.', '99503280-9', 'Fabricación, importación y venta de tuberías y artículos de acero', 1.15, 2.10, '2026-11-09 17:20:39.445019'),
(8, 'ANDACOR S.A.', '91400000-4', 'Explotación de centros turísticos y centros de esquí (El Colorado)', 1.25, 2.30, '2026-11-09 17:20:39.445019'),
(9, 'AD RETAIL FINANCIERO S.A.', '76675290-7', 'Emisión de tarjetas de crédito comerciales y servicios financieros', 1.05, 1.95, '2026-11-09 17:20:39.445019'),
(10, 'ABC S.A.', '96874030-2', 'Venta minorista de electrodomésticos, tecnología y artículos del hogar', 1.15, 2.10, '2026-11-09 17:20:39.445019');

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
(7, 'AppWeb', 'company'),
(10, 'AppWeb', 'predictionhistory'),
(8, 'AppWeb', 'uploadstate'),
(9, 'AppWeb', 'userprofile'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(23, 'capaAnalitica', 'pdfreport'),
(22, 'capaAnalitica', 'recommendation'),
(21, 'capaAnalitica', 'riskprediction'),
(5, 'contenttypes', 'contenttype'),
(20, 'moduloETL', 'financialratio'),
(19, 'moduloETL', 'financialupload'),
(14, 'moduloTransaccional', 'cashregisterclosure'),
(18, 'moduloTransaccional', 'closuremethoddetail'),
(15, 'moduloTransaccional', 'paymentmethod'),
(17, 'moduloTransaccional', 'pettycashwithdrawal'),
(16, 'moduloTransaccional', 'sale'),
(6, 'sessions', 'session'),
(11, 'usuarios', 'company'),
(12, 'usuarios', 'role'),
(13, 'usuarios', 'user');

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
(1, 'contenttypes', '0001_initial', '2026-11-10 19:01:07.338891'),
(2, 'auth', '0001_initial', '2026-11-10 19:01:18.699328'),
(3, 'AppWeb', '0001_initial', '2026-11-10 19:01:21.705541'),
(4, 'admin', '0001_initial', '2026-11-10 19:01:24.279613'),
(5, 'admin', '0002_logentry_remove_auto_add', '2026-11-10 19:01:24.357483'),
(6, 'admin', '0003_logentry_add_action_flag_choices', '2026-11-10 19:01:24.448003'),
(7, 'contenttypes', '0002_remove_content_type_name', '2026-11-10 19:01:26.438060'),
(8, 'auth', '0002_alter_permission_name_max_length', '2026-11-10 19:01:28.305506'),
(9, 'auth', '0003_alter_user_email_max_length', '2026-11-10 19:01:28.426815'),
(10, 'auth', '0004_alter_user_username_opts', '2026-11-10 19:01:28.478861'),
(11, 'auth', '0005_alter_user_last_login_null', '2026-11-10 19:01:29.025784'),
(12, 'auth', '0006_require_contenttypes_0002', '2026-11-10 19:01:29.056028'),
(13, 'auth', '0007_alter_validators_add_error_messages', '2026-11-10 19:01:29.101555'),
(14, 'auth', '0008_alter_user_username_max_length', '2026-11-10 19:01:29.283796'),
(15, 'auth', '0009_alter_user_last_name_max_length', '2026-11-10 19:01:29.415111'),
(16, 'auth', '0010_alter_group_name_max_length', '2026-11-10 19:01:29.670900'),
(17, 'auth', '0011_update_proxy_permissions', '2026-11-10 19:01:29.768703'),
(18, 'auth', '0012_alter_user_first_name_max_length', '2026-11-10 19:01:29.970982'),
(19, 'usuarios', '0001_initial', '2026-11-10 19:01:32.960921'),
(20, 'moduloETL', '0001_initial', '2026-11-10 19:01:41.139764'),
(21, 'capaAnalitica', '0001_initial', '2026-11-10 19:01:52.041621'),
(22, 'moduloTransaccional', '0001_initial', '2026-11-10 19:02:14.818468'),
(23, 'sessions', '0001_initial', '2026-11-10 19:02:15.926770');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('0w0bky9vbjua2b5u4zgzoay2kyzhse0b', '.eJxVjEEOwiAQRe8y66YBYSB2p3vP0AwwWrSFBOjKeHejaTRd_v9e3hPWulKJeYwBBtv9ZsqLKwwDNK5Nwh-UPMMAp7DEFGsrFHKBDkZa2zSulcs3BLj_HPkHpw8Id0q33PucWomu_yj9Rmt_yYHn8-buAhPVCQbQRxXUwbBi7xnpiAfthdBBXY1CJiPROuGkFyzxaq03WpNBiYzGOkEBXm_rb1Bm:1xTV3c:yH08sIKQY9b4xXo_ODwCKynm-BBclnDy62LCKjZsQPs', '2026-12-02 02:05:56.084760'),
('1bkem2pg59ynjm7lfeg9wtv96msk6npi', '.eJxVjEEOwiAQRe8y66YBYSB2p3vP0AwwWrSFBOjKeHejaTRd_v9e3hPWulKJeYwBBtv9ZsqLKwwDNK5Nwh-UPMMAp7DEFGsrFHKBDkZa2zSulcs3BLj_HPkHpw8Id0q33PucWomu_yj9Rmt_yYHn8-buAhPVCQbQRxXUwbBi7xnpiAfthdBBXY1CJiPROuGkFyzxaq03WpNBiYzGOkEBXm_rb1Bm:1xTV7f:ajy6_CvcFHfAGX_w-ArKUZPXUo_AHSTzqKgrkPmK5_8', '2026-12-02 02:10:07.628702'),
('3szhxpao6nrh4eyk0kkp30esnf4siv6w', '.eJxVjEEOwiAQRe8y66YBYSB2p3vP0AwwWrSFBOjKeHejaTRd_v9e3hPWulKJeYwBBtv9ZsqLKwwDNK5Nwh-UPMMAp7DEFGsrFHKBDkZa2zSulcs3BLj_HPkHpw8Id0q33PucWomu_yj9Rmt_yYHn8-buAhPVCQbQRxXUwbBi7xnpiAfthdBBXY1CJiPROuGkFyzxaq03WpNBiYzGOkEBXm_rb1Bm:1xTV2F:5Kcx7XHs07wJ4IO9zRLKep49PrS4vbtTM9hM5ryAa3Q', '2026-12-02 02:04:31.467080'),
('8naq0djxghgn55mea4xe8d1sy6hdu0fo', '.eJxVjMsOgyAQRf9l1saAghSX7brfQGZ4qH1AArJq-u-NjWnj8t5zcl5QS8W8JLM4GDlrfjumJ2UPI9gUV3QpG5twygh_JacHjHDZOTRgsK6zqcXnbw5Ox4_Q3n3cgLthnFK7pfNC7aa0Oy3tNTn_OO_uITBjmWEE3QsmVRecIJJaUhgsKa-Cs1wKLZGT7BkyLnAQkkSwzOrBS4GqCz2hhfcHI55TRQ:1xTNFf:KfMtlIfzZkJ148eQoeaurpd6mN0s1W_WrIuObf9HFwM', '2026-12-01 17:45:51.180263'),
('empvv6lecle4xw9o3am3rrhbntxmi611', '.eJxVjLkOwjAQBf9l6yjKmlxOSU9Hb63tdQ6CLdlxhfh3BIqCUr43o3lBTpniHNRsYUAsju3DU0eGAbZImhayISoTaIwEfymGFQa4HwYUoChvk8qJ4y8J8vxpMg_2X2AX8mMoTfBbnHX5VcqdpvIWLK_X3T0FJkoTDMAOL2hJIzembdGJpu9Y2J57aqS0iLXR2rZOdLKqHLERVFeuqesOjSaW8P4Ar3ZVLQ:1xTNFf:k3DejkU3g7-8VZFXJCsbxzeHbkgC_njiRYLxtyLm6q8', '2026-12-01 17:45:51.309662'),
('gl38zn0kfq3t9574yxw6m8p8sxtip7ux', '.eJxVjEEOwiAQRe8y66YBYSB2p3vP0AwwWrSFBOjKeHejaTRd_v9e3hPWulKJeYwBBtv9ZsqLKwwDNK5Nwh-UPMMAp7DEFGsrFHKBDkZa2zSulcs3BLj_HPkHpw8Id0q33PucWomu_yj9Rmt_yYHn8-buAhPVCQbQRxXUwbBi7xnpiAfthdBBXY1CJiPROuGkFyzxaq03WpNBiYzGOkEBXm_rb1Bm:1xTV4d:lIo2s5yspzG5XB0a0NumZ0-QAmTqDdB0IefhvwVtlno', '2026-12-02 02:06:59.805493'),
('gyovp14nsl81l0ft2i4tyj9p62y72ehl', '.eJxVjMsOgjAQRf9l1oQU-hJ2uvcbyLQdoApt0tKV8d8NhmhY3ntOzgtKLph8HLyD_lL9ZoirSQQ92IhTQviTFBfo4epWH3zeErqYoIIByzYPJVP6lkCdP4P2SWEH7oFhirWNYUve1LtSHzTX9-houR3uKTBjnqEH0XHHW0WcrCWJnWyFZUw4PiouCVUjtWGmsYwaOWptlRCoZCNJKm0YOnh_AF0fUOQ:1xQVu0:CHQsPFek9chiTejXnpaoxf61FE1JNubb1SIBKPRhhsk', '2026-11-23 20:23:40.966017'),
('isde4qtdw4t0krthdsjvct8gmo3feixc', '.eJxVjMsOgjAQRf9l1oQU-hJ2uvcbyLQdoApt0tKV8d8NhmhY3ntOzgtKLph8HLyD_lL9ZoirSQQ92IhTQviTFBfo4epWH3zeErqYoIIByzYPJVP6lkCdP4P2SWEH7oFhirWNYUve1LtSHzTX9-houR3uKTBjnqEH0XHHW0WcrCWJnWyFZUw4PiouCVUjtWGmsYwaOWptlRCoZCNJKm0YOnh_AF0fUOQ:1xQrUs:cEHOOzADeXf5Q7qvqbdesmwaCZ95R2PuiUgaW16NaJI', '2026-11-24 19:27:10.898517'),
('k6jfou743h4ukqbrmv4z3sdil9x4mw3o', '.eJxVjMsKwjAQRf9l1qUkpLGPpbj1D4Qyk5k-fGQgNSvx36VSlC7vPYfzgrxkTLP2M0PXFr8Z9UFJoAPOErUPimNC-POkd-jglOWSjRmsQgE95ufU50XSNwb1_iMMN4kr4CvGUcug8ZlmKlel3OhSnpXlftzcXWDCZYIODHsfLNmm8bV3QxsMG-cqtuhbJofWVGwleHK2OjDRcPA01OhRJDBTDe8PCu5Sew:1xTNFf:pAtXi90bdlLICGQHFUTn33nT-fuMa1seuJPEumjSR0o', '2026-12-01 17:45:51.109780'),
('m9w0qcib9sj2cddx8tspai6c77tp6a33', '.eJxVjMsOgyAQRf9l1saAghSX7brfQGZ4qH1AArJq-u-NjWnj8t5zcl5QS8W8JLM4GDlrfjumJ2UPI9gUV3QpG5twygh_JacHjHDZOTRgsK6zqcXnbw5Ox4_Q3n3cgLthnFK7pfNC7aa0Oy3tNTn_OO_uITBjmWEE3QsmVRecIJJaUhgsKa-Cs1wKLZGT7BkyLnAQkkSwzOrBS4GqCz2hhfcHI55TRQ:1xTNgJ:rpHWeJq0ELF-GCcuhv5YuBbudNZO7lvMceHxWak1qgU', '2026-12-01 18:13:23.590617'),
('nsezwyc7mwxc993j7i1qjbfep74pvyag', '.eJxVjMsOgyAQRf9l1saAghSX7brfQGZ4qH1AArJq-u-NjWnj8t5zcl5QS8W8JLM4GDlrfjumJ2UPI9gUV3QpG5twygh_JacHjHDZOTRgsK6zqcXnbw5Ox4_Q3n3cgLthnFK7pfNC7aa0Oy3tNTn_OO_uITBjmWEE3QsmVRecIJJaUhgsKa-Cs1wKLZGT7BkyLnAQkkSwzOrBS4GqCz2hhfcHI55TRQ:1xTNk8:3hxNl6_As4NMcv6eFoEp1lG_Ro4B11Gz9WuGfX-6MQQ', '2026-12-01 18:17:20.040702');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `financial_ratio`
--

CREATE TABLE `financial_ratio` (
  `id` bigint(20) NOT NULL,
  `period` varchar(20) DEFAULT NULL,
  `calculation_date` datetime(6) DEFAULT NULL,
  `v1_current_ratio` decimal(8,4) DEFAULT NULL,
  `v2_working_capital_to_assets` decimal(8,4) DEFAULT NULL,
  `v3_total_leverage` decimal(8,4) DEFAULT NULL,
  `v4_operating_roa` decimal(8,4) DEFAULT NULL,
  `v5_operating_margin` decimal(8,4) DEFAULT NULL,
  `v6_asset_turnover` decimal(8,4) DEFAULT NULL,
  `v7_cash_flow_volatility` decimal(8,4) DEFAULT NULL,
  `confirmed_closures_count` int(11) DEFAULT NULL,
  `uses_neutral_volatility` tinyint(1) DEFAULT NULL,
  `ref_quick_ratio` decimal(8,4) DEFAULT NULL,
  `ref_cash_ratio` decimal(8,4) DEFAULT NULL,
  `ref_operating_coverage` decimal(8,4) DEFAULT NULL,
  `ref_altman_z_score` decimal(8,4) DEFAULT NULL,
  `is_validated` tinyint(1) DEFAULT NULL,
  `validation_date` datetime(6) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `upload_id` bigint(20) DEFAULT NULL,
  `validated_by_user_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `financial_ratio`
--

INSERT INTO `financial_ratio` (`id`, `period`, `calculation_date`, `v1_current_ratio`, `v2_working_capital_to_assets`, `v3_total_leverage`, `v4_operating_roa`, `v5_operating_margin`, `v6_asset_turnover`, `v7_cash_flow_volatility`, `confirmed_closures_count`, `uses_neutral_volatility`, `ref_quick_ratio`, `ref_cash_ratio`, `ref_operating_coverage`, `ref_altman_z_score`, `is_validated`, `validation_date`, `company_id`, `upload_id`, `validated_by_user_id`) VALUES
(1, '2022-03-01 00:00:00', '2026-11-12 15:27:46.868508', 1.4294, 0.2456, 4.0097, 0.0126, 0.0522, 0.2408, 0.0645, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:27:46.868508', 3, 1, 8),
(2, '2022-06-01 00:00:00', '2026-11-12 15:27:46.918508', 1.4646, 0.2541, 3.4722, 0.0376, 0.0663, 0.5674, 0.0645, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:27:46.918508', 3, 2, 8),
(3, '2022-09-01 00:00:00', '2026-11-12 15:27:46.968508', 1.2911, 0.1927, 4.3995, 0.0588, 0.0722, 0.8154, 0.0645, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:27:46.968508', 3, 3, 8),
(4, '2022-12-01 00:00:00', '2026-11-12 15:27:47.018508', 1.2301, 0.1616, 4.8378, 0.0829, 0.0711, 1.1654, 0.0645, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:27:47.018508', 3, 4, 8),
(5, '2023-03-01 00:00:00', '2026-11-12 15:48:19.085299', 1.3012, 0.1938, 3.8234, 0.0025, 0.0116, 0.2196, 0.0761, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:48:19.085299', 3, 5, 8),
(6, '2023-06-01 00:00:00', '2026-11-12 15:48:19.135299', 1.2990, 0.1861, 3.3328, 0.0016, 0.0032, 0.4978, 0.0761, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:48:19.135299', 3, 6, 8),
(7, '2023-09-01 00:00:00', '2026-11-12 15:48:19.185299', 1.2024, 0.1437, 4.5634, 0.0164, 0.0241, 0.6785, 0.0761, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:48:19.185299', 3, 7, 8),
(8, '2023-12-01 00:00:00', '2026-11-12 15:48:19.235299', 1.1705, 0.1272, 4.8063, 0.0453, 0.0461, 0.9830, 0.0761, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:48:19.235299', 3, 8, 8),
(9, '2025-03-01 00:00:00', '2026-11-12 15:56:18.551928', 1.2765, 0.1916, 3.8940, 0.0079, 0.0370, 0.2145, 0.0794, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:56:18.551928', 3, 9, 8),
(10, '2025-06-01 00:00:00', '2026-11-12 15:56:18.601928', 1.3719, 0.2370, 3.3207, 0.0180, 0.0372, 0.4852, 0.0794, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:56:18.601928', 3, 10, 8),
(11, '2025-09-01 00:00:00', '2026-11-12 15:56:18.651928', 1.2720, 0.1928, 4.3474, 0.0300, 0.0418, 0.7175, 0.0794, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:56:18.651928', 3, 11, 8),
(12, '2025-12-01 00:00:00', '2026-11-12 15:56:18.701928', 1.2859, 0.2028, 3.9613, 0.0651, 0.0631, 1.0326, 0.0794, NULL, 0, NULL, NULL, NULL, NULL, 1, '2026-11-12 15:56:18.701928', 3, 12, 8);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `financial_upload`
--

CREATE TABLE `financial_upload` (
  `id` bigint(20) NOT NULL,
  `upload_date` datetime(6) DEFAULT NULL,
  `period` varchar(20) DEFAULT NULL,
  `source_file` varchar(255) DEFAULT NULL,
  `upload_type` varchar(20) DEFAULT NULL,
  `current_assets` decimal(14,2) DEFAULT NULL,
  `current_liabilities` decimal(14,2) DEFAULT NULL,
  `total_assets` decimal(14,2) DEFAULT NULL,
  `total_liabilities` decimal(14,2) DEFAULT NULL,
  `equity` decimal(14,2) DEFAULT NULL,
  `net_revenue` decimal(14,2) DEFAULT NULL,
  `ebit` decimal(14,2) DEFAULT NULL,
  `retained_earnings` decimal(14,2) DEFAULT NULL,
  `net_income` decimal(14,2) DEFAULT NULL,
  `inventories` decimal(14,2) DEFAULT NULL,
  `cash_and_equivalents` decimal(14,2) DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  `detected_errors` longtext DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `financial_upload`
--

INSERT INTO `financial_upload` (`id`, `upload_date`, `period`, `source_file`, `upload_type`, `current_assets`, `current_liabilities`, `total_assets`, `total_liabilities`, `equity`, `net_revenue`, `ebit`, `retained_earnings`, `net_income`, `inventories`, `cash_and_equivalents`, `status`, `detected_errors`, `company_id`, `user_id`) VALUES
(1, '2026-11-12 15:27:46.868508', '2022-03-01 00:00:00', '2022.xlsx', 'Balance General', 128827890000.00, 90128288000.00, 157546069000.00, 126098138000.00, 31447912000.00, 37929863000.00, 1981323000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(2, '2026-11-12 15:27:46.918508', '2022-06-01 00:00:00', '2022.xlsx', 'Balance General', 125300341000.00, 85550578000.00, 156462510000.00, 121476687000.00, 34985804000.00, 88778594000.00, 5884079000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(3, '2026-11-12 15:27:46.968508', '2022-09-01 00:00:00', '2022.xlsx', 'Balance General', 176834132000.00, 136960078000.00, 206928960000.00, 168604871000.00, 38324070000.00, 168734778000.00, 12174941000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(4, '2026-11-12 15:27:47.018508', '2022-12-01 00:00:00', '2022.xlsx', 'Balance General', 184473218000.00, 149962509000.00, 213585394000.00, 176998699000.00, 36586676000.00, 248905967000.00, 17699872000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(5, '2026-11-12 15:48:19.085299', '2023-03-01 00:00:00', '2023.xlsx', 'Balance General', 148815344000.00, 114368906000.00, 177751520000.00, 140899230000.00, 36852271000.00, 39032183000.00, 451857000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(6, '2026-11-12 15:48:19.135299', '2023-06-01 00:00:00', '2023.xlsx', 'Balance General', 127268115000.00, 97972815000.00, 157387061000.00, 121062389000.00, 36324653000.00, 78353516000.00, 250250000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(7, '2026-11-12 15:48:19.185299', '2023-09-01 00:00:00', '2023.xlsx', 'Balance General', 181481468000.00, 150929951000.00, 212606123000.00, 174390734000.00, 38215370000.00, 144254208000.00, 3479244000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(8, '2026-11-12 15:48:19.235299', '2023-12-01 00:00:00', '2023.xlsx', 'Balance General', 207017461000.00, 176866095000.00, 237124078000.00, 196285296000.00, 40838763000.00, 233099186000.00, 10738840000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(9, '2026-11-12 15:56:18.551928', '2025-03-01 00:00:00', '2025.xlsx', 'Balance General', 211408415000.00, 165618535000.00, 238970959000.00, 190140405000.00, 48828901000.00, 51260479000.00, 1895684000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(10, '2026-11-12 15:56:18.601928', '2025-06-01 00:00:00', '2025.xlsx', 'Balance General', 184093455000.00, 134190545000.00, 210568260000.00, 161831644000.00, 48734871000.00, 102160465000.00, 3795413000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(11, '2026-11-12 15:56:18.651928', '2025-09-01 00:00:00', '2025.xlsx', 'Balance General', 244538874000.00, 192240123000.00, 271204847000.00, 220486724000.00, 50716385000.00, 194586804000.00, 8133298000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8),
(12, '2026-11-12 15:56:18.701928', '2025-12-01 00:00:00', '2025.xlsx', 'Balance General', 265307246000.00, 206317302000.00, 290936552000.00, 232295004000.00, 58641536000.00, 300430750000.00, 18948500000.00, NULL, NULL, NULL, NULL, 'PROCESADO', NULL, 3, 8);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `payment_method`
--

CREATE TABLE `payment_method` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) NOT NULL,
  `commission_percentage` decimal(5,2) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `payment_method`
--

INSERT INTO `payment_method` (`id`, `name`, `commission_percentage`, `is_active`, `company_id`) VALUES
(1, 'Efectivo', 0.00, 1, NULL),
(2, 'Débito', 1.75, 1, NULL),
(3, 'Crédito', 2.35, 1, NULL),
(4, 'Transferencia', 0.00, 1, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pdf_report`
--

CREATE TABLE `pdf_report` (
  `id` bigint(20) NOT NULL,
  `generation_date` datetime(6) DEFAULT NULL,
  `file_path` varchar(500) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `prediction_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `petty_cash_withdrawal`
--

CREATE TABLE `petty_cash_withdrawal` (
  `id` bigint(20) NOT NULL,
  `date` datetime(6) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `responsible_person` varchar(100) DEFAULT NULL,
  `closure_id` bigint(20) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prediction_history`
--

CREATE TABLE `prediction_history` (
  `id` bigint(20) NOT NULL,
  `prediction_date` datetime(6) NOT NULL,
  `score` double NOT NULL,
  `risk` varchar(20) NOT NULL,
  `current_ratio` double DEFAULT NULL,
  `quick_ratio` double DEFAULT NULL,
  `company_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recommendation`
--

CREATE TABLE `recommendation` (
  `id` bigint(20) NOT NULL,
  `source_variable` varchar(50) DEFAULT NULL,
  `risk_group` varchar(40) DEFAULT NULL,
  `text` longtext DEFAULT NULL,
  `priority` varchar(10) DEFAULT NULL,
  `prediction_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `recommendation`
--

INSERT INTO `recommendation` (`id`, `source_variable`, `risk_group`, `text`, `priority`, `prediction_id`) VALUES
(1, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 1),
(2, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 24.6% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 1),
(3, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-SOLV\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-droplet-fill\", \"titulo\": \"Mantenimiento de la Cobertura de Caja y Aprovechamiento de Descuentos\", \"plantilla_diagnostico\": \"La empresa dispone de ${cobertura_pesos} por cada $1.000 en deudas inmediatas, lo que representa una posición de liquidez cómoda y tranquila.\", \"que_hacer\": \"Mantener el colchón de seguridad en la cuenta bancaria y aprovechar esta holgura para solicitar a los proveedores descuentos por pago al contado o anticipado, reduciendo costos de compra.\", \"procedimiento\": \"1. Mantener reservas de caja para imprevistos. 2. Negociar rebajas de precios con proveedores pagando al contado.\", \"fuente\": \"Administración prudente de liquidez (Zurita, 2008).\", \"diagnostico_operativo\": \"La empresa dispone de $$1.429 por cada $1.000 en deudas inmediatas, lo que representa una posición de liquidez cómoda y tranquila.\"}', 'Baja', 1),
(4, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 4.0 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 1),
(5, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 2),
(6, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 25.4% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 2),
(7, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-SOLV\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-droplet-fill\", \"titulo\": \"Mantenimiento de la Cobertura de Caja y Aprovechamiento de Descuentos\", \"plantilla_diagnostico\": \"La empresa dispone de ${cobertura_pesos} por cada $1.000 en deudas inmediatas, lo que representa una posición de liquidez cómoda y tranquila.\", \"que_hacer\": \"Mantener el colchón de seguridad en la cuenta bancaria y aprovechar esta holgura para solicitar a los proveedores descuentos por pago al contado o anticipado, reduciendo costos de compra.\", \"procedimiento\": \"1. Mantener reservas de caja para imprevistos. 2. Negociar rebajas de precios con proveedores pagando al contado.\", \"fuente\": \"Administración prudente de liquidez (Zurita, 2008).\", \"diagnostico_operativo\": \"La empresa dispone de $$1.464 por cada $1.000 en deudas inmediatas, lo que representa una posición de liquidez cómoda y tranquila.\"}', 'Baja', 2),
(8, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 3.5 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 2),
(9, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 3),
(10, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 19.3% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 3),
(11, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 4.4 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 3),
(12, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-ALER\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-droplet\", \"titulo\": \"Sincronización del Calendario de Cobros y Pagos del Mes\", \"plantilla_diagnostico\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de ${cobertura_pesos}. La cobertura es justa y deja poco margen ante imprevistos operativos.\", \"que_hacer\": \"Organizar el calendario de pagos a proveedores de modo que coincida con las fechas en que entran los pagos de clientes. Evitar comprometer pagos en semanas donde no se tenga certeza de recaudación.\", \"procedimiento\": \"1. Ajustar plazos de crédito a clientes nuevos a un máximo de 30 días. 2. Realizar promociones para vender mercadería que lleva tiempo en bodega.\", \"fuente\": \"Control de ciclo de caja (Ringeling, 2004).\", \"diagnostico_operativo\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de $$1.291. La cobertura es justa y deja poco margen ante imprevistos operativos.\"}', 'Media', 3),
(13, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 4),
(14, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-ALER\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-wallet\", \"titulo\": \"Ajuste del Fondo de Reserva para Operaciones\", \"plantilla_diagnostico\": \"El capital disponible para el día a día representa el {valor_pct}% del total de recursos de la empresa, un nivel que aconseja prudencia en la programación de compras.\", \"que_hacer\": \"Planificar las compras de mercadería e insumos de acuerdo a las ventas reales del mes, evitando comprar en exceso para no dejar dinero inmovilizado en bodegas.\", \"procedimiento\": \"1. Comprar solo lo necesario para el mes. 2. Monitorear semanalmente la diferencia entre lo que se tiene por cobrar y lo que se debe pagar.\", \"fuente\": \"Fondo de maniobra operativo (Altman, 1983).\", \"diagnostico_operativo\": \"El capital disponible para el día a día representa el 16.2% del total de recursos de la empresa, un nivel que aconseja prudencia en la programación de compras.\"}', 'Media', 4),
(15, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 4.8 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 4),
(16, 'roa_operacional', 'Rentabilidad', '{\"id_codigo\": \"TACT-ROA-SOLV\", \"variable_origen\": \"roa_operacional\", \"grupo_riesgo\": \"Rentabilidad\", \"prioridad\": \"Baja\", \"icono\": \"bi-graph-up-arrow\", \"titulo\": \"Sostenimiento de la Alta Productividad de los Recursos\", \"plantilla_diagnostico\": \"Los bienes y equipos de la empresa presentan un buen rendimiento ({valor_pct}%), generando resultados operacionales sólidos para el negocio.\", \"que_hacer\": \"Mantener el buen cuidado y mantenimiento preventivo de las maquinarias y equipos para evitar fallas que detengan las ventas o generen gastos imprevistos.\", \"procedimiento\": \"1. Calendarizar mantenimientos periódicos. 2. Respaldar a las áreas de trabajo con mejor desempeño.\", \"fuente\": \"Rendimiento operativo sostenible (Riquelme, 2018).\", \"diagnostico_operativo\": \"Los bienes y equipos de la empresa presentan un buen rendimiento (16.2%), generando resultados operacionales sólidos para el negocio.\"}', 'Baja', 4),
(17, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 5),
(18, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 19.4% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 5),
(19, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-ALER\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-droplet\", \"titulo\": \"Sincronización del Calendario de Cobros y Pagos del Mes\", \"plantilla_diagnostico\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de ${cobertura_pesos}. La cobertura es justa y deja poco margen ante imprevistos operativos.\", \"que_hacer\": \"Organizar el calendario de pagos a proveedores de modo que coincida con las fechas en que entran los pagos de clientes. Evitar comprometer pagos en semanas donde no se tenga certeza de recaudación.\", \"procedimiento\": \"1. Ajustar plazos de crédito a clientes nuevos a un máximo de 30 días. 2. Realizar promociones para vender mercadería que lleva tiempo en bodega.\", \"fuente\": \"Control de ciclo de caja (Ringeling, 2004).\", \"diagnostico_operativo\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de $$1.301. La cobertura es justa y deja poco margen ante imprevistos operativos.\"}', 'Media', 5),
(20, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 3.8 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 5),
(21, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 6),
(22, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 18.6% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 6),
(23, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-ALER\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-droplet\", \"titulo\": \"Sincronización del Calendario de Cobros y Pagos del Mes\", \"plantilla_diagnostico\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de ${cobertura_pesos}. La cobertura es justa y deja poco margen ante imprevistos operativos.\", \"que_hacer\": \"Organizar el calendario de pagos a proveedores de modo que coincida con las fechas en que entran los pagos de clientes. Evitar comprometer pagos en semanas donde no se tenga certeza de recaudación.\", \"procedimiento\": \"1. Ajustar plazos de crédito a clientes nuevos a un máximo de 30 días. 2. Realizar promociones para vender mercadería que lleva tiempo en bodega.\", \"fuente\": \"Control de ciclo de caja (Ringeling, 2004).\", \"diagnostico_operativo\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de $$1.299. La cobertura es justa y deja poco margen ante imprevistos operativos.\"}', 'Media', 6),
(24, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 3.3 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 6),
(25, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 7),
(26, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-ALER\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-wallet\", \"titulo\": \"Ajuste del Fondo de Reserva para Operaciones\", \"plantilla_diagnostico\": \"El capital disponible para el día a día representa el {valor_pct}% del total de recursos de la empresa, un nivel que aconseja prudencia en la programación de compras.\", \"que_hacer\": \"Planificar las compras de mercadería e insumos de acuerdo a las ventas reales del mes, evitando comprar en exceso para no dejar dinero inmovilizado en bodegas.\", \"procedimiento\": \"1. Comprar solo lo necesario para el mes. 2. Monitorear semanalmente la diferencia entre lo que se tiene por cobrar y lo que se debe pagar.\", \"fuente\": \"Fondo de maniobra operativo (Altman, 1983).\", \"diagnostico_operativo\": \"El capital disponible para el día a día representa el 14.4% del total de recursos de la empresa, un nivel que aconseja prudencia en la programación de compras.\"}', 'Media', 7),
(27, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 4.6 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 7),
(28, 'volatilidad_flujo_caja', 'Flujo de Caja', '{\"id_codigo\": \"TACT-VOL-SOLV\", \"variable_origen\": \"volatilidad_flujo_caja\", \"grupo_riesgo\": \"Flujo de Caja\", \"prioridad\": \"Baja\", \"icono\": \"bi-activity\", \"titulo\": \"Regularidad y Tranquilidad en los Ingresos de Caja\", \"plantilla_diagnostico\": \"Las entradas de dinero en la empresa son regulares y constantes a lo largo del mes, lo que permite planificar compromisos y compras con alta tranquilidad.\", \"que_hacer\": \"Mantener acuerdos comerciales de largo plazo que aseguren la continuidad de los ingresos y faciliten el cumplimiento ordenado de todos los pagos.\", \"procedimiento\": \"1. Fidelizar a los clientes cumplidores con buen servicio y atención.\", \"fuente\": \"Constancia en recaudación operativa (Ringeling, 2004).\", \"diagnostico_operativo\": \"Las entradas de dinero en la empresa son regulares y constantes a lo largo del mes, lo que permite planificar compromisos y compras con alta tranquilidad.\"}', 'Baja', 7),
(29, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 8),
(30, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-ALER\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-wallet\", \"titulo\": \"Ajuste del Fondo de Reserva para Operaciones\", \"plantilla_diagnostico\": \"El capital disponible para el día a día representa el {valor_pct}% del total de recursos de la empresa, un nivel que aconseja prudencia en la programación de compras.\", \"que_hacer\": \"Planificar las compras de mercadería e insumos de acuerdo a las ventas reales del mes, evitando comprar en exceso para no dejar dinero inmovilizado en bodegas.\", \"procedimiento\": \"1. Comprar solo lo necesario para el mes. 2. Monitorear semanalmente la diferencia entre lo que se tiene por cobrar y lo que se debe pagar.\", \"fuente\": \"Fondo de maniobra operativo (Altman, 1983).\", \"diagnostico_operativo\": \"El capital disponible para el día a día representa el 12.7% del total de recursos de la empresa, un nivel que aconseja prudencia en la programación de compras.\"}', 'Media', 8),
(31, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 4.8 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 8),
(32, 'roa_operacional', 'Rentabilidad', '{\"id_codigo\": \"TACT-ROA-ALER\", \"variable_origen\": \"roa_operacional\", \"grupo_riesgo\": \"Rentabilidad\", \"prioridad\": \"Media\", \"icono\": \"bi-graph-up\", \"titulo\": \"Aumento en el Uso y Productividad de las Instalaciones\", \"plantilla_diagnostico\": \"El rendimiento de los activos se sitúa en un nivel modesto ({valor_pct}%), lo que indica que se puede producir o vender más con la misma infraestructura que ya se tiene.\", \"que_hacer\": \"Buscar alternativas para aumentar el volumen de ventas utilizando las mismas máquinas, locales o personal, reduciendo los costos fijos por cada producto vendido.\", \"procedimiento\": \"1. Optimizar los horarios y turnos de trabajo. 2. Enfocar las ventas en los productos de mayor rotación.\", \"fuente\": \"Eficiencia en activos empresariales (Riquelme, 2018).\", \"diagnostico_operativo\": \"El rendimiento de los activos se sitúa en un nivel modesto (12.7%), lo que indica que se puede producir o vender más con la misma infraestructura que ya se tiene.\"}', 'Media', 8),
(33, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 9),
(34, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 19.2% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 9),
(35, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-ALER\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-droplet\", \"titulo\": \"Sincronización del Calendario de Cobros y Pagos del Mes\", \"plantilla_diagnostico\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de ${cobertura_pesos}. La cobertura es justa y deja poco margen ante imprevistos operativos.\", \"que_hacer\": \"Organizar el calendario de pagos a proveedores de modo que coincida con las fechas en que entran los pagos de clientes. Evitar comprometer pagos en semanas donde no se tenga certeza de recaudación.\", \"procedimiento\": \"1. Ajustar plazos de crédito a clientes nuevos a un máximo de 30 días. 2. Realizar promociones para vender mercadería que lleva tiempo en bodega.\", \"fuente\": \"Control de ciclo de caja (Ringeling, 2004).\", \"diagnostico_operativo\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de $$1.276. La cobertura es justa y deja poco margen ante imprevistos operativos.\"}', 'Media', 9),
(36, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 3.9 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 9),
(37, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 10),
(38, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 23.7% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 10),
(39, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-SOLV\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-droplet-fill\", \"titulo\": \"Mantenimiento de la Cobertura de Caja y Aprovechamiento de Descuentos\", \"plantilla_diagnostico\": \"La empresa dispone de ${cobertura_pesos} por cada $1.000 en deudas inmediatas, lo que representa una posición de liquidez cómoda y tranquila.\", \"que_hacer\": \"Mantener el colchón de seguridad en la cuenta bancaria y aprovechar esta holgura para solicitar a los proveedores descuentos por pago al contado o anticipado, reduciendo costos de compra.\", \"procedimiento\": \"1. Mantener reservas de caja para imprevistos. 2. Negociar rebajas de precios con proveedores pagando al contado.\", \"fuente\": \"Administración prudente de liquidez (Zurita, 2008).\", \"diagnostico_operativo\": \"La empresa dispone de $$1.371 por cada $1.000 en deudas inmediatas, lo que representa una posición de liquidez cómoda y tranquila.\"}', 'Baja', 10);
INSERT INTO `recommendation` (`id`, `source_variable`, `risk_group`, `text`, `priority`, `prediction_id`) VALUES
(40, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 3.3 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 10),
(41, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 11),
(42, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 19.3% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 11),
(43, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-ALER\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-droplet\", \"titulo\": \"Sincronización del Calendario de Cobros y Pagos del Mes\", \"plantilla_diagnostico\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de ${cobertura_pesos}. La cobertura es justa y deja poco margen ante imprevistos operativos.\", \"que_hacer\": \"Organizar el calendario de pagos a proveedores de modo que coincida con las fechas en que entran los pagos de clientes. Evitar comprometer pagos en semanas donde no se tenga certeza de recaudación.\", \"procedimiento\": \"1. Ajustar plazos de crédito a clientes nuevos a un máximo de 30 días. 2. Realizar promociones para vender mercadería que lleva tiempo en bodega.\", \"fuente\": \"Control de ciclo de caja (Ringeling, 2004).\", \"diagnostico_operativo\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de $$1.272. La cobertura es justa y deja poco margen ante imprevistos operativos.\"}', 'Media', 11),
(44, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 4.3 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 11),
(45, 'macro_transicion', 'Consolidación y Crecimiento Prudente', '{\"id_codigo\": \"MACRO-V-V\", \"transicion\": \"Estable (Solvente -> Solvente)\", \"tipo\": \"Consolidación y Crecimiento Prudente\", \"prioridad\": \"Estratégica\", \"clase_badge\": \"badge-status-solvente\", \"icono\": \"bi-shield-check\", \"titulo\": \"Consolidación de la Estabilidad Financiera y Reinversión Prudente\", \"resumen_transicion\": \"La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.\", \"accion_principal\": \"Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos (menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.\", \"procedimiento_pasos\": [\"1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.\", \"2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.\", \"3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.\"], \"cita_fuente\": \"Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).\"}', 'Estratégic', 12),
(46, 'capital_trabajo_sobre_activos', 'Liquidez', '{\"id_codigo\": \"TACT-CT-SOLV\", \"variable_origen\": \"capital_trabajo_sobre_activos\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Baja\", \"icono\": \"bi-wallet-fill\", \"titulo\": \"Preservación de la Holgura Operativa del Negocio\", \"plantilla_diagnostico\": \"El capital de trabajo representa el {valor_pct}% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\", \"que_hacer\": \"Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan plazos de cobro razonables para no comprometer el capital de trabajo acumulado.\", \"procedimiento\": \"1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.\", \"fuente\": \"Solvencia en empresas operativas (Zurita, 2008).\", \"diagnostico_operativo\": \"El capital de trabajo representa el 20.3% de los activos, entregando un respaldo seguro para solventar las operaciones habituales.\"}', 'Baja', 12),
(47, 'razon_corriente', 'Liquidez', '{\"id_codigo\": \"TACT-RC-ALER\", \"variable_origen\": \"razon_corriente\", \"grupo_riesgo\": \"Liquidez\", \"prioridad\": \"Media\", \"icono\": \"bi-droplet\", \"titulo\": \"Sincronización del Calendario de Cobros y Pagos del Mes\", \"plantilla_diagnostico\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de ${cobertura_pesos}. La cobertura es justa y deja poco margen ante imprevistos operativos.\", \"que_hacer\": \"Organizar el calendario de pagos a proveedores de modo que coincida con las fechas en que entran los pagos de clientes. Evitar comprometer pagos en semanas donde no se tenga certeza de recaudación.\", \"procedimiento\": \"1. Ajustar plazos de crédito a clientes nuevos a un máximo de 30 días. 2. Realizar promociones para vender mercadería que lleva tiempo en bodega.\", \"fuente\": \"Control de ciclo de caja (Ringeling, 2004).\", \"diagnostico_operativo\": \"Por cada $1.000 en compromisos inmediatos, la empresa dispone de $$1.285. La cobertura es justa y deja poco margen ante imprevistos operativos.\"}', 'Media', 12),
(48, 'leverage_total', 'Endeudamiento', '{\"id_codigo\": \"TACT-LEV-CRIT\", \"variable_origen\": \"leverage_total\", \"grupo_riesgo\": \"Endeudamiento\", \"prioridad\": \"Alta\", \"icono\": \"bi-bank\", \"titulo\": \"Reprogramación de Deudas de Corto Plazo a Mayor Plazo\", \"plantilla_diagnostico\": \"El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\", \"que_hacer\": \"Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.\", \"procedimiento\": \"1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.\", \"fuente\": \"Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).\", \"diagnostico_operativo\": \"El nivel de deuda actual supera en 4.0 veces el patrimonio aportado por los dueños de la empresa. Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.\"}', 'Alta', 12);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `risk_prediction`
--

CREATE TABLE `risk_prediction` (
  `id` bigint(20) NOT NULL,
  `prediction_date` datetime(6) DEFAULT NULL,
  `risk_score` decimal(5,2) DEFAULT NULL,
  `traffic_light_level` varchar(10) DEFAULT NULL,
  `influential_variables` longtext DEFAULT NULL,
  `variable_impacts` longtext DEFAULT NULL,
  `model_version` varchar(50) DEFAULT NULL,
  `inference_time_ms` int(11) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `executed_by_user_id` bigint(20) DEFAULT NULL,
  `ratio_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `risk_prediction`
--

INSERT INTO `risk_prediction` (`id`, `prediction_date`, `risk_score`, `traffic_light_level`, `influential_variables`, `variable_impacts`, `model_version`, `inference_time_ms`, `company_id`, `executed_by_user_id`, `ratio_id`) VALUES
(1, '2026-11-12 15:27:48.619642', 4.44, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.2456, \"unidad\": \"%\", \"impacto_shap\": -0.25120772509663475, \"impacto_pct\": -25.12, \"impacto_abs\": 25.12, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 25.1% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -25.1% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.4294, \"unidad\": \"x\", \"impacto_shap\": -0.14471562275869573, \"impacto_pct\": -14.47, \"impacto_abs\": 14.47, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.5% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.5% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.0097, \"unidad\": \"x\", \"impacto_shap\": 0.10801806341408908, \"impacto_pct\": 10.8, \"impacto_abs\": 10.8, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +10.8% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +10.8% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.4294, \"unidad\": \"x\", \"impacto_shap\": -0.14471562275869573, \"impacto_pct\": -14.47, \"impacto_abs\": 14.47, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.5% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.5% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.2456, \"unidad\": \"%\", \"impacto_shap\": -0.25120772509663475, \"impacto_pct\": -25.12, \"impacto_abs\": 25.12, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 25.1% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -25.1% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.0097, \"unidad\": \"x\", \"impacto_shap\": 0.10801806341408908, \"impacto_pct\": 10.8, \"impacto_abs\": 10.8, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +10.8% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +10.8% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0126, \"unidad\": \"%\", \"impacto_shap\": -0.042476015268250254, \"impacto_pct\": -4.25, \"impacto_abs\": 4.25, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 4.2% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -4.2% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0522, \"unidad\": \"%\", \"impacto_shap\": -0.0370393347609317, \"impacto_pct\": -3.7, \"impacto_abs\": 3.7, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 3.7% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -3.7% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.2408, \"unidad\": \"x\", \"impacto_shap\": -0.011527096148693102, \"impacto_pct\": -1.15, \"impacto_abs\": 1.15, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 1.1% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -1.1% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0645, \"unidad\": \"ratio\", \"impacto_shap\": -0.07661795363567882, \"impacto_pct\": -7.66, \"impacto_abs\": 7.66, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 7.7% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -7.7% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 1548, 3, 8, 1),
(2, '2026-11-12 15:27:50.613663', 4.14, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.2541, \"unidad\": \"%\", \"impacto_shap\": -0.22375980881238647, \"impacto_pct\": -22.38, \"impacto_abs\": 22.38, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 22.4% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -22.4% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.4646, \"unidad\": \"x\", \"impacto_shap\": -0.13022708132711522, \"impacto_pct\": -13.02, \"impacto_abs\": 13.02, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 13.0% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -13.0% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.4722, \"unidad\": \"x\", \"impacto_shap\": 0.09612403086135254, \"impacto_pct\": 9.61, \"impacto_abs\": 9.61, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +9.6% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +9.6% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.4646, \"unidad\": \"x\", \"impacto_shap\": -0.13022708132711522, \"impacto_pct\": -13.02, \"impacto_abs\": 13.02, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 13.0% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -13.0% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.2541, \"unidad\": \"%\", \"impacto_shap\": -0.22375980881238647, \"impacto_pct\": -22.38, \"impacto_abs\": 22.38, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 22.4% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -22.4% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.4722, \"unidad\": \"x\", \"impacto_shap\": 0.09612403086135254, \"impacto_pct\": 9.61, \"impacto_abs\": 9.61, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +9.6% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +9.6% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0376, \"unidad\": \"%\", \"impacto_shap\": -0.082927474252061, \"impacto_pct\": -8.29, \"impacto_abs\": 8.29, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 8.3% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -8.3% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0663, \"unidad\": \"%\", \"impacto_shap\": -0.037566988603579356, \"impacto_pct\": -3.76, \"impacto_abs\": 3.76, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 3.8% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -3.8% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.5674, \"unidad\": \"x\", \"impacto_shap\": -0.014584496046048197, \"impacto_pct\": -1.46, \"impacto_abs\": 1.46, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 1.5% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -1.5% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0645, \"unidad\": \"ratio\", \"impacto_shap\": -0.06565372968547623, \"impacto_pct\": -6.57, \"impacto_abs\": 6.57, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 6.6% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -6.6% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 1487, 3, 8, 2),
(3, '2026-11-12 15:27:51.786325', 9.37, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1927, \"unidad\": \"%\", \"impacto_shap\": -0.19155535363889634, \"impacto_pct\": -19.16, \"impacto_abs\": 19.16, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 19.2% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -19.2% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.3995, \"unidad\": \"x\", \"impacto_shap\": 0.12439945542370402, \"impacto_pct\": 12.44, \"impacto_abs\": 12.44, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +12.4% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +12.4% al riesgo\", \"aumenta_riesgo\": true}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2911, \"unidad\": \"x\", \"impacto_shap\": -0.11464540712462373, \"impacto_pct\": -11.46, \"impacto_abs\": 11.46, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 11.5% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -11.5% al riesgo\", \"aumenta_riesgo\": false}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2911, \"unidad\": \"x\", \"impacto_shap\": -0.11464540712462373, \"impacto_pct\": -11.46, \"impacto_abs\": 11.46, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 11.5% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -11.5% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1927, \"unidad\": \"%\", \"impacto_shap\": -0.19155535363889634, \"impacto_pct\": -19.16, \"impacto_abs\": 19.16, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 19.2% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -19.2% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.3995, \"unidad\": \"x\", \"impacto_shap\": 0.12439945542370402, \"impacto_pct\": 12.44, \"impacto_abs\": 12.44, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +12.4% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +12.4% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0588, \"unidad\": \"%\", \"impacto_shap\": -0.08568170179289182, \"impacto_pct\": -8.57, \"impacto_abs\": 8.57, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 8.6% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -8.6% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0722, \"unidad\": \"%\", \"impacto_shap\": -0.045388521670647865, \"impacto_pct\": -4.54, \"impacto_abs\": 4.54, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 4.5% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -4.5% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.8154, \"unidad\": \"x\", \"impacto_shap\": -0.02967072537358266, \"impacto_pct\": -2.97, \"impacto_abs\": 2.97, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 3.0% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -3.0% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0645, \"unidad\": \"ratio\", \"impacto_shap\": -0.06373331865991788, \"impacto_pct\": -6.37, \"impacto_abs\": 6.37, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 6.4% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -6.4% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 837, 3, 8, 3),
(4, '2026-11-12 15:27:53.370594', 13.33, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1616, \"unidad\": \"%\", \"impacto_shap\": -0.17418206222467025, \"impacto_pct\": -17.42, \"impacto_abs\": 17.42, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 17.4% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -17.4% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.8378, \"unidad\": \"x\", \"impacto_shap\": 0.14752724054411465, \"impacto_pct\": 14.75, \"impacto_abs\": 14.75, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +14.8% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +14.8% al riesgo\", \"aumenta_riesgo\": true}, {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0829, \"unidad\": \"%\", \"impacto_shap\": -0.11868819216871482, \"impacto_pct\": -11.87, \"impacto_abs\": 11.87, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 11.9% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -11.9% al riesgo\", \"aumenta_riesgo\": false}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2301, \"unidad\": \"x\", \"impacto_shap\": -0.08764575027186855, \"impacto_pct\": -8.76, \"impacto_abs\": 8.76, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 8.8% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -8.8% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1616, \"unidad\": \"%\", \"impacto_shap\": -0.17418206222467025, \"impacto_pct\": -17.42, \"impacto_abs\": 17.42, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 17.4% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -17.4% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.8378, \"unidad\": \"x\", \"impacto_shap\": 0.14752724054411465, \"impacto_pct\": 14.75, \"impacto_abs\": 14.75, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +14.8% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +14.8% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0829, \"unidad\": \"%\", \"impacto_shap\": -0.11868819216871482, \"impacto_pct\": -11.87, \"impacto_abs\": 11.87, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 11.9% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -11.9% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0711, \"unidad\": \"%\", \"impacto_shap\": -0.042785958098429056, \"impacto_pct\": -4.28, \"impacto_abs\": 4.28, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 4.3% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -4.3% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 1.1654, \"unidad\": \"x\", \"impacto_shap\": -0.033815852321688745, \"impacto_pct\": -3.38, \"impacto_abs\": 3.38, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 3.4% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -3.4% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0645, \"unidad\": \"ratio\", \"impacto_shap\": -0.057110262364762555, \"impacto_pct\": -5.71, \"impacto_abs\": 5.71, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 5.7% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -5.7% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 1144, 3, 8, 4),
(5, '2026-11-12 15:48:20.097818', 14.41, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1938, \"unidad\": \"%\", \"impacto_shap\": -0.2293618653595786, \"impacto_pct\": -22.94, \"impacto_abs\": 22.94, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 22.9% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -22.9% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.3012, \"unidad\": \"x\", \"impacto_shap\": -0.14341877000490633, \"impacto_pct\": -14.34, \"impacto_abs\": 14.34, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.3% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.3% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.8234, \"unidad\": \"x\", \"impacto_shap\": 0.12478794037357767, \"impacto_pct\": 12.48, \"impacto_abs\": 12.48, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +12.5% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +12.5% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.3012, \"unidad\": \"x\", \"impacto_shap\": -0.14341877000490633, \"impacto_pct\": -14.34, \"impacto_abs\": 14.34, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.3% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.3% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1938, \"unidad\": \"%\", \"impacto_shap\": -0.2293618653595786, \"impacto_pct\": -22.94, \"impacto_abs\": 22.94, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 22.9% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -22.9% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.8234, \"unidad\": \"x\", \"impacto_shap\": 0.12478794037357767, \"impacto_pct\": 12.48, \"impacto_abs\": 12.48, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +12.5% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +12.5% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0025, \"unidad\": \"%\", \"impacto_shap\": -0.0030281279385669263, \"impacto_pct\": -0.3, \"impacto_abs\": 0.3, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 0.3% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -0.3% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0116, \"unidad\": \"%\", \"impacto_shap\": 0.0033690582574515855, \"impacto_pct\": 0.34, \"impacto_abs\": 0.34, \"texto\": \"La caída del Margen Operacional aportó directamente al riesgo (aportó un +0.3% al riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un +0.3% al riesgo\", \"aumenta_riesgo\": true}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.2196, \"unidad\": \"x\", \"impacto_shap\": -0.009489218888055411, \"impacto_pct\": -0.95, \"impacto_abs\": 0.95, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 0.9% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -0.9% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0761, \"unidad\": \"ratio\", \"impacto_shap\": -0.09871976745463781, \"impacto_pct\": -9.87, \"impacto_abs\": 9.87, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 9.9% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -9.9% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 841, 3, 8, 5),
(6, '2026-11-12 15:48:21.419751', 19.62, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1861, \"unidad\": \"%\", \"impacto_shap\": -0.20913590241491262, \"impacto_pct\": -20.91, \"impacto_abs\": 20.91, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 20.9% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -20.9% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.299, \"unidad\": \"x\", \"impacto_shap\": -0.14027001592584612, \"impacto_pct\": -14.03, \"impacto_abs\": 14.03, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.0% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.0% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.3328, \"unidad\": \"x\", \"impacto_shap\": 0.12626267887609177, \"impacto_pct\": 12.63, \"impacto_abs\": 12.63, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +12.6% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +12.6% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.299, \"unidad\": \"x\", \"impacto_shap\": -0.14027001592584612, \"impacto_pct\": -14.03, \"impacto_abs\": 14.03, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.0% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.0% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1861, \"unidad\": \"%\", \"impacto_shap\": -0.20913590241491262, \"impacto_pct\": -20.91, \"impacto_abs\": 20.91, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 20.9% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -20.9% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.3328, \"unidad\": \"x\", \"impacto_shap\": 0.12626267887609177, \"impacto_pct\": 12.63, \"impacto_abs\": 12.63, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +12.6% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +12.6% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0016, \"unidad\": \"%\", \"impacto_shap\": -0.006651242047335956, \"impacto_pct\": -0.67, \"impacto_abs\": 0.67, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 0.7% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -0.7% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0032, \"unidad\": \"%\", \"impacto_shap\": 0.027580342019732147, \"impacto_pct\": 2.76, \"impacto_abs\": 2.76, \"texto\": \"La caída del Margen Operacional aportó directamente al riesgo (aportó un +2.8% al riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un +2.8% al riesgo\", \"aumenta_riesgo\": true}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.4978, \"unidad\": \"x\", \"impacto_shap\": -0.011093452226273826, \"impacto_pct\": -1.11, \"impacto_abs\": 1.11, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 1.1% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -1.1% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0761, \"unidad\": \"ratio\", \"impacto_shap\": -0.0905396737467425, \"impacto_pct\": -9.05, \"impacto_abs\": 9.05, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 9.1% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -9.1% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 913, 3, 8, 6),
(7, '2026-11-12 15:48:22.523337', 17.03, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1437, \"unidad\": \"%\", \"impacto_shap\": -0.2072383823975489, \"impacto_pct\": -20.72, \"impacto_abs\": 20.72, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 20.7% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -20.7% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.5634, \"unidad\": \"x\", \"impacto_shap\": 0.1404627390474468, \"impacto_pct\": 14.05, \"impacto_abs\": 14.05, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +14.1% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +14.1% al riesgo\", \"aumenta_riesgo\": true}, {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0761, \"unidad\": \"ratio\", \"impacto_shap\": -0.08662062569488747, \"impacto_pct\": -8.66, \"impacto_abs\": 8.66, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 8.7% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -8.7% al riesgo\", \"aumenta_riesgo\": false}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2024, \"unidad\": \"x\", \"impacto_shap\": -0.07416144234995348, \"impacto_pct\": -7.42, \"impacto_abs\": 7.42, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 7.4% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -7.4% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1437, \"unidad\": \"%\", \"impacto_shap\": -0.2072383823975489, \"impacto_pct\": -20.72, \"impacto_abs\": 20.72, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 20.7% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -20.7% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.5634, \"unidad\": \"x\", \"impacto_shap\": 0.1404627390474468, \"impacto_pct\": 14.05, \"impacto_abs\": 14.05, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +14.1% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +14.1% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0164, \"unidad\": \"%\", \"impacto_shap\": -0.06578751417001387, \"impacto_pct\": -6.58, \"impacto_abs\": 6.58, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 6.6% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -6.6% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0241, \"unidad\": \"%\", \"impacto_shap\": -0.009292387757676468, \"impacto_pct\": -0.93, \"impacto_abs\": 0.93, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 0.9% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -0.9% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.6785, \"unidad\": \"x\", \"impacto_shap\": -0.02701425623054187, \"impacto_pct\": -2.7, \"impacto_abs\": 2.7, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 2.7% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -2.7% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0761, \"unidad\": \"ratio\", \"impacto_shap\": -0.08662062569488747, \"impacto_pct\": -8.66, \"impacto_abs\": 8.66, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 8.7% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -8.7% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 744, 3, 8, 7),
(8, '2026-11-12 15:48:23.702363', 16.81, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1272, \"unidad\": \"%\", \"impacto_shap\": -0.1974637608732527, \"impacto_pct\": -19.75, \"impacto_abs\": 19.75, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 19.8% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -19.8% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.8063, \"unidad\": \"x\", \"impacto_shap\": 0.13077624315287212, \"impacto_pct\": 13.08, \"impacto_abs\": 13.08, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +13.1% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +13.1% al riesgo\", \"aumenta_riesgo\": true}, {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0453, \"unidad\": \"%\", \"impacto_shap\": -0.0969902744777408, \"impacto_pct\": -9.7, \"impacto_abs\": 9.7, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 9.7% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -9.7% al riesgo\", \"aumenta_riesgo\": false}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.1705, \"unidad\": \"x\", \"impacto_shap\": -0.03878190586379603, \"impacto_pct\": -3.88, \"impacto_abs\": 3.88, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 3.9% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -3.9% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1272, \"unidad\": \"%\", \"impacto_shap\": -0.1974637608732527, \"impacto_pct\": -19.75, \"impacto_abs\": 19.75, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 19.8% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -19.8% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.8063, \"unidad\": \"x\", \"impacto_shap\": 0.13077624315287212, \"impacto_pct\": 13.08, \"impacto_abs\": 13.08, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +13.1% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +13.1% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0453, \"unidad\": \"%\", \"impacto_shap\": -0.0969902744777408, \"impacto_pct\": -9.7, \"impacto_abs\": 9.7, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 9.7% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -9.7% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0461, \"unidad\": \"%\", \"impacto_shap\": -0.029027279684359707, \"impacto_pct\": -2.9, \"impacto_abs\": 2.9, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 2.9% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -2.9% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.983, \"unidad\": \"x\", \"impacto_shap\": -0.03605940387708038, \"impacto_pct\": -3.61, \"impacto_abs\": 3.61, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 3.6% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -3.6% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0761, \"unidad\": \"ratio\", \"impacto_shap\": -0.06436518955264578, \"impacto_pct\": -6.44, \"impacto_abs\": 6.44, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 6.4% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -6.4% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 902, 3, 8, 8),
(9, '2026-11-12 15:56:19.656996', 5.29, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1916, \"unidad\": \"%\", \"impacto_shap\": -0.2418887560178469, \"impacto_pct\": -24.19, \"impacto_abs\": 24.19, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 24.2% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -24.2% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2765, \"unidad\": \"x\", \"impacto_shap\": -0.14036779304954755, \"impacto_pct\": -14.04, \"impacto_abs\": 14.04, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.0% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.0% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.894, \"unidad\": \"x\", \"impacto_shap\": 0.11283064238651257, \"impacto_pct\": 11.28, \"impacto_abs\": 11.28, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +11.3% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +11.3% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2765, \"unidad\": \"x\", \"impacto_shap\": -0.14036779304954755, \"impacto_pct\": -14.04, \"impacto_abs\": 14.04, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 14.0% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -14.0% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1916, \"unidad\": \"%\", \"impacto_shap\": -0.2418887560178469, \"impacto_pct\": -24.19, \"impacto_abs\": 24.19, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 24.2% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -24.2% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.894, \"unidad\": \"x\", \"impacto_shap\": 0.11283064238651257, \"impacto_pct\": 11.28, \"impacto_abs\": 11.28, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +11.3% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +11.3% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0079, \"unidad\": \"%\", \"impacto_shap\": -0.03943560201967089, \"impacto_pct\": -3.94, \"impacto_abs\": 3.94, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 3.9% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -3.9% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.037, \"unidad\": \"%\", \"impacto_shap\": -0.041838010215226505, \"impacto_pct\": -4.18, \"impacto_abs\": 4.18, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 4.2% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -4.2% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.2145, \"unidad\": \"x\", \"impacto_shap\": -0.011918683057282782, \"impacto_pct\": -1.19, \"impacto_abs\": 1.19, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 1.2% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -1.2% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0794, \"unidad\": \"ratio\", \"impacto_shap\": -0.08446700432255218, \"impacto_pct\": -8.45, \"impacto_abs\": 8.45, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 8.4% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -8.4% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 974, 3, 8, 9);
INSERT INTO `risk_prediction` (`id`, `prediction_date`, `risk_score`, `traffic_light_level`, `influential_variables`, `variable_impacts`, `model_version`, `inference_time_ms`, `company_id`, `executed_by_user_id`, `ratio_id`) VALUES
(10, '2026-11-12 15:56:20.954496', 7.59, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.237, \"unidad\": \"%\", \"impacto_shap\": -0.23467416668164104, \"impacto_pct\": -23.47, \"impacto_abs\": 23.47, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 23.5% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -23.5% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.3719, \"unidad\": \"x\", \"impacto_shap\": -0.13818091774915767, \"impacto_pct\": -13.82, \"impacto_abs\": 13.82, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 13.8% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -13.8% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.3207, \"unidad\": \"x\", \"impacto_shap\": 0.11055105323961642, \"impacto_pct\": 11.06, \"impacto_abs\": 11.06, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +11.1% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +11.1% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.3719, \"unidad\": \"x\", \"impacto_shap\": -0.13818091774915767, \"impacto_pct\": -13.82, \"impacto_abs\": 13.82, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 13.8% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -13.8% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.237, \"unidad\": \"%\", \"impacto_shap\": -0.23467416668164104, \"impacto_pct\": -23.47, \"impacto_abs\": 23.47, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 23.5% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -23.5% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.3207, \"unidad\": \"x\", \"impacto_shap\": 0.11055105323961642, \"impacto_pct\": 11.06, \"impacto_abs\": 11.06, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +11.1% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +11.1% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.018, \"unidad\": \"%\", \"impacto_shap\": -0.04886162591665062, \"impacto_pct\": -4.89, \"impacto_abs\": 4.89, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 4.9% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -4.9% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0372, \"unidad\": \"%\", \"impacto_shap\": -0.02693933875780832, \"impacto_pct\": -2.69, \"impacto_abs\": 2.69, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 2.7% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -2.7% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.4852, \"unidad\": \"x\", \"impacto_shap\": -0.015053376084470094, \"impacto_pct\": -1.51, \"impacto_abs\": 1.51, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 1.5% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -1.5% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0794, \"unidad\": \"ratio\", \"impacto_shap\": -0.07090331162649041, \"impacto_pct\": -7.09, \"impacto_abs\": 7.09, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 7.1% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -7.1% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 660, 3, 8, 10),
(11, '2026-11-12 15:56:22.020003', 5.97, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1928, \"unidad\": \"%\", \"impacto_shap\": -0.2133927186658479, \"impacto_pct\": -21.34, \"impacto_abs\": 21.34, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 21.3% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -21.3% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.272, \"unidad\": \"x\", \"impacto_shap\": -0.13120793124375865, \"impacto_pct\": -13.12, \"impacto_abs\": 13.12, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 13.1% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -13.1% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.3474, \"unidad\": \"x\", \"impacto_shap\": 0.11762211619095153, \"impacto_pct\": 11.76, \"impacto_abs\": 11.76, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +11.8% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +11.8% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.272, \"unidad\": \"x\", \"impacto_shap\": -0.13120793124375865, \"impacto_pct\": -13.12, \"impacto_abs\": 13.12, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 13.1% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -13.1% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.1928, \"unidad\": \"%\", \"impacto_shap\": -0.2133927186658479, \"impacto_pct\": -21.34, \"impacto_abs\": 21.34, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 21.3% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -21.3% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 4.3474, \"unidad\": \"x\", \"impacto_shap\": 0.11762211619095153, \"impacto_pct\": 11.76, \"impacto_abs\": 11.76, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +11.8% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +11.8% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.03, \"unidad\": \"%\", \"impacto_shap\": -0.07601916187635437, \"impacto_pct\": -7.6, \"impacto_abs\": 7.6, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 7.6% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -7.6% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0418, \"unidad\": \"%\", \"impacto_shap\": -0.03952788666944264, \"impacto_pct\": -3.95, \"impacto_abs\": 3.95, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 4.0% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -4.0% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 0.7175, \"unidad\": \"x\", \"impacto_shap\": -0.024720397547029597, \"impacto_pct\": -2.47, \"impacto_abs\": 2.47, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 2.5% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -2.5% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0794, \"unidad\": \"ratio\", \"impacto_shap\": -0.07308368472598721, \"impacto_pct\": -7.31, \"impacto_abs\": 7.31, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 7.3% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -7.3% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 646, 3, 8, 11),
(12, '2026-11-12 15:56:23.235206', 5.13, 'Verde', '[{\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.2028, \"unidad\": \"%\", \"impacto_shap\": -0.19744666781282538, \"impacto_pct\": -19.74, \"impacto_abs\": 19.74, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 19.7% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -19.7% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2859, \"unidad\": \"x\", \"impacto_shap\": -0.12137847933386157, \"impacto_pct\": -12.14, \"impacto_abs\": 12.14, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 12.1% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -12.1% al riesgo\", \"aumenta_riesgo\": false}, {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.9613, \"unidad\": \"x\", \"impacto_shap\": 0.09720572067188378, \"impacto_pct\": 9.72, \"impacto_abs\": 9.72, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +9.7% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +9.7% al riesgo\", \"aumenta_riesgo\": true}]', '{\"razon_corriente\": {\"codigo\": \"X1\", \"clave\": \"razon_corriente\", \"nombre\": \"Razón Corriente\", \"grupo\": \"Liquidez\", \"valor\": 1.2859, \"unidad\": \"x\", \"impacto_shap\": -0.12137847933386157, \"impacto_pct\": -12.14, \"impacto_abs\": 12.14, \"texto\": \"La sólida Razón Corriente fortalece la liquidez y reduce el riesgo (redujo un 12.1% el riesgo)\", \"texto_resumen\": \"La variación de Razón Corriente aportó un -12.1% al riesgo\", \"aumenta_riesgo\": false}, \"capital_trabajo_sobre_activos\": {\"codigo\": \"X2\", \"clave\": \"capital_trabajo_sobre_activos\", \"nombre\": \"Capital de Trabajo sobre Activos\", \"grupo\": \"Liquidez\", \"valor\": 0.2028, \"unidad\": \"%\", \"impacto_shap\": -0.19744666781282538, \"impacto_pct\": -19.74, \"impacto_abs\": 19.74, \"texto\": \"El excedente de Capital de Trabajo amortigua contingencias operativas (redujo un 19.7% el riesgo)\", \"texto_resumen\": \"La variación de Capital de Trabajo sobre Activos aportó un -19.7% al riesgo\", \"aumenta_riesgo\": false}, \"leverage_total\": {\"codigo\": \"X3\", \"clave\": \"leverage_total\", \"nombre\": \"Leverage Total\", \"grupo\": \"Endeudamiento\", \"valor\": 3.9613, \"unidad\": \"x\", \"impacto_shap\": 0.09720572067188378, \"impacto_pct\": 9.72, \"impacto_abs\": 9.72, \"texto\": \"El bajo apalancamiento financiero mantiene controlado el endeudamiento (aportó un +9.7% al riesgo)\", \"texto_resumen\": \"La variación de Leverage Total aportó un +9.7% al riesgo\", \"aumenta_riesgo\": true}, \"roa_operacional\": {\"codigo\": \"X4\", \"clave\": \"roa_operacional\", \"nombre\": \"ROA Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0651, \"unidad\": \"%\", \"impacto_shap\": -0.09345886203442448, \"impacto_pct\": -9.35, \"impacto_abs\": 9.35, \"texto\": \"El buen rendimiento de activos (ROA) apoya la solidez del negocio (redujo un 9.3% el riesgo)\", \"texto_resumen\": \"La variación de ROA Operacional aportó un -9.3% al riesgo\", \"aumenta_riesgo\": false}, \"margen_operacional\": {\"codigo\": \"X5\", \"clave\": \"margen_operacional\", \"nombre\": \"Margen Operacional\", \"grupo\": \"Rentabilidad\", \"valor\": 0.0631, \"unidad\": \"%\", \"impacto_shap\": -0.040792945704244785, \"impacto_pct\": -4.08, \"impacto_abs\": 4.08, \"texto\": \"El sólido Margen Operacional genera un flujo saludable para el negocio (redujo un 4.1% el riesgo)\", \"texto_resumen\": \"La variación de Margen Operacional aportó un -4.1% al riesgo\", \"aumenta_riesgo\": false}, \"rotacion_activos\": {\"codigo\": \"X6\", \"clave\": \"rotacion_activos\", \"nombre\": \"Rotación de Activos\", \"grupo\": \"Eficiencia\", \"valor\": 1.0326, \"unidad\": \"x\", \"impacto_shap\": -0.029825932795220764, \"impacto_pct\": -2.98, \"impacto_abs\": 2.98, \"texto\": \"La alta Rotación de Activos demuestra eficiencia comercial y operativa (redujo un 3.0% el riesgo)\", \"texto_resumen\": \"La variación de Rotación de Activos aportó un -3.0% al riesgo\", \"aumenta_riesgo\": false}, \"volatilidad_flujo_caja\": {\"codigo\": \"X7\", \"clave\": \"volatilidad_flujo_caja\", \"nombre\": \"Volatilidad del Flujo de Caja\", \"grupo\": \"Flujo de Caja\", \"valor\": 0.0794, \"unidad\": \"ratio\", \"impacto_shap\": -0.06299833891236088, \"impacto_pct\": -6.3, \"impacto_abs\": 6.3, \"texto\": \"La alta dispersión en los flujos diarios de caja aumenta la incertidumbre (redujo un 6.3% el riesgo)\", \"texto_resumen\": \"La variación de Volatilidad del Flujo de Caja aportó un -6.3% al riesgo\", \"aumenta_riesgo\": false}}', 'v13_trimestral_optimizado', 660, 3, 8, 12);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `role`
--

CREATE TABLE `role` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `role`
--

INSERT INTO `role` (`id`, `name`, `description`) VALUES
(1, 'Dueño', 'Gerencia, visualización de dashboard, registro de retiros de caja chica y cuadratura diaria'),
(2, 'Contador', 'Carga de planillas ETL, ejecución de predicciones y revisión contable'),
(3, 'Trabajador', 'Registro de ventas operativas con método de pago y descuentos diarios'),
(4, 'Administrador', 'Gestión técnica de usuarios, roles y permisos de la plataforma');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sale`
--

CREATE TABLE `sale` (
  `id` bigint(20) NOT NULL,
  `date` datetime(6) DEFAULT NULL,
  `gross_total` decimal(10,2) DEFAULT NULL,
  `discount_type` varchar(10) DEFAULT NULL,
  `discount_amount` decimal(10,2) DEFAULT NULL,
  `charged_total` decimal(10,2) DEFAULT NULL,
  `applied_commission` decimal(10,2) DEFAULT NULL,
  `net_income` decimal(10,2) DEFAULT NULL,
  `closure_id` bigint(20) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `payment_method_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sale`
--

INSERT INTO `sale` (`id`, `date`, `gross_total`, `discount_type`, `discount_amount`, `charged_total`, `applied_commission`, `net_income`, `closure_id`, `company_id`, `payment_method_id`, `user_id`) VALUES
(1, '2026-11-12 15:20:44.522375', 50000.00, 'Sin Desc', 0.00, 50000.00, 875.00, 49125.00, 1, 3, 2, 8),
(2, '2026-11-12 15:20:52.102454', 24000.00, 'Sin Desc', 0.00, 24000.00, 420.00, 23580.00, 1, 3, 2, 8),
(3, '2026-11-12 15:21:00.856669', 3000.00, 'Sin Desc', 0.00, 3000.00, 0.00, 3000.00, 1, 3, 1, 8),
(4, '2026-11-12 15:21:06.781902', 1700.00, 'Sin Desc', 0.00, 1700.00, 0.00, 1700.00, 1, 3, 1, 8),
(5, '2026-11-12 15:21:22.057762', 4050.00, 'Sin Desc', 0.00, 4050.00, 0.00, 4050.00, 1, 3, 1, 8);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `upload_state`
--

CREATE TABLE `upload_state` (
  `id` bigint(20) NOT NULL,
  `csv_path` varchar(500) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `upload_state`
--

INSERT INTO `upload_state` (`id`, `csv_path`, `updated_at`) VALUES
(1, NULL, '2026-11-12 15:56:23.604160');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` bigint(20) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `role_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `user`
--

INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `is_active`, `created_at`, `last_login`, `company_id`, `role_id`) VALUES
(1, 'Alexis', 'admin@nstock.cl', 'pbkdf2_sha256$600000$KbtTH8eCRccGACC1MWekWR$Pryx8YSzQ+L4HzBWwbu2OYMi9kL+gHX/s8jxv9Vk8Y8=', 1, '2026-11-03 12:25:42.000000', NULL, 1, 4),
(2, 'admin', 'admin@admin.cl', 'pbkdf2_sha256$600000$YeAOLQCylZseIX7LFNquCZ$mOzLcdNeAzW8HfTp7phi2spAdsvR5LpS1oE/tpFDp4k=', 1, '2026-11-03 12:25:42.000000', '2026-11-04 18:46:55.074005', 2, 4),
(7, 'test1', 'test1@test.cl', 'pbkdf2_sha256$600000$kIudPsIDeg9akKAxQhLMPS$La+HJop9usfYk2SXnQxMRSF5vKPdRs82WJKvQldWW40=', 1, '2026-11-04 18:55:47.053246', '2026-11-18 02:10:07.493823', 2, 4),
(8, 'coagra', 'admin@coagra.cl', 'pbkdf2_sha256$600000$N4jS2gOIBQk6fo2KQW6Rqs$2JGFm+8peE4+gZaMeADjw6lfxd4sxx/6hKQs8HuDSbs=', 1, '2026-11-09 20:23:40.025729', '2026-11-12 15:20:28.701420', 3, 4),
(9, 'dueno_coagra', 'dueno@coagra.cl', 'pbkdf2_sha256$600000$1imK7H6gfkuwkCXH0utbgq$QIqFnTDgP+OW1RcRdrun2/qpa3/1FUUq2lsVJjHXwog=', 1, '2026-11-17 17:03:14.811098', '2026-11-17 18:12:41.364058', 3, 1),
(10, 'contador_coagra', 'contador@coagra.cl', 'pbkdf2_sha256$600000$9TiMIy23KiMhIQQMjlS4kl$B2FS66O1jaHc8hUSMbGhCSI6u6t9ooU8akxnX3JJAlw=', 1, '2026-11-17 17:03:18.229793', '2026-11-17 18:17:19.913479', 3, 2),
(11, 'trabajador_coagra', 'trabajador@coagra.cl', 'pbkdf2_sha256$600000$HynrNczt6r7RelMqCSF5UA$Wi0a67t5IULKB776qV35aYkjKmTujaODB87uhbz6zTI=', 1, '2026-11-17 17:03:21.146292', '2026-11-17 18:13:09.052358', 3, 3),
(13, 'TestDueño', 'propietario@test.cl', 'pbkdf2_sha256$600000$V6foaa29XbR3Fop5Z7KXLl$akPpNBbUoOOd7EXrkEGb4JgPeJeZ2Obb681VIIDK1jA=', 1, '2026-11-19 18:23:23.373800', '2026-11-19 18:23:24.617527', 3, 1),
(14, 'TestContador', 'contador@test.cl', 'pbkdf2_sha256$600000$pXgXgBE7925ZEAojGbL9Ak$/syAxSfGgci1A6tOC9RhPPhI/rV2Rqcla44Gh8hqjsE=', 1, '2026-11-19 18:24:32.716183', '2026-11-19 18:24:33.924506', 3, 2),
(15, 'TestTrabajador', 'trabajador@test.cl', 'pbkdf2_sha256$600000$3cBGFEl6wdhzaKtIDskchR$v8nOoZdlZpV5wX5F0PIWU8ib0wlRZiOXqaGlENTcnQA=', 1, '2026-11-19 18:25:36.823258', '2026-11-19 18:25:37.959507', 3, 3),
(16, 'TestAdministrador', 'admin@test.cl', 'pbkdf2_sha256$600000$yCupPbOWkPuXwvCFqaaXyd$OsapjT93HFtbY6IMolh2Rq4p6jUzPfThdhi20cz4SUI=', 1, '2026-11-19 18:26:19.245036', '2026-11-19 18:26:20.459359', 3, 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_profile`
--

CREATE TABLE `user_profile` (
  `id` bigint(20) NOT NULL,
  `role` varchar(20) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `user_profile`
--

INSERT INTO `user_profile` (`id`, `role`, `user_id`) VALUES
(1, 'Administrador', 1),
(2, 'Administrador', 2),
(3, 'Administrador', 3),
(4, 'Administrador', 4),
(5, 'Administrador', 5),
(6, 'Administrador', 6),
(7, 'Dueño', 7),
(8, 'Contador', 8),
(9, 'Trabajador', 9),
(10, 'Dueño', 10),
(11, 'Contador', 11),
(12, 'Trabajador', 12),
(13, 'Administrador', 13);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `appweb_company`
--
ALTER TABLE `appweb_company`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `tax_id` (`tax_id`);

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
-- Indices de la tabla `cash_register_closure`
--
ALTER TABLE `cash_register_closure`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `date` (`date`),
  ADD KEY `cash_register_closure_closed_by_user_id_b3b3ec29_fk_user_id` (`closed_by_user_id`),
  ADD KEY `cash_register_closure_company_id_7ade5d93_fk_company_id` (`company_id`),
  ADD KEY `cash_register_closure_reviewed_by_user_id_53cb735c_fk_user_id` (`reviewed_by_user_id`);

--
-- Indices de la tabla `closure_method_detail`
--
ALTER TABLE `closure_method_detail`
  ADD PRIMARY KEY (`id`),
  ADD KEY `closure_method_detai_closure_id_e4c62ead_fk_cash_regi` (`closure_id`),
  ADD KEY `closure_method_detai_payment_method_id_61c5f8ff_fk_payment_m` (`payment_method_id`);

--
-- Indices de la tabla `company`
--
ALTER TABLE `company`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `tax_id` (`tax_id`);

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
-- Indices de la tabla `financial_ratio`
--
ALTER TABLE `financial_ratio`
  ADD PRIMARY KEY (`id`),
  ADD KEY `financial_ratio_company_id_9e76c423_fk_company_id` (`company_id`),
  ADD KEY `financial_ratio_upload_id_7c29b7c7_fk_financial_upload_id` (`upload_id`),
  ADD KEY `financial_ratio_validated_by_user_id_74f8c329_fk_user_id` (`validated_by_user_id`);

--
-- Indices de la tabla `financial_upload`
--
ALTER TABLE `financial_upload`
  ADD PRIMARY KEY (`id`),
  ADD KEY `financial_upload_company_id_de46dc82_fk_company_id` (`company_id`),
  ADD KEY `financial_upload_user_id_210331e9_fk_user_id` (`user_id`);

--
-- Indices de la tabla `payment_method`
--
ALTER TABLE `payment_method`
  ADD PRIMARY KEY (`id`),
  ADD KEY `payment_method_company_id_0e511cb9_fk_company_id` (`company_id`);

--
-- Indices de la tabla `pdf_report`
--
ALTER TABLE `pdf_report`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pdf_report_company_id_da07dd4b_fk_company_id` (`company_id`),
  ADD KEY `pdf_report_prediction_id_924b4a0e_fk_risk_prediction_id` (`prediction_id`),
  ADD KEY `pdf_report_user_id_f08cf5d9_fk_user_id` (`user_id`);

--
-- Indices de la tabla `petty_cash_withdrawal`
--
ALTER TABLE `petty_cash_withdrawal`
  ADD PRIMARY KEY (`id`),
  ADD KEY `petty_cash_withdrawa_closure_id_dab38c61_fk_cash_regi` (`closure_id`),
  ADD KEY `petty_cash_withdrawal_company_id_d26b4bcf_fk_company_id` (`company_id`),
  ADD KEY `petty_cash_withdrawal_user_id_57d15f4b_fk_user_id` (`user_id`);

--
-- Indices de la tabla `prediction_history`
--
ALTER TABLE `prediction_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `prediction_history_company_id_cb1c1d6b_fk_appweb_company_id` (`company_id`);

--
-- Indices de la tabla `recommendation`
--
ALTER TABLE `recommendation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `recommendation_prediction_id_97d3e707_fk_risk_prediction_id` (`prediction_id`);

--
-- Indices de la tabla `risk_prediction`
--
ALTER TABLE `risk_prediction`
  ADD PRIMARY KEY (`id`),
  ADD KEY `risk_prediction_company_id_a6790533_fk_company_id` (`company_id`),
  ADD KEY `risk_prediction_executed_by_user_id_27f5ab9b_fk_user_id` (`executed_by_user_id`),
  ADD KEY `risk_prediction_ratio_id_3b8731b6_fk_financial_ratio_id` (`ratio_id`);

--
-- Indices de la tabla `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `sale`
--
ALTER TABLE `sale`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sale_closure_id_874d0189_fk_cash_register_closure_id` (`closure_id`),
  ADD KEY `sale_company_id_2b389395_fk_company_id` (`company_id`),
  ADD KEY `sale_payment_method_id_1b6d6a66_fk_payment_method_id` (`payment_method_id`),
  ADD KEY `sale_user_id_ae07b266_fk_user_id` (`user_id`);

--
-- Indices de la tabla `upload_state`
--
ALTER TABLE `upload_state`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `user_company_id_99854d28_fk_company_id` (`company_id`),
  ADD KEY `user_role_id_c3a87a3d_fk_role_id` (`role_id`);

--
-- Indices de la tabla `user_profile`
--
ALTER TABLE `user_profile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `appweb_company`
--
ALTER TABLE `appweb_company`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

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
-- AUTO_INCREMENT de la tabla `cash_register_closure`
--
ALTER TABLE `cash_register_closure`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `closure_method_detail`
--
ALTER TABLE `closure_method_detail`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `company`
--
ALTER TABLE `company`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

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
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT de la tabla `financial_ratio`
--
ALTER TABLE `financial_ratio`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `financial_upload`
--
ALTER TABLE `financial_upload`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `payment_method`
--
ALTER TABLE `payment_method`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `pdf_report`
--
ALTER TABLE `pdf_report`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `petty_cash_withdrawal`
--
ALTER TABLE `petty_cash_withdrawal`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `prediction_history`
--
ALTER TABLE `prediction_history`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `recommendation`
--
ALTER TABLE `recommendation`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT de la tabla `risk_prediction`
--
ALTER TABLE `risk_prediction`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `role`
--
ALTER TABLE `role`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `sale`
--
ALTER TABLE `sale`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `upload_state`
--
ALTER TABLE `upload_state`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `user_profile`
--
ALTER TABLE `user_profile`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- Restricciones para tablas volcadas
--

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
-- Filtros para la tabla `cash_register_closure`
--
ALTER TABLE `cash_register_closure`
  ADD CONSTRAINT `cash_register_closure_closed_by_user_id_b3b3ec29_fk_user_id` FOREIGN KEY (`closed_by_user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `cash_register_closure_company_id_7ade5d93_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `cash_register_closure_reviewed_by_user_id_53cb735c_fk_user_id` FOREIGN KEY (`reviewed_by_user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `closure_method_detail`
--
ALTER TABLE `closure_method_detail`
  ADD CONSTRAINT `closure_method_detai_closure_id_e4c62ead_fk_cash_regi` FOREIGN KEY (`closure_id`) REFERENCES `cash_register_closure` (`id`),
  ADD CONSTRAINT `closure_method_detai_payment_method_id_61c5f8ff_fk_payment_m` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `financial_ratio`
--
ALTER TABLE `financial_ratio`
  ADD CONSTRAINT `financial_ratio_company_id_9e76c423_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `financial_ratio_upload_id_7c29b7c7_fk_financial_upload_id` FOREIGN KEY (`upload_id`) REFERENCES `financial_upload` (`id`),
  ADD CONSTRAINT `financial_ratio_validated_by_user_id_74f8c329_fk_user_id` FOREIGN KEY (`validated_by_user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `financial_upload`
--
ALTER TABLE `financial_upload`
  ADD CONSTRAINT `financial_upload_company_id_de46dc82_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `financial_upload_user_id_210331e9_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `payment_method`
--
ALTER TABLE `payment_method`
  ADD CONSTRAINT `payment_method_company_id_0e511cb9_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`);

--
-- Filtros para la tabla `pdf_report`
--
ALTER TABLE `pdf_report`
  ADD CONSTRAINT `pdf_report_company_id_da07dd4b_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `pdf_report_prediction_id_924b4a0e_fk_risk_prediction_id` FOREIGN KEY (`prediction_id`) REFERENCES `risk_prediction` (`id`),
  ADD CONSTRAINT `pdf_report_user_id_f08cf5d9_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `petty_cash_withdrawal`
--
ALTER TABLE `petty_cash_withdrawal`
  ADD CONSTRAINT `petty_cash_withdrawa_closure_id_dab38c61_fk_cash_regi` FOREIGN KEY (`closure_id`) REFERENCES `cash_register_closure` (`id`),
  ADD CONSTRAINT `petty_cash_withdrawal_company_id_d26b4bcf_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `petty_cash_withdrawal_user_id_57d15f4b_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `prediction_history`
--
ALTER TABLE `prediction_history`
  ADD CONSTRAINT `prediction_history_company_id_cb1c1d6b_fk_appweb_company_id` FOREIGN KEY (`company_id`) REFERENCES `appweb_company` (`id`);

--
-- Filtros para la tabla `recommendation`
--
ALTER TABLE `recommendation`
  ADD CONSTRAINT `recommendation_prediction_id_97d3e707_fk_risk_prediction_id` FOREIGN KEY (`prediction_id`) REFERENCES `risk_prediction` (`id`);

--
-- Filtros para la tabla `risk_prediction`
--
ALTER TABLE `risk_prediction`
  ADD CONSTRAINT `risk_prediction_company_id_a6790533_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `risk_prediction_executed_by_user_id_27f5ab9b_fk_user_id` FOREIGN KEY (`executed_by_user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `risk_prediction_ratio_id_3b8731b6_fk_financial_ratio_id` FOREIGN KEY (`ratio_id`) REFERENCES `financial_ratio` (`id`);

--
-- Filtros para la tabla `sale`
--
ALTER TABLE `sale`
  ADD CONSTRAINT `sale_closure_id_874d0189_fk_cash_register_closure_id` FOREIGN KEY (`closure_id`) REFERENCES `cash_register_closure` (`id`),
  ADD CONSTRAINT `sale_company_id_2b389395_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `sale_payment_method_id_1b6d6a66_fk_payment_method_id` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`),
  ADD CONSTRAINT `sale_user_id_ae07b266_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `user`
--
ALTER TABLE `user`
  ADD CONSTRAINT `user_company_id_99854d28_fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`),
  ADD CONSTRAINT `user_role_id_c3a87a3d_fk_role_id` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`);

--
-- Filtros para la tabla `user_profile`
--
ALTER TABLE `user_profile`
  ADD CONSTRAINT `user_profile_user_id_8fdce8e2_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
