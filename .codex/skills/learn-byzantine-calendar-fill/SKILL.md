---
name: learn-byzantine-calendar-fill
description: Fill one LearnByzantineMusic calendar month with celebrations and liturgical readings.
---

# learn-byzantine-calendar-fill

Skill για σταδιακό γέμισμα εορτολογίου και αναγνωσμάτων στο project `LearnByzantineMusic`, με είσοδο είτε μήνα είτε συγκεκριμένη ημέρα.

## Scope
- Χρήση μόνο στο repository:
  - `~/Downloads/projects/LearnByzantineMusic`
- Ενημερώνει μόνο το dataset:
  - `app/src/main/assets/calendar_celebrations_v1.json`

## Input format
- `YYYY-MM` (π.χ. `2025-01`) για γέμισμα ολόκληρου μήνα.
- (legacy) `DD-MM-YYYY` (π.χ. `01-01-2025`) με ίδιο αποτέλεσμα: normalize στο αντίστοιχο `YYYY-MM`.

## Bootstrap (one-time)
- Για seed προστατευμένων ημερών (αμετακίνητες γιορτές + επίσημες αργίες) στα έτη 2025-2026:
  - `./scripts/seed_protected_days.py 2025 2026`
- Το seed είναι deterministic, χωρίς internet retrieval, και κάνει insert μόνο σε missing ημερομηνίες.

## Behavior
1. Ελέγχει ότι το cwd είναι το `LearnByzantineMusic`.
2. Αν δοθεί legacy `DD-MM-YYYY`, γίνεται normalize σε `YYYY-MM`.
3. Τρέχει:
   - `./scripts/fill_calendar_month.py YYYY-MM`
4. Το script ενημερώνει μόνο τον ζητούμενο μήνα.
5. Γεμίζει:
   - `days` (εορτολόγιο)
   - `readings` (παραπομπές + πλήρες `text_ancient` + πλήρες `text_modern`)
6. Οι protected ημερομηνίες (αμετακίνητες γιορτές + επίσημες αργίες) στο `days`:
   - δεν γίνονται overwrite αν ήδη υπάρχουν,
   - προστίθενται αυτόματα μόνο αν λείπουν.
7. Για τα αναγνώσματα εφαρμόζεται retrieval pipeline από το υπάρχον script (`saint.gr`) ανά ημέρα του μήνα.
8. Για `text_modern` εφαρμόζει πολιτική:
   - provider-1: Κολιτσάρα
   - provider-2: Τρεμπέλα
   - provider-3: επιτρεπτός εξωτερικός provider μόνο αν περάσει license policy
   - generated fallback μόνο όταν αποτύχουν/απορριφθούν όλοι
9. Δεν εμφανίζει/αποθηκεύει source metadata σε app data/UI.
10. Επιστρέφει summary:
   - `Days parsed`
   - `Days updated`
   - `apostle count`
   - `gospel count`
   - `provider-1 / provider-2 / provider-3 / generated hits`
   - `days with feast-extra readings`

## Example
- `learn-byzantine-calendar-fill 2025-01`
- `learn-byzantine-calendar-fill 01-01-2025`
- `./scripts/seed_protected_days.py 2025 2026`

## Safety rules
- Μην αλλάζεις άλλους μήνες πέρα από το requested `YYYY-MM` (ή του μήνα που προκύπτει από `DD-MM-YYYY`).
- Μην αλλάζεις `version/country_scope/language` από `1/GR/el`.
- Κράτα deterministic ταξινόμηση keys (`YYYY-MM-DD`) και entries by `priority`.
- Μην αποθηκεύεις/προβάλεις πουθενά source names, domains ή URLs στο app dataset/UI.
