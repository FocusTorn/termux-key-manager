#!/usr/bin/env bash
# Continuity consistency check. Run from repo root:
#   bash _docs/_continuity/check.sh [slug]    (default: every feature not CLOSED/ABANDONED)
# Needs bash 4+, git, grep, sed (Termux OK). Exit 0 = clean, 1 = failures. Warnings don't fail.
P="${PROGRESS_DIR:-_docs/_continuity}"
fail=0
bad()  { echo "FAIL: $*"; fail=1; }
warn() { echo "WARN: $*"; }
ok()   { echo "ok:   $*"; }
trim() { echo "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/`//g'; }

[ -f "$P/README.md" ] || bad "missing $P/README.md"
[ -f "$P/INDEX.md" ]  || bad "missing $P/INDEX.md"
[ "$fail" -eq 1 ] && exit 1

declare -A STATUS FINAL_SHA
active=0
rows=$(grep -E '^\|' "$P/INDEX.md" | grep -vE '^\|[-: |]+$' | grep -viE '^\| *slug *\|')

# ---- INDEX checks:  | slug | status | final SHA | summary |
while IFS='|' read -r _ s st sha _; do
  s=$(trim "$s"); [ -z "$s" ] && continue
  st=$(trim "$st"); sha=$(trim "$sha")
  STATUS[$s]=$st
  FINAL_SHA[$s]=$sha
  case "$st" in
    ACTIVE) active=$((active+1)) ;;
    PAUSED|BLOCKED) ;;
    CLOSED|ABANDONED)
      C="$P/features/$s/closeout.md"
      [ -f "$C" ] || bad "$s is $st but has no closeout.md"
      if [ -z "$sha" ]; then
        bad "$s is $st but INDEX has no final SHA"
      elif git rev-parse --git-dir >/dev/null 2>&1; then
        git cat-file -e "${sha}^{commit}" 2>/dev/null || bad "$s: INDEX final SHA $sha not found"
      fi
      [ -f "$P/features/$s/progress-log.md" ] || bad "$s: terminal feature has no progress-log.md for closeout evidence"
      if [ -f "$C" ]; then
        outcome=$(grep -m1 '^\*\*Outcome:\*\*' "$C" | sed -E 's/^\*\*Outcome:\*\*[[:space:]]*//' | tr -d '\r')
        case "$st:$outcome" in
          CLOSED:MET|CLOSED:PARTIAL|ABANDONED:ABANDONED) ;;
          CLOSED:*) bad "$s: INDEX status CLOSED conflicts with closeout outcome '$outcome' (expected MET or PARTIAL)" ;;
          ABANDONED:*) bad "$s: INDEX status ABANDONED conflicts with closeout outcome '$outcome' (expected ABANDONED)" ;;
        esac
        csha=$(grep -m1 '^\*\*Final SHA:\*\*' "$C" | grep -oE '[0-9a-fA-F]{7,40}' | head -1 | tr 'A-F' 'a-f')
        isha=$(printf '%s' "$sha" | tr 'A-F' 'a-f')
        if [ -z "$csha" ]; then
          bad "$s: closeout has no valid '**Final SHA:**' value"
        elif [ -z "$isha" ]; then
          bad "$s: INDEX has no final SHA to compare with closeout"
        elif [ "$csha" != "$isha" ]; then
          bad "$s: closeout Final SHA $csha does not match INDEX SHA $isha"
        fi
        local_ids=$(sed -E 's/[a-z0-9][a-z0-9-]*:(PL-[0-9]{4})//g' "$C" | grep -oE 'PL-[0-9]{4}' | sort -u)
        for id in $local_ids; do
          grep -qE "^## $id\\b" "$P/features/$s/progress-log.md" 2>/dev/null || bad "$s: closeout cites $id but no matching progress-log entry exists"
        done
        cross_refs=$(grep -oE '[a-z0-9][a-z0-9-]*:PL-[0-9]{4}' "$C" | sort -u)
        for ref in $cross_refs; do
          rslug=${ref%%:*}; rid=${ref#*:}
          if [ ! -f "$P/features/$rslug/progress-log.md" ]; then
            bad "$s: closeout reference $ref points to a missing feature log"
          elif ! grep -qE "^## $rid\\b" "$P/features/$rslug/progress-log.md"; then
            bad "$s: closeout reference $ref has no matching progress-log entry"
          fi
        done
      fi ;;
    *) bad "INDEX: $s has invalid status '$st'" ;;
  esac
  [ -d "$P/features/$s" ] || bad "INDEX lists $s but $P/features/$s is missing"
done <<< "$rows"
[ "$active" -gt 1 ] && warn "$active features marked ACTIVE (normally one; fine if intentional)"
for d in "$P"/features/*/; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  [ -n "${STATUS[$n]:-}" ] || bad "feature dir $n is not in INDEX.md"
done

check_feature() {
  local slug="$1" F="$P/features/$1"
  local H="$F/handoff.md" R="$F/roadmap.md" L="$F/progress-log.md"
  echo "== $slug (${STATUS[$slug]:-?})"
  local f
  for f in handoff.md roadmap.md progress-log.md; do
    [ -f "$F/$f" ] || { bad "$slug: missing $f"; return; }
  done

  local sha; sha=$(grep -m1 'Valid as of' "$H" | grep -oE '[0-9a-f]{7,40}' | head -1)
  if [ -z "$sha" ]; then bad "$slug: handoff has no 'Valid as of' SHA"
  elif ! git rev-parse --git-dir >/dev/null 2>&1; then warn "$slug: not a git repo; staleness unchecked"
  elif ! git cat-file -e "${sha}^{commit}" 2>/dev/null; then bad "$slug: Valid-as-of SHA $sha not found (pull first?)"
  else
    local n changed
    n=$(git rev-list --count "${sha}..HEAD")
    changed=$(git diff --name-only "$sha" HEAD -- . ":(exclude)$P")
    if [ -n "$changed" ]; then
      warn "$slug: $n commit(s) since $sha changed non-continuity files; assess impact (not automatically stale):"
      echo "$changed" | sed 's/^/        /' | head -15
    else ok "$slug: no non-continuity changes since $sha"; fi
  fi

  local p missing=0
  for p in $(cat "$H" "$R" | grep -oE '`[^`]+`' | tr -d '`' | grep '/' \
      | grep -vE '[[:space:]<>*{}|]|^https?:|^-' | sort -u); do
    [ -e "$p" ] || { bad "$slug: referenced path missing: $p"; missing=1; }
  done
  [ "$missing" -eq 0 ] && ok "$slug: referenced paths resolve"

  local ref rs rid
  for ref in $(cat "$H" "$R" | grep -oE '[a-z0-9][a-z0-9-]*:(PL-[0-9]{4}|D-[0-9]{3}|G[0-9]+)' | sort -u); do
    rs=${ref%%:*}; rid=${ref#*:}
    [ -d "$P/features/$rs" ] || { bad "$slug: ref $ref points to unknown feature"; continue; }
    case "$rid" in
      PL-*) grep -qE "^## $rid\\b" "$P/features/$rs/progress-log.md" || bad "$slug: $ref not found" ;;
      *)    grep -qE "^### $rid\\b" "$P/features/$rs/roadmap.md"     || bad "$slug: $ref not found" ;;
    esac
  done

  local id
  for id in $(cat "$H" "$R" | sed -E 's/[a-z0-9][a-z0-9-]*:(PL-[0-9]{4}|D-[0-9]{3}|G[0-9]+)//g' \
      | grep -oE 'PL-[0-9]{4}' | sort -u); do
    grep -qE "^## $id\\b" "$L" || bad "$slug: $id cited but no entry in progress-log"
  done
  for id in $(grep -oE 'D-[0-9]{3}' "$H" | sort -u); do
    grep -qE "^### $id\\b" "$R" || bad "$slug: $id cited in handoff but not defined in roadmap"
  done

  local latest marker hmark
  latest=$(grep -oE '^## PL-[0-9]{4}' "$L" | tail -1 | sed 's/^## //')
  marker=$(grep -m1 '^\*\*Progress through:\*\*' "$R" | grep -oE 'PL-[0-9]{4}')
  if [ -z "$latest" ]; then bad "$slug: progress-log has no PL-#### entry"
  elif [ -z "$marker" ]; then bad "$slug: roadmap has no '**Progress through:** PL-####' marker"
  elif [ "$marker" != "$latest" ]; then bad "$slug: roadmap reviewed through $marker but newest log entry is $latest"
  else ok "$slug: roadmap marker matches newest log entry ($latest)"; fi

  hmark=$(grep -m1 '^\*\*Roadmap reviewed through:\*\*' "$H" | grep -oE 'PL-[0-9]{4}')
  if [ -z "$hmark" ]; then warn "$slug: handoff has no '**Roadmap reviewed through:**' line"
  elif [ -n "$marker" ] && [ "$hmark" != "$marker" ]; then
    warn "$slug: handoff reviewed through $hmark but roadmap through $marker (refresh at next transfer boundary)"
  fi

  # Keep dependency links as history. Only unresolved prerequisites warn;
  # a DONE gate satisfies the dependency and must not create recurring noise.
  local dep dslug gate_status
  for dep in $(grep -m1 '^\*\*Depends on:\*\*' "$R" | grep -oE '[a-z0-9][a-z0-9-]*:G[0-9]+'); do
    dslug=${dep%%:*}
    if [ "${STATUS[$dslug]:-}" = ABANDONED ]; then
      bad "$slug: depends on $dep but $dslug is ABANDONED"
      continue
    fi
    if [ -f "$P/features/$dslug/roadmap.md" ]; then
      gate_status=$(awk -v g="### ${dep#*:}" 'index($0,g)==1{f=1;next} /^### /{f=0} f&&/^\*\*Status:\*\*/{sub(/^\*\*Status:\*\*[[:space:]]*/,""); print; exit}' "$P/features/$dslug/roadmap.md")
      if [[ "$gate_status" == DONE* ]]; then
        : # satisfied dependency; preserve the link without warning
      elif [ "${STATUS[$dslug]:-}" = CLOSED ]; then
        bad "$slug: depends on $dep, but $dslug is CLOSED while that gate is '$gate_status'"
      elif [ -z "$gate_status" ]; then
        bad "$slug: dependency $dep does not resolve to a gate status"
      else
        warn "$slug: prerequisite $dep is unresolved (gate status: $gate_status)"
      fi
    fi
  done

  local nh nr
  nh=$(grep -m1 '^\*\*Next action:\*\*' "$H"); nr=$(grep -m1 '^\*\*Next action:\*\*' "$R")
  if [ -z "$nh" ] || [ -z "$nr" ]; then bad "$slug: missing '**Next action:**' in handoff or roadmap"
  elif [ "$nh" != "$nr" ]; then bad "$slug: next action differs between handoff and roadmap"
  else ok "$slug: next action matches"; fi

  local line
  while IFS= read -r line; do
    case "$line" in
      "**Status:** NOT STARTED"*|"**Status:** IN PROGRESS"*|"**Status:** BLOCKED"*) ;;
      "**Status:** DONE"*) echo "$line" | grep -qE 'PL-[0-9]{4}' || bad "$slug: DONE gate lacks PL citation: $line" ;;
      *) bad "$slug: invalid gate status: $line" ;;
    esac
  done < <(grep '^\*\*Status:\*\*' "$R")
}

if [ -n "${1:-}" ]; then
  [ -n "${STATUS[$1]:-}" ] || { bad "unknown feature: $1"; exit 1; }
  case "${STATUS[$1]}" in CLOSED|ABANDONED) echo "== $1 (${STATUS[$1]}) [terminal; closeout checked]" ;; *) check_feature "$1" ;; esac
else
  for s in "${!STATUS[@]}"; do
    case "${STATUS[$s]}" in CLOSED|ABANDONED) continue ;; esac
    check_feature "$s"
  done
fi

echo; [ "$fail" -eq 0 ] && echo "RESULT: clean" || echo "RESULT: FAILURES (see above)"
exit "$fail"
