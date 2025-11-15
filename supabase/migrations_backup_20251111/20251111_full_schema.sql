-- SkyApp Full Schema Migration (idempotent)
-- This migration creates extensions, types, tables, indexes, triggers, and RLS policies.
-- Safe to re-run: guarded with IF NOT EXISTS or exception handling.

-- 1) Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2) Enums (create if missing)
DO $$
BEGIN
  BEGIN
    CREATE TYPE user_role AS ENUM ('ADMIN', 'BUREAU', 'TECHNICIEN');
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE TYPE search_status AS ENUM ('DRAFT', 'ACTIVE', 'SHARED', 'SHARED_TO_BUREAU', 'PROCESSED', 'ARCHIVED');
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE TYPE quote_status AS ENUM ('DRAFT', 'SENT', 'ACCEPTED', 'REJECTED', 'EXPIRED');
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE TYPE worksite_status AS ENUM ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE TYPE worksite_source AS ENUM ('QUOTE', 'MANUAL');
  EXCEPTION WHEN duplicate_object THEN NULL; END;
END$$;

-- Ensure DRAFT value exists on search_status
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    WHERE t.typname = 'search_status' AND e.enumlabel = 'DRAFT'
  ) THEN
    ALTER TYPE search_status ADD VALUE 'DRAFT';
  END IF;
END$$;

-- 3) Tables
CREATE TABLE IF NOT EXISTS public.companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT NOT NULL UNIQUE,
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL,
  role user_role NOT NULL,
  company_id UUID REFERENCES public.companies(id),
  actif BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.clients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES public.companies(id),
  nom TEXT NOT NULL,
  email TEXT NOT NULL,
  telephone TEXT,
  adresse TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.searches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.users(id),
  company_id UUID NOT NULL REFERENCES public.companies(id),
  location TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL DEFAULT '',
  observations TEXT,
  latitude DECIMAL(10,8),
  longitude DECIMAL(11,8),
  status search_status DEFAULT 'ACTIVE',
  photos JSONB DEFAULT '[]'::jsonb,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.quotes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES public.companies(id),
  client_id UUID NOT NULL REFERENCES public.clients(id),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL DEFAULT 0,
  status quote_status DEFAULT 'DRAFT',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.worksites (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  client_id UUID REFERENCES public.clients(id),
  client_name TEXT DEFAULT '',
  quote_id UUID REFERENCES public.quotes(id),
  company_id UUID NOT NULL REFERENCES public.companies(id),
  source worksite_source DEFAULT 'MANUAL',
  status worksite_status DEFAULT 'PLANNED',
  description TEXT DEFAULT '',
  address TEXT DEFAULT '',
  amount DECIMAL(10,2) DEFAULT 0.0,
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  search_id UUID NOT NULL REFERENCES public.searches(id),
  user_id UUID NOT NULL REFERENCES public.users(id),
  company_id UUID NOT NULL REFERENCES public.companies(id),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.materials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES public.companies(id),
  name TEXT NOT NULL,
  description TEXT,
  category TEXT,
  qr_code TEXT UNIQUE NOT NULL,
  location TEXT,
  status TEXT DEFAULT 'DISPONIBLE',
  assigned_to UUID REFERENCES public.users(id),
  assigned_date TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4) Indexes
CREATE INDEX IF NOT EXISTS idx_users_company_id ON public.users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_searches_user_id ON public.searches(user_id);
CREATE INDEX IF NOT EXISTS idx_searches_company_id ON public.searches(company_id);
CREATE INDEX IF NOT EXISTS idx_searches_status ON public.searches(status);
CREATE INDEX IF NOT EXISTS idx_searches_status_updated_at ON public.searches(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_clients_company_id ON public.clients(company_id);
CREATE INDEX IF NOT EXISTS idx_quotes_company_id ON public.quotes(company_id);
CREATE INDEX IF NOT EXISTS idx_quotes_client_id ON public.quotes(client_id);
CREATE INDEX IF NOT EXISTS idx_worksites_company_id ON public.worksites(company_id);
CREATE INDEX IF NOT EXISTS idx_materials_company_id ON public.materials(company_id);
CREATE INDEX IF NOT EXISTS idx_materials_qr_code ON public.materials(qr_code);

-- 5) updated_at trigger
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_companies_updated_at'
  ) THEN
    CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON public.companies FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_updated_at'
  ) THEN
    CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_clients_updated_at'
  ) THEN
    CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON public.clients FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_searches_updated_at'
  ) THEN
    CREATE TRIGGER update_searches_updated_at BEFORE UPDATE ON public.searches FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_quotes_updated_at'
  ) THEN
    CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON public.quotes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_worksites_updated_at'
  ) THEN
    CREATE TRIGGER update_worksites_updated_at BEFORE UPDATE ON public.worksites FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_reports_updated_at'
  ) THEN
    CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON public.reports FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_materials_updated_at'
  ) THEN
    CREATE TRIGGER update_materials_updated_at BEFORE UPDATE ON public.materials FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
  END IF;
END $$;

-- 6) RLS enable
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.worksites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.materials ENABLE ROW LEVEL SECURITY;

-- 7) Policies (create if not exists by catching duplicates)
DO $$ BEGIN
  BEGIN
    CREATE POLICY "Users can view their own company" ON public.companies
      FOR SELECT USING (id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Admins can manage their company" ON public.companies
      FOR ALL USING (id IN (SELECT company_id FROM public.users WHERE id = auth.uid() AND role = 'ADMIN'));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Users can view users in their company" ON public.users
      FOR SELECT USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Admins can manage users in their company" ON public.users
      FOR ALL USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid() AND role = 'ADMIN'));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Company access clients" ON public.clients
      FOR ALL USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Company access searches" ON public.searches
      FOR ALL USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Company access quotes" ON public.quotes
      FOR ALL USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Company access worksites" ON public.worksites
      FOR ALL USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Company access reports" ON public.reports
      FOR ALL USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    CREATE POLICY "Company access materials" ON public.materials
      FOR ALL USING (company_id IN (SELECT company_id FROM public.users WHERE id = auth.uid()));
  EXCEPTION WHEN duplicate_object THEN NULL; END;
END $$;
