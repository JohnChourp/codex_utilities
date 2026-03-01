---
name: learn-byzantine-calendar-fill
description: Fill one requested month in LearnByzantineMusic calendar dataset with celebrations and readings using the project month-fill pipeline.
---

# learn-byzantine-calendar-fill

Skill για σταδιακό γέμισμα εορτολογίου και αναγνωσμάτων στο project `LearnByzantineMusic`, με είσοδο είτε μήνα είτε συγκεκριμένη ημέρα.

## Scope
- Χρήση μόνο στο repository:
  - `/Users/john/Downloads/projects/LearnByzantineMusic`
- Ενημερώνει μόνο το dataset:
  - `app/src/main/assets/calendar_celebrations_v1.json`

## Input format
- `YYYY-MM` (π.χ. `2025-01`) για γέμισμα ολόκληρου μήνα.
- `YYYY-MM-DD` (π.χ. `2025-01-15`) για γέμισμα του μήνα στον οποίο ανήκει η ημέρα.
- (legacy) `DD-MM-YYYY` (π.χ. `01-01-2025`) με ίδιο αποτέλεσμα: normalize στο αντίστοιχο `YYYY-MM`.

## Behavior
1. Ελέγχει ότι το cwd είναι το `LearnByzantineMusic`.
2. Αν δοθεί `YYYY-MM-DD` (ή legacy `DD-MM-YYYY`), γίνεται normalize σε `YYYY-MM`.
3. Τρέχει:
   - `./scripts/fill_calendar_month.py YYYY-MM`
4. Το script κάνει overwrite μόνο του ζητούμενου μήνα.
5. Γεμίζει:
   - `days` (εορτολόγιο)
   - `readings` (παραπομπές + πλήρες `text_ancient` + πλήρες `text_modern`)
6. Για τα αναγνώσματα εφαρμόζει internet retrieval pipeline:
   - primary source: `saint.gr` (year page + `readingsday` pages)
   - αν το primary source είναι ελλιπές/ασυνεπές για ζητούμενες ημέρες, γίνεται υποχρεωτικό fallback search σε δευτερεύουσες πηγές
   - resolve `YYYY-MM-DD -> readingsday_id` ή ισοδύναμο ημερολογιακό mapping
   - fetch ανά ημέρα και parse όλων των sections
   - split σε πολλαπλά αναγνώσματα ανά ημέρα (καθημερινό + εορτής όπου υπάρχουν)
7. Για `text_modern` εφαρμόζει πολιτική:
   - provider-1: Κολιτσάρα
   - provider-2: Τρεμπέλα
   - provider-3: επιτρεπτός εξωτερικός provider μόνο αν περάσει license policy
   - generated fallback μόνο όταν αποτύχουν/απορριφθούν όλοι
8. Δεν εμφανίζει/αποθηκεύει source metadata σε app data/UI.
9. Επιστρέφει summary:
   - `Days parsed`
   - `Days updated`
   - `apostle count`
   - `gospel count`
   - `provider-1 / provider-2 / provider-3 / generated hits`
   - `days with feast-extra readings`
   - `fallback sources used` (μόνο στο CLI summary, όχι στο app dataset)

## Source fallback policy (mandatory)
1. Πάντα ξεκινά από `saint.gr`.
2. Αν λείπουν ημέρες ή λείπουν sections/readings για ζητούμενη ημέρα, κάνει αναζήτηση και σε άλλες πηγές.
3. Για κάθε εναλλακτική πηγή που αποδίδει έγκυρο αποτέλεσμα, ενημερώνει/εμπλουτίζει το skill με σύντομη οδηγία ώστε να χρησιμοποιείται και μελλοντικά.
4. Προτεραιότητα αξιοπιστίας:
   - εκκλησιαστική/θεολογική επίσημη πηγή
   - πηγή με σταθερό ημερολογιακό mapping και πλήρες κείμενο
   - πηγή που επιτρέπει χρήση βάσει license policy
5. Σε σύγκρουση μεταξύ πηγών:
   - προτιμάται η πηγή υψηλότερης αξιοπιστίας
   - αν η σύγκρουση δεν λύνεται, δεν αποθηκεύεται αμφίβολο κείμενο και σημειώνεται warning στο summary

## Example
- `learn-byzantine-calendar-fill 2025-01`
- `learn-byzantine-calendar-fill 2025-01-15`
- `learn-byzantine-calendar-fill 01-01-2025`

## Safety rules
- Μην αλλάζεις άλλους μήνες πέρα από το requested `YYYY-MM` (ή του μήνα που προκύπτει από `YYYY-MM-DD`).
- Μην αλλάζεις `version/country_scope/language` από `1/GR/el`.
- Κράτα deterministic ταξινόμηση keys (`YYYY-MM-DD`) και entries by `priority`.
- Μην αποθηκεύεις/προβάλεις πουθενά source names, domains ή URLs στο app dataset/UI.
