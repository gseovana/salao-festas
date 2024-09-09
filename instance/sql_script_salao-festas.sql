CREATE TABLE IF NOT EXISTS `cliente` (
  `cpf` VARCHAR(11) NOT NULL,
  `nome_cliente` VARCHAR(100) NOT NULL,
  `celular` VARCHAR(14) NOT NULL,
  `endereco` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`cpf`)
);

CREATE TABLE IF NOT EXISTS `visitacao` (
  `data` DATE NOT NULL,
  `horario` VARCHAR(45) NOT NULL,
  `cliente_cpf` VARCHAR(11) NOT NULL,
  PRIMARY KEY (`data`, `horario`, `cliente_cpf`),
  FOREIGN KEY (`cliente_cpf`)
    REFERENCES `cliente` (`cpf`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `evento` (
  `data` DATE NOT NULL,
  `horario` VARCHAR(45) NOT NULL,
  `nome_evento` VARCHAR(50) NOT NULL,
  `tipo` VARCHAR(45) NOT NULL,
  `cliente_cpf` VARCHAR(11) NOT NULL,
  PRIMARY KEY (`data`, `horario`),
  FOREIGN KEY (`cliente_cpf`)
    REFERENCES `cliente` (`cpf`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `pagamento` (
  `id_pagto` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `forma_pagto` VARCHAR(45) NOT NULL,
  `qtd_parcelas` INT NOT NULL,
  `evento_data` DATE NOT NULL,
  `evento_horario` VARCHAR(45) NOT NULL,
  FOREIGN KEY (`evento_data`, `evento_horario`)
    REFERENCES `evento` (`data`, `horario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `kit_mobilia` (
  `id_mobilia` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `quantidade` INT NOT NULL
);

CREATE TABLE IF NOT EXISTS `cliente_aluga_mobilia` (
  `cliente_cpf` VARCHAR(11) NOT NULL,
  `kit_mobilia_id_mobilia` INTEGER NOT NULL,
  `qtd_alugada` INT NOT NULL,
  PRIMARY KEY (`cliente_cpf`, `kit_mobilia_id_mobilia`),
  FOREIGN KEY (`cliente_cpf`)
    REFERENCES `cliente` (`cpf`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  FOREIGN KEY (`kit_mobilia_id_mobilia`)
    REFERENCES `kit_mobilia` (`id_mobilia`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `parceiro` (
  `id_parceiro` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `celular` VARCHAR(14) NOT NULL
);
