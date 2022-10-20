-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Oct 20, 2022 at 06:27 AM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `chatapp`
--

-- --------------------------------------------------------

--
-- Table structure for table `friendship`
--

CREATE TABLE `friendship` (
  `id` int(11) NOT NULL,
  `accepted` tinyint(1) NOT NULL DEFAULT 0,
  `requestingUserId` int(11) DEFAULT NULL,
  `acceptingUserId` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT current_timestamp(),
  `updated_on` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `friendship`
--

INSERT INTO `friendship` (`id`, `accepted`, `requestingUserId`, `acceptingUserId`, `created_on`, `updated_on`) VALUES
(9, 1, 1, 2, '2022-10-03 18:16:08', '2022-10-03 17:32:00'),
(10, 0, 2, 1, '2022-10-03 18:16:39', '2022-10-03 18:16:39'),
(14, 1, 1, 3, '2022-10-04 18:33:58', '2022-10-04 17:34:07'),
(15, 0, 2, 3, '2022-10-04 19:14:39', '2022-10-04 19:14:39');

-- --------------------------------------------------------

--
-- Table structure for table `message`
--

CREATE TABLE `message` (
  `id` int(11) NOT NULL,
  `message` varchar(250) DEFAULT NULL,
  `senderId` int(11) NOT NULL,
  `receiverId` int(11) NOT NULL,
  `created_on` datetime DEFAULT current_timestamp(),
  `updated_on` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `message`
--

INSERT INTO `message` (`id`, `message`, `senderId`, `receiverId`, `created_on`, `updated_on`) VALUES
(1, 'hello Nick', 1, 2, '2022-10-04 04:44:49', '2022-10-04 04:44:49'),
(2, 'sup bro, how&#x27;s the family', 2, 1, '2022-10-04 04:44:58', '2022-10-04 04:44:58'),
(3, 'this is another test message', 1, 2, '2022-10-04 06:42:47', '2022-10-04 06:42:47'),
(4, 'Hi bro', 1, 3, '2022-10-04 18:34:25', '2022-10-04 18:34:25'),
(5, 'what&#x27;s up?', 3, 1, '2022-10-04 18:34:36', '2022-10-04 18:34:36'),
(6, 'Good bro, I just checked out your profile', 1, 3, '2022-10-04 18:34:51', '2022-10-04 18:34:51'),
(7, 'Looks good right?', 3, 1, '2022-10-04 18:34:58', '2022-10-04 18:34:58'),
(8, 'Yeah', 1, 3, '2022-10-04 18:35:02', '2022-10-04 18:35:02'),
(9, 'sup bro', 3, 1, '2022-10-04 18:47:59', '2022-10-04 18:47:59'),
(10, 'I am good', 1, 3, '2022-10-04 18:48:06', '2022-10-04 18:48:06');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(250) DEFAULT NULL,
  `session_id` varchar(200) DEFAULT NULL,
  `created_on` datetime DEFAULT current_timestamp(),
  `updated_on` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `password`, `session_id`, `created_on`, `updated_on`) VALUES
(1, 'Spiff Jekey-Green', 'spiffjekeygreen@gmail.com', '$2b$12$bZj0qvZ0MtATAilCghcE2uM/2DNjxzBlUVOWe4WnlXeOrryn9N0Iy', '', '2022-10-02 22:02:36', '2022-10-09 19:20:55'),
(2, 'Nicky Joe', 'nickyjoe@gmail.com', '$2b$12$iLtdG372.qQPUAQuhELdt.R8F3n73UTtV/0i/BmySL/sPys7nnApG', '', '2022-10-02 22:02:42', '2022-10-09 19:20:03'),
(3, 'Test 1', 'test@gmail.com', '$2b$12$YGD64441WlzBYWtUGFJSwe9BTzut/Vklq./Pg3/17J4ACTc4kJ7Xm', '', '2022-10-02 22:02:51', '2022-10-04 18:14:43');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `friendship`
--
ALTER TABLE `friendship`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`id`),
  ADD KEY `senderId` (`senderId`),
  ADD KEY `receiverId` (`receiverId`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `friendship`
--
ALTER TABLE `friendship`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `message`
--
ALTER TABLE `message`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `message_ibfk_1` FOREIGN KEY (`senderId`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `message_ibfk_2` FOREIGN KEY (`receiverId`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
