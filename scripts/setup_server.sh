#!/usr/bin/env bash
#
# Serverda bazani noldan tayyorlaydi va kontent bilan to'ldiradi.
#
# Ishlatish:
#   cd portfolio_backend
#   bash scripts/setup_server.sh
#
# Nima qiladi:
#   1. .env borligini tekshiradi
#   2. Bog'liqliklarni o'rnatadi (pipenv)
#   3. Migratsiyalarni bajaradi
#   4. Kontentni yozadi (profil, ko'nikmalar, loyihalar, havolalar)
#   5. Static fayllarni yig'adi
#
# Baza git'ga qo'shilmaydi — shuning uchun har bir serverda shu skript ishlatiladi.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "▸ Loyiha papkasi: $PROJECT_DIR"

# ── 1. .env tekshiruvi ────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "✗ .env fayli topilmadi."
  echo "  .env.example dan nusxa oling va SECRET_KEY ni to'ldiring:"
  echo "    cp .env.example .env"
  exit 1
fi

if ! grep -q '^SECRET_KEY=.\+' .env; then
  echo "✗ .env ichida SECRET_KEY bo'sh yoki yo'q."
  exit 1
fi

echo "✓ .env topildi"

# ── 2. Bog'liqliklar ──────────────────────────────────────────────────
echo "▸ Bog'liqliklar o'rnatilmoqda…"
pipenv install --deploy

RUN="pipenv run python manage.py"

# ── 3. Migratsiyalar ──────────────────────────────────────────────────
echo "▸ Migratsiyalar…"
$RUN migrate --noinput

# ── 4. Kontent ────────────────────────────────────────────────────────
# --reset bayrog'i bilan ishlatilsa, eski kontent o'chirilib qayta yoziladi.
echo "▸ Kontent yozilmoqda…"
$RUN seed_portfolio "$@"

# ── 5. Static fayllar ─────────────────────────────────────────────────
echo "▸ Static fayllar yig'ilmoqda…"
$RUN collectstatic --noinput

echo ""
echo "✓ Tayyor."
echo ""
echo "Keyingi qadamlar:"
echo "  1. Admin foydalanuvchi yarating:  pipenv run python manage.py createsuperuser"
echo "  2. Rasm va CV faylini admin panel orqali yuklang"
echo "  3. Serverni ishga tushiring:      pipenv run gunicorn portfolio.wsgi"
