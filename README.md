# ChessMatch

Gerenciador de usuários, torneios e registros de partidas de xadrez em Django. Não inclui tabuleiro para jogar. A organização original de modelos, formulários, views e templates foi preservada.

## Instalação no Windows / PowerShell

Validado com Python 3.12.10 e Django 5.2.18 LTS. Django 4.2 encerrou suporte em abril de 2026. Recomenda-se manter o Python 3.12 atualizado com correções de segurança.

```powershell
cd C:\Users\Giovana\chess_web
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe manage.py migrate
.\.venv312\Scripts\python.exe manage.py createsuperuser
.\.venv312\Scripts\python.exe manage.py runserver
```

Se `.venv312` já existe, use-o diretamente. Não é necessário ativar o ambiente. Abra http://127.0.0.1:8000/ e entre com email e senha. O primeiro administrador deve ser criado interativamente com `createsuperuser`; nenhuma conta ou senha padrão é criada. Não compartilhe senhas no chat.

Contas existentes são preservadas. Se veio da instalação antiga que criava `root@ifmg.br`, troque sua senha conhecida antes de usar:

```powershell
.\.venv312\Scripts\python.exe manage.py changepassword root@ifmg.br
```

Administradores gerenciam usuários. Usuários comuns podem consultar e editar o próprio perfil e gerenciar torneios e partidas. Senha vazia na edição mantém a senha atual. Excluir torneio também exclui partidas vinculadas, conforme a relação original.

## Bancos e migrações

SQLite é padrão (`db.sqlite3`). Antes de migrar bancos existentes, faça backup consistente e confira emails acima de 254 caracteres; a migração 0013 interrompe a operação se houver algum, sem truncar dados. Corrija esses endereços conscientemente antes de repetir. Nunca apague o banco nem use `--fake` para contornar falhas.

As migrações históricas 0001 e 0005 foram ajustadas para permitir índices de email em MySQL utf8mb4; 0002 não cria mais conta com senha fixa; 0010 converte campos de perfil NULL para texto vazio com o modelo histórico e alias do banco. A nova 0013 aplica o limite de email em bancos existentes. Nenhuma conta antiga é removida por essas mudanças.

Para MySQL, crie um banco separado com utf8mb4, copie `mysql.template.cnf` para `mysql.cnf` e preencha as credenciais locais. Instale requirements e execute:

```powershell
$env:CHESS_DATABASE = 'mysql'
.\.venv312\Scripts\python.exe manage.py migrate
.\.venv312\Scripts\python.exe manage.py createsuperuser
.\.venv312\Scripts\python.exe manage.py runserver
```

PyMySQL é ativado somente nesse modo. Para voltar a SQLite, remova a variável (`Remove-Item Env:CHESS_DATABASE`). SQLite e MySQL são bancos independentes: trocar configuração não transfere dados. Para executar testes em MySQL, a conta deve ter permissão para criar e remover o banco de testes. Os testes usam um banco separado; nunca configure o nome do banco de testes para um banco com dados reais.

## Configuração

Variáveis opcionais: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`true`/`false`) e `DJANGO_ALLOWED_HOSTS` (hosts separados por vírgula). O arquivo `.env` não é carregado automaticamente; defina variáveis no PowerShell ou no ambiente. Configuração padrão é para desenvolvimento. Para produção, configure segredo próprio, DEBUG false, hosts, HTTPS, servidor de aplicação e arquivos estáticos antes de publicar. Bootstrap é carregado por CDN e requer internet para sua aparência completa.

## Validação

```powershell
.\.venv312\Scripts\python.exe manage.py check
.\.venv312\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv312\Scripts\python.exe manage.py test
```

Sete testes cobrem autenticação, perfil, senha e hash, permissões, cadastros, POST/CSRF e migração de perfil antigo com NULL, além de rejeição de emails longos.

A atualização local foi validada em SQLite. MySQL ainda requer validação em um servidor disponível; a compatibilidade do caminho configurado não substitui um teste real.

O backup anterior à atualização está em `backups/db-antes-atualizacao.sqlite3` e o diff das alterações locais anteriores em `backups/alteracoes-locais.patch`. Esses arquivos e credenciais não são versionados. Preserve o backup para recuperação; não o restaure sobre um banco em uso.

## Cadastro público

Na tela de entrada, qualquer visitante pode clicar em **Criar conta**, informar nome, email, senha e confirmação. O cadastro entra automaticamente no dashboard e sempre cria uma conta comum, sem privilégios administrativos. Cada pessoa pode editar o próprio perfil e gerenciar torneios e partidas.

O endereço 127.0.0.1 funciona somente no computador que executa o servidor. O cadastro público não publica o site na internet; acesso por outras máquinas exige configurar hospedagem ou rede.


## Sistema suíço local

Em **Torneios**, crie um torneio, configure o número de rodadas (padrão: 5) e clique em **Sistema suíço**. Selecione os usuários participantes e salve. A inscrição usa a identidade do usuário, não apenas o nome; pessoas com nomes iguais permanecem distintas. O número inicial segue a ordem de cadastro dos usuários, sem rating.

Escolha a data e clique em **Gerar próxima rodada**. Na primeira rodada, a metade superior da ordem inicial enfrenta a metade inferior, alternando a cor da metade superior por mesa. Nas seguintes, o gerador calcula uma combinação completa que minimiza a soma das diferenças de pontuação; depois prefere equilíbrio de cores e proximidade da ordem inicial. Não permite repetir adversário, ter diferença de cores maior que 2 ou jogar a mesma cor três vezes seguidas. Se não encontrar uma combinação completa compatível, não cria uma rodada parcial nem relaxa silenciosamente essas regras.

Registre cada resultado na página do torneio: brancas, pretas ou empate. Vitória vale 1, empate 0,5 e derrota 0. Quando houver número ímpar, a folga vale 1 ponto e não atribui cor nem adversário; busca-se o participante de menor pontuação e pior ordem inicial que ainda não teve folga e permita completar os pares. Cada pessoa só recebe uma folga.

A classificação ordena por pontos, Buchholz simples (soma dos pontos dos adversários reais), vitórias e número inicial. Folgas não acrescentam adversários virtuais ao Buchholz. Os números são parciais enquanto houver resultados pendentes. Esta é uma regra de desempate local, sem os ajustes oficiais para partidas não jogadas.

Todas as partidas da rodada precisam de resultado antes da próxima. Resultados podem ser corrigidos até gerar a rodada seguinte; depois ficam fechados, pois mudá-los invalidaria os pares já gerados. Inscrições e número de rodadas também fecham após o início. O número de rodadas efetivo fica limitado à configuração e a N−1 para N par, ou N para N ímpar. Partidas geradas são protegidas contra edição manual de adversários ou exclusão individual.

Os torneios com partidas manuais antigas não são convertidos automaticamente: crie outro torneio para começar no suíço. Isso evita tentar inferir identidades e resultados de dados antigos. O backup anterior à migração está em `backups/db-antes-suico.sqlite3`.

Esta implementação segue princípios básicos do suíço, mas **não implementa o sistema holandês FIDE completo** (incluindo todos os critérios de flutuação, rating, exceções e desempates oficiais), nem possui homologação. Para torneios oficiais, use software de pareamento aprovado e arbitragem adequada. Não há tratamento de abandono, WO ou entrada tardia nesta versão. Como nas demais telas, usuários autenticados podem organizar torneios e lançar resultados.

A dependência NetworkX resolve o emparelhamento de cardinalidade máxima e peso mínimo; o gerador exige que todos os participantes sem folga sejam emparelhados antes de gravar. Geração, inscrições e resultados usam transações e bloqueio por torneio. Um formulário de geração antigo é rejeitado para evitar rodadas duplicadas.


Referências consultadas: [princípios básicos do suíço — FIDE](https://doc.fide.com/docs/DOC/2025_3FC/CM3-202517.pdf), [sistema holandês FIDE vigente desde fevereiro de 2026](https://handbook.fide.com/chapter/C0403202602) e [emparelhamento de peso mínimo — NetworkX](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.matching.min_weight_matching.html).

Validação desta implementação: 18 testes automatizados passaram em SQLite, incluindo um torneio de 30 jogadores em 5 rodadas (75 confrontos distintos), 29 jogadores com folgas, pontuação e desempates, inscrições, resultados, bloqueios e CSRF. Trinta simulações adicionais de 30 jogadores e cinco rodadas com resultados pseudoaleatórios também encontraram pareamentos completos. Isso não constitui prova de equivalência ao sistema holandês nem garante conclusão para qualquer histórico possível; configurações sem combinação válida são bloqueadas sem criar partidas parciais. MySQL permanece sem validação local.
