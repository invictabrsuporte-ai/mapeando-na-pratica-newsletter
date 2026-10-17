# Operação semanal da newsletter

| Quando (BRT) | O que acontece | Quem |
|---|---|---|
| Dom 19:00 | GitHub Actions coleta vagas (Gupy, Vagas.com, LinkedIn) e grava `vagas.json` | automático |
| Dom 20:00 | Rotina monta a edição (notícias de seg a dom em `Invicta-OS/Content/pesquisa`, vagas, JSON, HTML) e envia a PRÉVIA só ao Alan | automático |
| Dom noite / Seg | Alan revisa a prévia, pede ajustes e diz "aprovado" | Alan |
| Ter 07:00 | Rotina de envio confere `aprovacao/edicao-NN.aprovada` e envia aos inscritos em lotes BCC | automático |

Regras
- Sem `aprovacao/edicao-NN.aprovada`, nada vai aos inscritos (o Alan recebe um aviso).
- Com `aprovacao/edicao-NN.enviada`, a edição nunca é reenviada.
- Data da edição = a terça-feira de envio. Rodar a montagem de novo na mesma semana reaproveita o mesmo número e sobrescreve os arquivos.
- Notícias só entram se a fonte primária foi aberta e conferida; o que não foi conferido vai para PENDÊNCIAS.
- Vagas: nunca inventadas; se a coleta falhar, a edição sai sem a seção e avisa.
- Python 3.12 (os geradores também rodam no 3.11).
