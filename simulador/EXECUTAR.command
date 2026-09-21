#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
python3 main.py || { echo; read -r -p "Falhou. Pressione Enter para fechar..."; }
