# Explicação: GatoService (adocato)

Este documento explica de maneira direta e passo-a-passo o papel do arquivo
`projadocato/adocato/services/gatoservice.py`, o que cada método faz e exatamente
como ele se conecta com outros arquivos do projeto (models, views, urls e templates).
O objetivo é ser claro e acessível — com foco em "quem chama quem".

---

## 1) Propósito geral do `GatoService`

- `GatoService` é uma camada de serviço (service layer) que centraliza a lógica
  relacionada ao modelo `Gato`.
- Ele deixa as *views* mais simples: as views apenas extraem dados do `request`
  e chamam métodos do `GatoService` em vez de manipular o ORM diretamente.
- Facilita testes, reutilização e manutenção.

Em termos práticos: se a aplicação precisa criar, atualizar, listar ou excluir
um gato, a chamada vai para o `GatoService`.

---

## 2) Métodos principais (resumo)

- `buscar_gatos(nome=None, disponivel=None)`
  - Retorna um queryset de `Gato` filtrado por nome parcial e/ou disponibilidade.
  - Usado pela view `gato_list` para exibir a lista de gatos.

- `listar_gatos_por_raca(raca_id)`
  - Retorna gatos cuja `raca.id == raca_id`.
  - Usado pela view `gato_list_por_raca`.

- `listar_gatos_disponiveis()`
  - Retorna apenas os gatos com `disponivel=True`.
  - Usado pela view `listar_gatos_disponiveis`.

- `obter_gato_por_id(gato_id)`
  - Retorna a instância `Gato` ou `None` (se não existir).
  - Usado por views que precisam carregar um gato para editar/excluir.

- `cadastrar_gato(...)`
  - Cria uma instância `Gato`, chama `full_clean()` (validação do model) e salva.
  - A view `gato_cadastrar` passa `request.POST`/`request.FILES` para este método.

- `atualizar_gato(...)`
  - Atualiza apenas os campos fornecidos (parcial), valida (`full_clean`) e salva.
  - Usado pela view `gato_editar`.

- `excluir_gato(gato_id)`
  - Deleta o registro e retorna `True`/`False` conforme o resultado.
  - Usado pela view `gato_excluir`.

---

## 3) Fluxo passo-a-passo (exemplo: cadastrar um gato)

1. O usuário abre o formulário em `/gatos/cadastrar/` (URL definida em
   `projadocato/adocato/urls.py`).
2. O navegador envia `POST` para a view `gato_cadastrar` (`projadocato/adocato/views.py`).
3. A view extrai os dados de `request.POST` e `request.FILES` (ex.: `foto`).
4. A view chama: `GatoService.cadastrar_gato(nome, sexo, cor, data_nascimento, raca_id, descricao, foto)`.
5. `GatoService` cria um objeto `Gato` (usa `Raca.objects.get(id=raca_id)` para a FK).
6. `GatoService` chama `gato.full_clean()` — isso executa as validações declaradas
   em `Gato.clean()` (veja `projadocato/adocato/models.py`).
7. Se tudo OK, `gato.save()` persiste no banco. Se `full_clean()` falhar, é levantado
   `ValidationError` e a view exibe mensagens de erro.
8. A view redireciona/mostra mensagem de sucesso (usa `GerenciadorMensagem` em utils).

Observação: `full_clean()` delega a lógica de validação ao modelo (`Gato.clean()`),
por isso é importante olhar `models.py` para entender regras como "nome mínimo"
ou "data de nascimento não pode ser no futuro".

---

## 4) Onde procurar os arquivos relevantes

- Modelos (schema + validações): `projadocato/adocato/models.py`  
  (contém `Gato`, `Raca`, `Adotante`, etc.)

- Serviços (aqui explicado): `projadocato/adocato/services/gatoservice.py`

- Views (camada HTTP que usa o serviço): `projadocato/adocato/views.py`

- URLs (mapeamento de rotas): `projadocato/adocato/urls.py`

- Templates (onde os dados aparecem): `projadocato/adocato/templates/adocato/gatos/`  
  - `lista.html` (espera `context['gatos']`)  
  - `form.html` (espera `context['racas']` e, quando editar, `context['gato']`)

---

## 5) "Quem chama quem" (lista literal e curta)

- `urls.py` -> mapeia URL -> chama `views.py` (ex.: `/gatos/` -> `gato_list`).
- `views.py` -> chama `GatoService` (ex.: `GatoService.buscar_gatos`) para obter/alterar dados.
- `GatoService` -> usa `models.Gato` e `models.Raca` para consultar/criar/atualizar.
- `GatoService` -> chama `full_clean()` que aplica regras em `Gato.clean()` (models).
- `views.py` -> passa o resultado (queryset ou instância) para o template.
- `templates` -> exibem os dados ao usuário.

---

## 6) Exemplo de chamada real (trecho da view)

```python
# em projadocato/adocato/views.py
# bloco simplificado
if request.method == 'POST':
    nome = request.POST.get('nome')
    foto = request.FILES.get('foto')
    try:
        GatoService.cadastrar_gato(nome, sexo, cor, data_nascimento, raca_id, descricao, foto)
        # sucesso -> redireciona
    except ValidationError as e:
        # a view transforma esse erro em mensagens para o template
```

---

## 7) Observações úteis / sugestões práticas

- `Raca.objects.get(id=raca_id)` pode lançar `Raca.DoesNotExist`. O `GatoService`
  atualmente deixa essa exceção propagar. A view espera `ValidationError` —
  seria melhor o serviço capturar `Raca.DoesNotExist` e lançar `ValidationError`
  com mensagem amigável.

- `foto` é um `ImageField`: a view deve enviar o arquivo (via `request.FILES`) e o
  Django cuidará do upload (ver `MEDIA_ROOT`/`MEDIA_URL` nas configurações).

- Ao inspecionar um problema, siga este caminho: URL -> view -> service -> model -> template.
  Isso torna mais simples localizar onde uma validação ou erro acontece.

- Para testar manualmente (local):
  1. Rodar servidor: `python manage.py runserver`
  2. Acessar `/gatos/` e `/gatos/cadastrar/` para verificar comportamento.
  3. Se houver erro de validação, a view pega `ValidationError` e exibe mensagens.

---

## 8) Quer que eu também:
- (A) Insira comentários inline diretamente no `gatoservice.py`?  
- (B) Abra um PR/commit com este arquivo `docs/ADOCATO_SERVICES.md` no repositório?  

Se quiser, já posso commitar este arquivo para você. Diga qual opção prefere.
