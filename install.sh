#!/usr/bin/env bash
# Instala o Robô de vagas (Linux/Steam Deck): skill do Claude Code + venv + atalho no Desktop.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.claude/skills" "$HOME/.local/bin" "$HOME/.config/robo-vagas/perfis"
chmod 700 "$HOME/.config/robo-vagas" "$HOME/.config/robo-vagas/perfis"
ln -sfn "$DIR/skill" "$HOME/.claude/skills/robo-vagas"
[ -x "$HOME/.venvs/robo-vagas/bin/python" ] || python3 -m venv "$HOME/.venvs/robo-vagas"
"$HOME/.venvs/robo-vagas/bin/pip" install -q --disable-pip-version-check -r "$DIR/requirements.txt"
install -m 755 "$DIR/bin/robo-vagas" "$HOME/.local/bin/robo-vagas"
DESK="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
sed -e "s#@HOME@#$HOME#g" -e "s#@DIR@#$DIR#g" "$DIR/launchers/robo-vagas.desktop.in" > "$DESK/robo-vagas.desktop"
chmod +x "$DESK/robo-vagas.desktop"
echo "Pronto. Dê dois cliques em 'Robô de vagas' no Desktop (ou rode: robo-vagas)."
echo "Na primeira vez o robô faz um questionário para montar o seu perfil."
