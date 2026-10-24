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
