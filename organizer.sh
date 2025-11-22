#!/usr/bin/env bash
# Organizes CSV files by timestamping and archiving them with a log entry.

set -euo pipefail

archive_dir="./archive"
log_file="organizer.log"

# Ensure archive directory exists.
mkdir -p "$archive_dir"

found_any=false

# Process CSV files in the current directory only.
while IFS= read -r -d '' file; do
  found_any=true
  base_name="$(basename "$file")"
  timestamp="$(date +"%Y%m%d-%H%M%S")"
  name_without_ext="${base_name%.csv}"
  new_name="${name_without_ext}-${timestamp}.csv"
  destination="${archive_dir}/${new_name}"

  # Record an entry with the file contents before moving.
  {
    echo "[$(date -Iseconds)] ${base_name} -> ${new_name}"
    cat "$file"
    echo
  } >> "$log_file"

  mv "$file" "$destination"
  echo "Archived ${base_name} -> ${destination}"
done < <(find . -maxdepth 1 -type f -name "*.csv" -print0)

if ! $found_any; then
  echo "No CSV files found to archive."
fi
