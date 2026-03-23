# Acessos

- ### Usuário Padrão
```bash
sudo -i -u postgres psql
```

- ### Com usuário

```bash
psql -U nome_do_usuario -W
```

# Comandos dentro do terminal postgres

- ### Verificar usuários

```bash
\du
```

- ### Verificar tabelas

```bash
\dt
```

- ### Trocar de Database

```bash
\c nome_da_database
```

# Limpar Database

```bash
DO $$ DECLARE
    r RECORD;
BEGIN
    -- Apagar todas as tabelas
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;

    -- Apagar todas as sequências
    FOR r IN (SELECT sequencename FROM pg_sequences WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequencename) || ' CASCADE';
    END LOOP;

    -- Apagar todas as funções
    FOR r IN (SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public') LOOP
        EXECUTE 'DROP FUNCTION IF EXISTS ' || quote_ident(r.routine_name) || ' CASCADE';
    END LOOP;
END $$;
```