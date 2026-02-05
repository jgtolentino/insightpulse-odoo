#!/usr/bin/env bash
set -euo pipefail
command -v supabase >/dev/null 2>&1 || { echo "supabase CLI missing"; exit 2; }
supabase start
