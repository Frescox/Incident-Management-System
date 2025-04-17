-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 17-04-2025 a las 01:18:39
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
-- Base de datos: `sistema_incidencias`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id`, `nombre`, `descripcion`, `created_at`, `updated_at`) VALUES
(1, 'Hardware', 'Problemas con equipos físicos', '2025-04-16 18:51:56', '2025-04-16 18:51:56'),
(2, 'Software', 'Problemas con aplicaciones y programas', '2025-04-16 18:51:56', '2025-04-16 18:51:56'),
(3, 'Redes', 'Problemas de conectividad y red', '2025-04-16 18:51:56', '2025-04-16 18:51:56'),
(4, 'Correo', 'Problemas con el correo electrónico', '2025-04-16 18:51:56', '2025-04-16 18:51:56');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categoria_agente`
--

CREATE TABLE `categoria_agente` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `categoria_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comentarios`
--

CREATE TABLE `comentarios` (
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `id` int(11) NOT NULL,
  `incidencia_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `contenido` text NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estados`
--

CREATE TABLE `estados` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estados`
--

INSERT INTO `estados` (`id`, `nombre`, `descripcion`, `created_at`, `updated_at`) VALUES
(1, 'nuevo', 'Incidencia recién creada', '2025-04-14 07:22:14', '2025-04-14 07:22:14'),
(2, 'en_progreso', 'Incidencia siendo atendida', '2025-04-14 07:22:14', '2025-04-14 07:22:14'),
(3, 'resuelto', 'Incidencia resuelta', '2025-04-14 07:22:14', '2025-04-14 07:22:14'),
(4, 'cerrado', 'Incidencia cerrada', '2025-04-14 07:22:14', '2025-04-14 07:22:14');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_estados`
--

CREATE TABLE `historial_estados` (
  `id` int(11) NOT NULL,
  `incidencia_id` int(11) NOT NULL,
  `estado_anterior_id` int(11) NOT NULL,
  `estado_nuevo_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `comentario` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `fecha_cambio` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `incidencias`
--

CREATE TABLE `incidencias` (
  `id` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text NOT NULL,
  `categoria_id` int(11) NOT NULL,
  `prioridad_id` int(11) NOT NULL,
  `estado_id` int(11) NOT NULL,
  `usuario_creador_id` int(11) NOT NULL,
  `agente_asignado_id` int(11) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  `fecha_ultima_actualizacion` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `fecha_resolucion` datetime DEFAULT NULL,
  `fecha_cierre` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `incidencias`
--

INSERT INTO `incidencias` (`id`, `titulo`, `descripcion`, `categoria_id`, `prioridad_id`, `estado_id`, `usuario_creador_id`, `agente_asignado_id`, `fecha_creacion`, `fecha_ultima_actualizacion`, `fecha_resolucion`, `fecha_cierre`, `created_at`, `updated_at`) VALUES
(1, 'Problema con el teclado', 'El teclado de mi computadora no responde correctamente. Algunas teclas no funcionan y otras escriben caracteres incorrectos.', 1, 2, 2, 100, 101, '2025-04-16 10:30:00', '2025-04-16 14:45:00', NULL, NULL, '2025-04-16 20:00:57', '2025-04-16 20:00:57'),
(2, 'Problema con el teclado', 'El teclado de mi computadora no responde correctamente. Algunas teclas no funcionan y otras escriben caracteres incorrectos.', 1, 2, 2, 100, 101, '2025-04-15 13:04:36', '2025-04-16 13:04:36', NULL, NULL, '2025-04-15 20:04:36', '2025-04-16 20:04:36'),
(3, 'Problema con el teclado', 'El teclado de mi computadora no responde correctamente. Algunas teclas no funcionan y otras escriben caracteres incorrectos.', 1, 2, 2, 100, 101, '2025-04-15 13:05:40', '2025-04-16 13:05:40', NULL, NULL, '2025-04-15 20:05:40', '2025-04-16 20:05:40'),
(4, 'Problema con el teclado', 'El teclado de mi computadora no responde correctamente. Algunas teclas no funcionan y otras escriben caracteres incorrectos.', 1, 2, 2, 100, 101, '2025-04-15 13:05:50', '2025-04-16 13:05:50', NULL, NULL, '2025-04-15 20:05:50', '2025-04-16 20:05:50'),
(5, 'Problema MacBook', 'Disco ssd', 1, 1, 1, 48, NULL, '2025-04-16 21:02:34', '2025-04-16 21:02:34', NULL, NULL, '2025-04-16 21:02:34', '2025-04-16 21:02:34'),
(6, 'Problema Monitor Asus', 'Pantalla Rota y Puertos', 3, 2, 1, 48, NULL, '2025-04-16 21:48:18', '2025-04-16 21:48:48', NULL, NULL, '2025-04-16 21:48:18', '2025-04-16 21:48:48');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `log_actividad`
--

CREATE TABLE `log_actividad` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `accion` varchar(255) NOT NULL,
  `entidad` varchar(50) DEFAULT NULL,
  `entidad_id` int(11) DEFAULT NULL,
  `detalles` text DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `log_actividad`
--

INSERT INTO `log_actividad` (`id`, `usuario_id`, `accion`, `entidad`, `entidad_id`, `detalles`, `user_agent`, `created_at`) VALUES
(1, 101, 'Actualización de incidencia', 'incidencias', 4, 'El agente ha tomado la incidencia y cambiado su estado', NULL, '2025-04-15 21:05:51');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `mensaje` text NOT NULL,
  `leida` tinyint(1) DEFAULT 0,
  `enlace` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `notificaciones`
--

INSERT INTO `notificaciones` (`id`, `usuario_id`, `titulo`, `mensaje`, `leida`, `enlace`, `created_at`, `updated_at`) VALUES
(1, 100, 'Su incidencia ha sido actualizada', 'El estado de su incidencia #4 ha cambiado a \"En progreso\"', 0, '/incidencias/4', '2025-04-15 21:05:50', '2025-04-15 21:05:50');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prioridades`
--

CREATE TABLE `prioridades` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `prioridades`
--

INSERT INTO `prioridades` (`id`, `nombre`, `descripcion`, `created_at`, `updated_at`) VALUES
(1, 'alta', 'Atención inmediata requerida', '2025-04-14 07:22:14', '2025-04-14 07:22:14'),
(2, 'media', 'Atención normal', '2025-04-14 07:22:14', '2025-04-14 07:22:14'),
(3, 'baja', 'Atención cuando sea posible', '2025-04-14 07:22:14', '2025-04-14 07:22:14');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id`, `nombre`, `descripcion`, `created_at`, `updated_at`) VALUES
(1, 'administrador', 'Control total del sistema', '2025-04-14 07:22:14', '2025-04-14 07:22:14'),
(2, 'agente', 'Gestión de incidencias asignadas', '2025-04-14 07:22:14', '2025-04-14 07:22:14'),
(3, 'usuario', 'Creación y seguimiento de incidencias propias', '2025-04-14 07:22:14', '2025-04-14 07:22:14');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sesiones`
--

CREATE TABLE `sesiones` (
  `id` varchar(128) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `payload` text NOT NULL,
  `last_activity` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol_id` int(11) NOT NULL,
  `estado` tinyint(1) DEFAULT 1,
  `telefono` varchar(100) DEFAULT NULL,
  `metodo_verificacion` enum('email','sms') DEFAULT NULL,
  `otp` varchar(6) DEFAULT NULL,
  `otp_expira` int(11) DEFAULT NULL,
  `verificado` tinyint(1) DEFAULT 0,
  `ultimo_login` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `apellido`, `email`, `password`, `rol_id`, `estado`, `telefono`, `metodo_verificacion`, `otp`, `otp_expira`, `verificado`, `ultimo_login`, `created_at`, `updated_at`) VALUES
(1, 'encrypted_nombre', 'encrypted_apellido', 'encrypted_email@test.com', 'encrypted_password', 3, 1, NULL, NULL, NULL, NULL, 1, NULL, '2025-04-16 19:58:59', '2025-04-16 19:58:59'),
(2, 'encrypted_agente', 'encrypted_apente_apellido', 'encrypted_agente@test.com', 'encrypted_password', 2, 1, NULL, NULL, NULL, NULL, 1, NULL, '2025-04-16 19:58:59', '2025-04-16 19:58:59'),
(48, 'M5BDBy88NXCJqLXAP+ML2oHWYH8QQhARVapat4eLEGQ=', 'hy1Xkx++WIqtNAUGhwgLzoZLwIO4N9AtM9E9fg6DEJU=', 'Weiq2n5rJx7m1c5+yvawfGpK6S//AoHAUEbrggLu5dY7ai4fxU/aPGAxciduNai/', 'r8LEF8KMy3Z4KWHT/hlp0MelGnSUgS1wlH2TAkoA8p4=', 3, 1, NULL, 'email', NULL, NULL, 1, '2025-04-16 16:14:03', '2025-04-16 16:57:23', '2025-04-16 23:14:03'),
(100, 'encrypted_nombre', 'encrypted_apellido', 'usuario_prueba@test.com', 'encrypted_password', 3, 1, NULL, NULL, NULL, NULL, 1, NULL, '2025-04-16 20:00:57', '2025-04-16 20:00:57'),
(101, 'encrypted_agente', 'encrypted_apellido', 'agente_prueba@test.com', 'encrypted_password', 2, 1, NULL, NULL, NULL, NULL, 1, NULL, '2025-04-16 20:00:57', '2025-04-16 20:00:57'),
(102, 'pqLTjOaBh/E+rh8RjDP7ighk00pJCLjus33hWDTNAjo=', '71FMYQ6Y/JkgnqNVsWLCCs3+DzROJj89FybdAax4GtA=', 'jAnJR5+AqvNlZyLs4LiFHqzHK5dGD9avUxtl/TW/bXoSQ/yKvvD7MqNeRzd8E+WX', 'y7flI3En3blHUaWqR2wCx4GgebQGbuoDONwv+MX1Fs8=', 3, 1, NULL, 'email', '841759', 1744844922, 0, NULL, '2025-04-16 22:53:42', '2025-04-16 22:53:43');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `categoria_agente`
--
ALTER TABLE `categoria_agente`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `comentarios`
--
ALTER TABLE `comentarios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `incidencia_id` (`incidencia_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `estados`
--
ALTER TABLE `estados`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `historial_estados`
--
ALTER TABLE `historial_estados`
  ADD PRIMARY KEY (`id`),
  ADD KEY `estado_anterior_id` (`estado_anterior_id`),
  ADD KEY `estado_nuevo_id` (`estado_nuevo_id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `idx_historial_incidencia` (`incidencia_id`);

--
-- Indices de la tabla `incidencias`
--
ALTER TABLE `incidencias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_incidencias_estado` (`estado_id`),
  ADD KEY `idx_incidencias_categoria` (`categoria_id`),
  ADD KEY `idx_incidencias_prioridad` (`prioridad_id`),
  ADD KEY `idx_incidencias_agente` (`agente_asignado_id`),
  ADD KEY `idx_incidencias_creador` (`usuario_creador_id`);

--
-- Indices de la tabla `log_actividad`
--
ALTER TABLE `log_actividad`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_log_actividad_usuario` (`usuario_id`),
  ADD KEY `idx_log_actividad_accion` (`accion`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `prioridades`
--
ALTER TABLE `prioridades`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `sesiones`
--
ALTER TABLE `sesiones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `rol_id` (`rol_id`),
  ADD KEY `idx_usuarios_email` (`email`),
  ADD KEY `idx_usuarios_verificado` (`verificado`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `categoria_agente`
--
ALTER TABLE `categoria_agente`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `comentarios`
--
ALTER TABLE `comentarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estados`
--
ALTER TABLE `estados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `historial_estados`
--
ALTER TABLE `historial_estados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `incidencias`
--
ALTER TABLE `incidencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `log_actividad`
--
ALTER TABLE `log_actividad`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `prioridades`
--
ALTER TABLE `prioridades`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=103;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `categoria_agente`
--
ALTER TABLE `categoria_agente`
  ADD CONSTRAINT `categoria_agente_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `categoria_agente_ibfk_2` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`);

--
-- Filtros para la tabla `comentarios`
--
ALTER TABLE `comentarios`
  ADD CONSTRAINT `comentarios_ibfk_1` FOREIGN KEY (`incidencia_id`) REFERENCES `incidencias` (`id`),
  ADD CONSTRAINT `comentarios_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `historial_estados`
--
ALTER TABLE `historial_estados`
  ADD CONSTRAINT `historial_estados_ibfk_1` FOREIGN KEY (`incidencia_id`) REFERENCES `incidencias` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `historial_estados_ibfk_2` FOREIGN KEY (`estado_anterior_id`) REFERENCES `estados` (`id`),
  ADD CONSTRAINT `historial_estados_ibfk_3` FOREIGN KEY (`estado_nuevo_id`) REFERENCES `estados` (`id`),
  ADD CONSTRAINT `historial_estados_ibfk_4` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `incidencias`
--
ALTER TABLE `incidencias`
  ADD CONSTRAINT `incidencias_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`),
  ADD CONSTRAINT `incidencias_ibfk_2` FOREIGN KEY (`prioridad_id`) REFERENCES `prioridades` (`id`),
  ADD CONSTRAINT `incidencias_ibfk_3` FOREIGN KEY (`estado_id`) REFERENCES `estados` (`id`),
  ADD CONSTRAINT `incidencias_ibfk_4` FOREIGN KEY (`usuario_creador_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `incidencias_ibfk_5` FOREIGN KEY (`agente_asignado_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `log_actividad`
--
ALTER TABLE `log_actividad`
  ADD CONSTRAINT `log_actividad_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `sesiones`
--
ALTER TABLE `sesiones`
  ADD CONSTRAINT `sesiones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
