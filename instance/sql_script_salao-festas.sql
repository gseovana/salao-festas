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
    ON DELETE CASCADE
    ON UPDATE RESTRICT
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
    ON DELETE CASCADE
    ON UPDATE RESTRICT
);

CREATE TABLE IF NOT EXISTS `pagamento` (
  `id_pagto` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `forma_pagto` VARCHAR(45) NOT NULL,
  `qtd_parcelas` INT NOT NULL,
  `evento_data` DATE NOT NULL,
  `evento_horario` VARCHAR(45) NOT NULL,
  `valor` DECIMAL(10,2) NOT NULL,
  `data_pagto` DATE NOT NULL,
  FOREIGN KEY (`evento_data`, `evento_horario`)
    REFERENCES `evento` (`data`, `horario`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT
);

CREATE TABLE IF NOT EXISTS `mobilia` (
  `tipo_mobilia` VARCHAR(45) NOT NULL PRIMARY KEY,
  `quantidade` INT NOT NULL,
  `valor` DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS `cliente_aluga_mobilia` (
  `cliente_cpf` VARCHAR(11) NOT NULL,
  `tipo_mobilia` VARCHAR(45) NOT NULL,
  `qtd_alugada` INT NOT NULL,
  `valor` DECIMAL(10,2) NOT NULL,
  `data_aluguel` DATE NOT NULL,
  PRIMARY KEY (`cliente_cpf`, `tipo_mobilia`),
  FOREIGN KEY (`cliente_cpf`)
    REFERENCES `cliente` (`cpf`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  FOREIGN KEY (`tipo_mobilia`)
    REFERENCES `mobilia` (`tipo_mobilia`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `parceiro` (
  `id_parceiro` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `celular` VARCHAR(14) NOT NULL
);

-- Trigger para evitar conflitos de horários entre eventos e visitações
CREATE TRIGGER verifica_conflito_evento
BEFORE INSERT ON evento
FOR EACH ROW
BEGIN
  -- Verifica se existe uma visita agendada para o mesmo horário
  SELECT RAISE(ABORT, 'Horário indisponível.')
  WHERE EXISTS (SELECT 1 FROM visitacao WHERE data = NEW.data AND horario = NEW.horario);
END;

CREATE TRIGGER verifica_conflito_visita
BEFORE INSERT ON visitacao
FOR EACH ROW
BEGIN
  -- Verifica se existe um evento agendado para o mesmo horário
  SELECT RAISE(ABORT, 'Horário insdisponível.')
  WHERE EXISTS (SELECT 1 FROM evento WHERE data = NEW.data AND horario = NEW.horario);
END;

-- Trigger para evitar a criação de eventos no passado
CREATE TRIGGER evita_evento_no_passado
BEFORE INSERT ON evento
FOR EACH ROW
BEGIN
  -- Verifica se a data e o horário do novo evento são maiores ou iguais à data e hora atuais
  SELECT RAISE(ABORT, 'Não é possível agendar um evento no passado.')
  WHERE DATETIME(NEW.data || ' ' || NEW.horario) < DATETIME('now');
END;

-- Trigger para evitar a criação de visitas no passado
CREATE TRIGGER evita_visita_no_passado
BEFORE INSERT ON visitacao
FOR EACH ROW
BEGIN
  -- Verifica se a data e o horário da nova visita são maiores ou iguais à data e hora atuais
  SELECT RAISE(ABORT, 'Não é possível agendar uma visita no passado.')
  WHERE DATETIME(NEW.data || ' ' || NEW.horario) < DATETIME('now');
END;
