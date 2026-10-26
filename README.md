# ChessMatch

ChessMatch é uma aplicação web para organizar torneios de xadrez, gerenciar participantes e registrar partidas e resultados. O sistema acompanha a competição, desde a inscrição dos jogadores até a classificação por pontos.

## Funcionalidades

- Cadastro de contas, login por email e edição de perfil.
- Administração de usuários e permissões de acesso.
- Cadastro e gerenciamento de torneios e partidas.
- Inscrição de participantes e geração de rodadas pelo sistema suíço local.
- Pareamento por proximidade de pontuação, sem repetir adversários, com equilíbrio de cores e folgas quando necessário.
- Registro de vitórias e empates, cálculo de pontos e classificação com Buchholz simples.
- Dashboard com totais de usuários, torneios, partidas e resultados recentes.

O pareamento é uma implementação local do sistema suíço, sem equivalência ao sistema holandês completo da FIDE.

## Linguagens utilizadas

- **Python:** regras de negócio, autenticação, acesso aos dados e pareamento.
- **HTML:** estrutura das páginas e formulários.
- **CSS:** estilos e adaptação da interface para diferentes tamanhos de tela.
- **JavaScript:** confirmação de exclusões na interface.

## Tecnologias e integrações

- **Django:** framework responsável pelas rotas, modelos, formulários, templates, autenticação e sessões.
- **Bootstrap:** componentes e estilos da interface, carregados por CDN.
- **django-widget-tweaks:** aplicação de classes e atributos aos campos dos formulários nos templates.
- **NetworkX:** cálculo das combinações de jogadores para os pareamentos suíços.
- **SQLite:** banco de dados padrão para armazenamento local.
- **MySQL com PyMySQL:** opção de banco de dados por configuração, com suporte a caracteres utf8mb4.


## Publicar no Render

O arquivo `render.yaml` configura um serviço web e PostgreSQL com o plano gratuito.
O Render gera a chave secreta e conecta o banco sem gravar senhas no repositório.
Na sua conta do Render, escolha **New → Blueprint**, conecte este repositório e
confira os recursos e preços antes de criar. Selecione a branch que contém este arquivo.
Não selecione recursos pagos para esta demonstração.

O build instala as dependências e prepara o CSS. Ao iniciar, o serviço aplica as
migrações e executa o Gunicorn. O endereço do serviço aparece no painel do Render.
A primeira abertura pode demorar quando o serviço gratuito estiver suspenso.

O PostgreSQL gratuito tem prazo de expiração: confira a data no painel e exporte
os dados antes dela. Um banco novo começa vazio e exige atualizar DATABASE_URL.
Não reutilize SQLite no serviço gratuito para guardar cadastros permanentemente.

A página “Criar conta” permite cadastrar usuários. Para criar um administrador,
execute `python manage.py createsuperuser` em um terminal autorizado conectado ao
banco publicado, usando a conexão externa fornecida pelo Render em DATABASE_URL.
Não publique credenciais, nem use uma senha padrão no código. Não é necessário
administrador para verificar a página de login e o cadastro público.
