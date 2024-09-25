# Salão de festas Lutilê
## Escopo do sistema
### Contexto (mini mundo)
O Salão de Festas Lutilê é um estabelecimento localizado em João Monlevade e sede seu espaço para a realização de eventos em geral como casamentos, festas infantis, entre outros. O cliente interessado em alugar o salão, caso queira, pode entrar em contato com os donos para agendar uma visita até o local e conhecer o ambiente. Após visitá-lo, ele poderá agendar a data de seu evento e caso a disponibilidade esteja comprometida neste dia, o cliente deverá escolher outro dia e horário que não esteja ocupado, seguindo o cronograma de agendamentos. O registro e controle de pagamentos é feito manualmente e traz inúmeros problemas, já que os donos permitem o parcelamento do valor em até 3 vezes. O aluguel do espaço já inclui uma quantidade mínima de mesas e cadeiras. Caso o cliente queira/precise alugar mais mobília, o salão dispõe de “kits de mobília” (uma mesa e quatro cadeiras) que estão disponíveis para uso, porém é cobrado um valor a mais pelo aluguel dos kits, proporcional à quantidade de kits alugada. O cliente também recebe uma lista de indicações de empresas parceiras prestadoras de outros serviços como decoração, buffet, utensílios e mobiliários extras. O controle de disponibilidade do salão é feito de forma manual, na qual o locatário tem uma agenda com os dias disponíveis e reservados para a locação. Algumas informações estatísticas são importantes para os responsáveis do salão, como por exemplo os meses com mais eventos e a situação do pagamentos.

Protótipo do projeto: [Figma](https://www.figma.com/design/3fbXBYaMHcIvfDEajtjQVN/Sal%C3%A3o-de-Festas-Lutil%C3%AA?node-id=1-2&node-type=frame&t=z4tsD4EOVi3sIRS4-0) 

![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

### Objetivo
O objetivo geral do software proposto é auxiliar os proprietários do salão no processo de agendamento de visitas, locação e pagamentos. Atualmente esses processos trazem desafios aos donos na gestão do estabelecimento, já que ocorrem inteiramente de forma manual.

### Diagramas de classe e de atividades
Os diagramas podem ser visualizados de duas formas, a primeira forma é no final do readme onde vai estar localizado as imagens dos diagramas de classe e os diaggramas de atividades, e a segunda forma é acessando a pasta "Diagramas" localizada na raiz do projeto.

### Funcionalidades
As funcionalidades do sistema incluem:
- Login
- Manter agendamento de visita
- Manter evento
- Manter cliente
- Manter pagamento
- Manter empresa parceira
- Gerar relatórios
- Consultar calendário de eventos

## Membros da equipe e papel
Andre Luis Magalhaes Santos **(BD | Back-end)**<br/> 
Geovana Silva de Oliveira **(Full-stack | BD)**<br/> 
Jessica de Sousa Costa **(Front-end | UI/UX)**<br/> 
Nicolas de Oliveira Gomes **(Front-end)**<br/> 
Pablo Goncalves Barbosa **(Full-stack | BD)**<br/> 
Vinicius Andrade Costa **(Front-end)**<br/> 

## Tecnologias utilizadas
**Back-end:** Python e Flask<br/>
**Front-end:** HTML e CSS<br/>
**Banco de dados:** SQLite<br/>

## Backlog do produto
1. Como usuário cliente, gostaria de me cadastrar, atualizar meus dados, vê-los e deletar minha conta. 
2. Como usuário cliente, gostaria de criar, ler, atualizar e deletar meus agendamentos de visita.
3. Como usuário cliente, gostaria de ver o calendário de agendamento de visitas com as datas disponíveis.
4. Como usuário administrador, gostaria de alterar e deletar qualquer agendamento de visita.
5. Como usuário administrador, gostaria de criar, ler, atualizar e deletar eventos.
6. Como usuário administrador, gostaria de criar, ler, atualizar e deletar pagamentos.
7. Como usuário administrador, gostaria de criar, ler, atualizar e deletar "kits mobília".
8. Como usuário administrador, gostaria de criar, ler, atualizar e deletar empresas parceiras.
9. Como usuário administrador, gostaria de gerar relatório dos eventos.
10. Como usuário administrador, gostaria de gerar relatório de pagamentos.

## Backlog da Sprint
#### História 1: Como usuário cliente, gostaria de me cadastrar, atualizar meus dados, vê-los e deletar minha conta.
- Configurar ambientes e instalar bibliotecas
- Instalar banco de dados e criar as tabelas
- Testas as rotas da página inicial e de clientes
- Criar primeira versão tela principal
- Criar tela de cadastro de cliente
- Criar telas de CRUD cliente 
- Implementar lógica do backend
- Integrar as telas com a lógica do backend
- Integrar com banco de dados
  
#### História 2: Como usuário cliente, gostaria de criar, ler, atualizar e deletar meus agendamentos de visita.
- Criar rotas de login e de agendamentos de visita
- Criar tela de login
- Implementar lógica no backend para logar no sistema
- Integrar a tela de login com a lógica implementada no backend
- Adaptar tela inicial para as views de cliente e administrador
- Criar rotas de agendamento de visita
- Criar telas de CRUD de agendamentos de visita
- Implementar lógica de CRUD de agendamentos de visita no backend
- Integrar as telas de CRUD com a lógica do backend
- Integrar com o banco de dados
  
#### História 3: Como usuário cliente, gostaria de ver o calendário de agendamento de visitas com as datas disponíveis.
- Criar tela de calendário
- Implementar lógica para indicar dias disponíveis no backend
- Integrar a tela com a lógica do backend
- Integrar com o banco de dados

#### História 4: Como usuário administrador, gostaria de alterar e deletar qualquer agendamento de visita.
- Criar tela de adiministrar agendamentos de visita
- Implementar lógica para vsiualiar, alterar e deletar agendamentos de visita no backend
- Integrar a tela com a lógica do backend
- Integrar com o banco de dados
  
#### História 5: Como usuário administrador, gostaria de criar, ler, atualizar e deletar eventos.
- Criar telas de CRUD de evento
- Implementar lógicas de CRUD de evento no backend
- Integrar as telas de CRUD com a lógica do backend
- Integrar com o banco de dados
  
#### História 6: Como usuário administrador, gostaria de criar, ler, atualizar e deletar pagamentos.
#### História 7: Como usuário administrador, gostaria de criar, ler, atualizar e deletar "kits mobília".
#### História 8: Como usuário administrador, gostaria de criar, ler, atualizar e deletar parceiros.
#### História 9: Como usuário administrador, gostaria de gerar relatório dos eventos. 
#### História 10: Como usuário administrador, gostaria de gerar relatório de pagamentos.



## Diagramas de Atividade
![AgendarVisita](https://github.com/user-attachments/assets/78e8f1a8-af8a-49ad-aa7d-aaa4f1f70839)
![AlterarAgendamentoAdm](https://github.com/user-attachments/assets/203e2988-144a-4cb5-9bba-51d38d90f143)
![AtualizarAgendamento](https://github.com/user-attachments/assets/072e0e13-018c-44ce-ac87-781afc6911e3)
![AtualizarDadosCliente](https://github.com/user-attachments/assets/9cc4ffaa-246e-408c-942e-4db7a56d29a1)
![AtualizarKitMobília](https://github.com/user-attachments/assets/04769a5d-7c2d-4153-9b9c-55ffe395d22c)
![AtualizarPagamento](https://github.com/user-attachments/assets/a8297534-207f-4da8-8b7e-7f829b178901)
![AtualizarParceiros](https://github.com/user-attachments/assets/ca856112-a744-4b98-8c33-4636dca66441)
![Cadastro](https://github.com/user-attachments/assets/4e2dcb65-ae10-4cb4-bdf4-6e388ba48dab)
![CriarEvento](https://github.com/user-attachments/assets/0091693a-fc4d-428c-b229-6a95a13f9b39)
![DeletarAgendamento](https://github.com/user-attachments/assets/73a7728b-f4f8-4eb7-9b9d-070fed4f05c8)
![DeletarAgendamentoAdm](https://github.com/user-attachments/assets/b9bfa5ce-c1fb-4f32-8754-47d6a95323d2)
![DeletarEvento](https://github.com/user-attachments/assets/f4c7a1f7-be95-4561-8910-e7e55d3d638c)
![DeletarKitMobília](https://github.com/user-attachments/assets/ead5b137-e3e0-4f88-9c12-b0fce1ddb2c8)
![DeletarPagamento](https://github.com/user-attachments/assets/97d1d6c0-f444-44a2-becb-780ebc5a9c66)
![DeletarParceiros](https://github.com/user-attachments/assets/ee77c1d1-3644-4a38-b774-8ed52a7ecfa6)
![KitMobília](https://github.com/user-attachments/assets/750bffe2-ac36-4af8-a6ad-104a204bf989)
![Login](https://github.com/user-attachments/assets/8d3d4f12-a3ae-471f-ae41-7fc7a553abcd)
![Pagamento](https://github.com/user-attachments/assets/8641d899-94f2-4579-943c-34512a14fc68)
![Parceiros](https://github.com/user-attachments/assets/bd13a48f-458d-4508-908c-4f506a5f95e4)
![RelatorioEvento](https://github.com/user-attachments/assets/76d581cc-b0d7-403e-8c28-a69a200bfe16)
![RelatórioPagamento](https://github.com/user-attachments/assets/ab1a36c2-00db-4101-9280-567b159bd25d)















