#!/usr/bin/env bash
# fix_shuf.sh
# Analyse tous les .sh, remplace "shuf" par un sélecteur POSIX-compatible
# et injecte une fonction pick() si nécessaire.

TARGET_DIR="${1:-.}"

echo "=== Correction automatique des scripts (suppression de shuf) ==="
echo "Cible : $TARGET_DIR"
echo

fix_file() {
  local file="$1"

  # Vérifie présence de shuf
  if ! grep -q "shuf" "$file"; then
    echo "[OK]  $file (aucune occurrence de shuf)"
    return
  fi

  echo "[FIX] $file (shuf détecté, remplacement en cours)"

  # Sauvegarde
  cp "$file" "$file.bak_shuf"

  # Remplacement de pick ... par pick ...
  # On convertit : pick a b c  -> pick a b c
  sed -i '' -E 's/pick/pick/g' "$file"

  # Ajouter la fonction pick() si absente
  if ! grep -q "pick()" "$file"; then
    cat << 'EOF' | cat - "$file" > "$file.tmp" && mv "$file.tmp" "$file"
# --- ajout automatique : fonction pick() compatible POSIX ---
pick() {
  set -- "$@"
  c=$#
  i=$((RANDOM % c + 1))
  eval "echo \${$i}"
}
# ------------------------------------------------------------

EOF
  fi
}

export -f fix_file

# Trouve tous les scripts .sh (récursif)
find "$TARGET_DIR" -type f -name "*.sh" | while read -r f; do
  fix_file "$f"
done

echo
echo "=== Correction terminée ==="
echo "Des copies de sauvegarde *.bak_shuf ont été créées."

