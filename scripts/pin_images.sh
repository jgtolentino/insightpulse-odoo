#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PINS="${ROOT}/ops/pins"
OUT_ENV="${ROOT}/runtime/dev/.env.odoo19"

ODOO_TAG="$(tr -d '\r' < "${PINS}/odoo_19.tag.txt")"
PG_TAG="$(tr -d '\r' < "${PINS}/postgres_16.tag.txt")"
PGADMIN_TAG="$(tr -d '\r' < "${PINS}/pgadmin.tag.txt")"

echo "Pulling pinned tags..."
docker pull "${ODOO_TAG}"
docker pull "${PG_TAG}"
docker pull "${PGADMIN_TAG}"

ODOO_DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "${ODOO_TAG}")"
PG_DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "${PG_TAG}")"
PGADMIN_DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "${PGADMIN_TAG}")"

mkdir -p "$(dirname "${OUT_ENV}")"
printf "ODOO_IMAGE=%s\nPG_IMAGE=%s\nPGADMIN_IMAGE=%s\n" "${ODOO_DIGEST}" "${PG_DIGEST}" "${PGADMIN_DIGEST}" > "${OUT_ENV}"

echo "Pinned:"
echo "  ODOO_IMAGE=${ODOO_DIGEST}"
echo "  PG_IMAGE=${PG_DIGEST}"
echo "  PGADMIN_IMAGE=${PGADMIN_DIGEST}"
echo "Wrote ${OUT_ENV}"
