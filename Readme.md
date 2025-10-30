# 🧩 Gerador de Pacotes — HTML Soul

Gerador de pacotes automatizado desenvolvido em **Python**, criado para facilitar e padronizar a geração de pacotes da **versão HTML Soul**.
Feito para uso interno da equipe de desenvolvimento.

Agora também disponível em **versão executável (.exe)** — não é necessário ter Python instalado para rodar.

---

## 💡 Como usar

### Usando o executável (.exe)

1. Baixe a versão mais recente na aba de [**Releases**](../../releases/latest).
2. Execute o arquivo .exe:

> 💡 Dica: Ao tentar executar o windows alerta de que a fonte do exe é desconhecida, até porque não sou famoso, só confia 👍.

---

## 🔄 Atualizações

Para garantir que esteja sempre na versão mais recente, utilize a **tag `latest`** disponível nas [releases](../../releases/latest).

---

## 🧰 Como gerar o executável (para desenvolvedores)

Caso precise atualizar o `.exe`, use o [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
python -m PyInstaller --onedir --noconsole --icon=assets/icone_menhera-kun.ico --add-data "assets:assets" main.py
```

O executável será criado na pasta `dist/`.

---

## 👥 Contribuição

Este projeto é mantido pela equipe de desenvolvimento.
Sugestões e melhorias podem ser feitas via _pull request_ ou _issue_ no repositório.
