# Errori Database Supabase

> **Ultimo aggiornamento:** 2026-02-11
> **Migrazione applicata:** `sec_01_rls_revoke` (Alembic)

---

## Riepilogo

| Categoria | Totale | Risolti | Residui |
|-----------|--------|---------|---------|
| security_definer_view | 15 | 15 | 0 |
| rls_disabled_in_public | 48 | 48 | 0 |
| **Totale** | **63** | **63** | **0** |

---

## 1. Security Definer View (15/15 RISOLTI)

Tutte le 15 viste sono state convertite da `SECURITY DEFINER` a `SECURITY INVOKER`
tramite `ALTER VIEW ... SET (security_invoker = on)`.

Le viste ora eseguono con i permessi del chiamante, rispettando RLS e REVOKE.

| Vista | Stato |
|-------|-------|
| `vw_financials_monthly_wide` | RISOLTO |
| `vw_sp_map_coverage` | RISOLTO |
| `vw_banks_monthly_wide` | RISOLTO |
| `vw_ce_map_coverage` | RISOLTO |
| `vw_fin_kpi_latest` | RISOLTO |
| `vw_sp_unmapped_sample` | RISOLTO |
| `vw_fin_kpi_standard_latest` | RISOLTO |
| `vw_cf_monthly` | RISOLTO |
| `vw_financials_monthly` | RISOLTO |
| `vw_financials_monthly_long_full` | RISOLTO |
| `vw_ce_unmapped_sample` | RISOLTO |
| `vw_banks_monthly` | RISOLTO |
| `vw_kpi_base` | RISOLTO |
| `v_ce_monthly_summary` | RISOLTO |
| `v_sp_monthly_summary` | RISOLTO |

---

## 2. RLS Disabled in Public (48/48 RISOLTI)

Row Level Security abilitata su tutte le 48 tabelle dello schema public
tramite `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.

Nessuna policy RLS definita (deny-all): i ruoli `anon` e `authenticated` non hanno
accesso. Il backend opera tramite `postgres` (superuser) e `service_role`, che
bypassano RLS automaticamente.

| Tabella | Stato |
|---------|-------|
| `users` | RISOLTO |
| `companies` | RISOLTO |
| `cases` | RISOLTO |
| `case_snapshots` | RISOLTO |
| `uploads` | RISOLTO |
| `assumptions` | RISOLTO |
| `alembic_version` | RISOLTO |
| `stg_tb_entries` | RISOLTO |
| `stg_xbrl_facts` | RISOLTO |
| `stg_map_sp` | RISOLTO |
| `stg_map_ce` | RISOLTO |
| `stg_map_sp_backup` | RISOLTO |
| `stg_map_ce_backup` | RISOLTO |
| `backup_stg_map_sp` | RISOLTO |
| `backup_stg_map_ce` | RISOLTO |
| `fin_sp_riclass` | RISOLTO |
| `fin_ce_riclass` | RISOLTO |
| `fin_sp_monthly` | RISOLTO |
| `fin_ce_monthly` | RISOLTO |
| `fin_banks_monthly` | RISOLTO |
| `fin_cflow_monthly` | RISOLTO |
| `fin_kpi_monthly` | RISOLTO |
| `fin_kpi_standard` | RISOLTO |
| `lkp_cflow_map` | RISOLTO |
| `lkp_banks_master` | RISOLTO |
| `lkp_banks_map` | RISOLTO |
| `dim_calendar` | RISOLTO |
| `dim_month` | RISOLTO |
| `mdm_attivo_items` | RISOLTO |
| `mdm_attivo_schedule` | RISOLTO |
| `mdm_scenarios` | RISOLTO |
| `mdm_passivo_items` | RISOLTO |
| `mdm_passivo_tipologie` | RISOLTO |
| `mdm_liquidazione` | RISOLTO |
| `mdm_cessione_monthly` | RISOLTO |
| `mdm_concordato_monthly` | RISOLTO |
| `mdm_affitto_monthly` | RISOLTO |
| `mdm_prededuzione_monthly` | RISOLTO |
| `mdm_ce_projection` | RISOLTO |
| `mdm_sp_projection` | RISOLTO |
| `mdm_cflow_projection` | RISOLTO |
| `mdm_banca_projection` | RISOLTO |
| `mdm_test_piat` | RISOLTO |
| `mdm_nuovo_finanziamento` | RISOLTO |
| `mdm_finanziamento_schedule` | RISOLTO |
| `mdm_scadenziario_tributario` | RISOLTO |
| `mdm_scadenziario_tributario_rate` | RISOLTO |
| `mdm_imm_fin_movimenti` | RISOLTO |

---

## 3. Azioni aggiuntive applicate

### REVOKE privilegi PostgREST

Revocati tutti i permessi ai ruoli `anon` e `authenticated` su tabelle, sequenze
e funzioni nello schema public. Anche i `DEFAULT PRIVILEGES` sono stati revocati
per impedire accesso automatico a oggetti creati in futuro.

```sql
REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM anon;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES    FROM anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM anon;
-- Idem per authenticated
```

---

## Dettaglio migrazione

- **File:** `alembic/versions/sec_01_rls_revoke_postgrest.py`
- **Revision:** `sec_01_rls_revoke`
- **Parent:** `auth_01_users`
- **Applicata il:** 2026-02-11
