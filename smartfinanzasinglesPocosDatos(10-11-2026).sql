-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 10-11-2026 a las 20:27:27
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
-- Base de datos: `smartfinanzasingles`
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
(5, '', '2026-11-10 19:26:55.618722', 0, 'test1', '', '', 'test1@test.cl', 0, 1, '2026-11-04 18:55:48.391435'),
(6, '', '2026-11-10 19:27:10.852685', 0, 'coagra', '', '', 'coagra@test.cl', 0, 1, '2026-11-09 20:23:40.769559');

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
('gyovp14nsl81l0ft2i4tyj9p62y72ehl', '.eJxVjMsOgjAQRf9l1oQU-hJ2uvcbyLQdoApt0tKV8d8NhmhY3ntOzgtKLph8HLyD_lL9ZoirSQQ92IhTQviTFBfo4epWH3zeErqYoIIByzYPJVP6lkCdP4P2SWEH7oFhirWNYUve1LtSHzTX9-houR3uKTBjnqEH0XHHW0WcrCWJnWyFZUw4PiouCVUjtWGmsYwaOWptlRCoZCNJKm0YOnh_AF0fUOQ:1xQVu0:CHQsPFek9chiTejXnpaoxf61FE1JNubb1SIBKPRhhsk', '2026-11-23 20:23:40.966017'),
('isde4qtdw4t0krthdsjvct8gmo3feixc', '.eJxVjMsOgjAQRf9l1oQU-hJ2uvcbyLQdoApt0tKV8d8NhmhY3ntOzgtKLph8HLyD_lL9ZoirSQQ92IhTQviTFBfo4epWH3zeErqYoIIByzYPJVP6lkCdP4P2SWEH7oFhirWNYUve1LtSHzTX9-houR3uKTBjnqEH0XHHW0WcrCWJnWyFZUw4PiouCVUjtWGmsYwaOWptlRCoZCNJKm0YOnh_AF0fUOQ:1xQrUs:cEHOOzADeXf5Q7qvqbdesmwaCZ95R2PuiUgaW16NaJI', '2026-11-24 19:27:10.898517');

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
(1, NULL, '2026-11-04 01:31:32.114471');

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
(7, 'test1', 'test1@test.cl', 'pbkdf2_sha256$600000$kIudPsIDeg9akKAxQhLMPS$La+HJop9usfYk2SXnQxMRSF5vKPdRs82WJKvQldWW40=', 1, '2026-11-04 18:55:47.053246', '2026-11-10 19:26:55.500017', 2, 4),
(8, 'coagra', 'coagra@test.cl', 'pbkdf2_sha256$600000$CPz1g3yNgoMOoDikyXrQD8$0yLgC5e1y1na2vq6qGPIvPAsX3OG7vKCxvQB20mKx+g=', 1, '2026-11-09 20:23:40.025729', '2026-11-10 19:27:10.711427', 3, 4);

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
(6, 'Administrador', 6);

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

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
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `closure_method_detail`
--
ALTER TABLE `closure_method_detail`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

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
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `financial_upload`
--
ALTER TABLE `financial_upload`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

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
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `risk_prediction`
--
ALTER TABLE `risk_prediction`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `role`
--
ALTER TABLE `role`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `sale`
--
ALTER TABLE `sale`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `upload_state`
--
ALTER TABLE `upload_state`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `user_profile`
--
ALTER TABLE `user_profile`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

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
