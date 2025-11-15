


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA IF NOT EXISTS "public";


ALTER SCHEMA "public" OWNER TO "pg_database_owner";


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE TYPE "public"."quote_status" AS ENUM (
    'DRAFT',
    'SENT',
    'ACCEPTED',
    'REJECTED',
    'EXPIRED'
);


ALTER TYPE "public"."quote_status" OWNER TO "postgres";


CREATE TYPE "public"."search_status" AS ENUM (
    'ACTIVE',
    'SHARED',
    'SHARED_TO_BUREAU',
    'PROCESSED',
    'ARCHIVED',
    'DRAFT'
);


ALTER TYPE "public"."search_status" OWNER TO "postgres";


CREATE TYPE "public"."user_role" AS ENUM (
    'ADMIN',
    'BUREAU',
    'TECHNICIEN'
);


ALTER TYPE "public"."user_role" OWNER TO "postgres";


CREATE TYPE "public"."worksite_source" AS ENUM (
    'QUOTE',
    'MANUAL'
);


ALTER TYPE "public"."worksite_source" OWNER TO "postgres";


CREATE TYPE "public"."worksite_status" AS ENUM (
    'PLANNED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE "public"."worksite_status" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_current_company_id"() RETURNS "uuid"
    LANGUAGE "sql" STABLE SECURITY DEFINER
    AS $$
  select company_id from users where id = (select auth.uid());
$$;


ALTER FUNCTION "public"."get_current_company_id"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_updated_at_column"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
begin
  new.updated_at = now();
  return new;
end;
$$;


ALTER FUNCTION "public"."update_updated_at_column"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."clients" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "company_id" "uuid" NOT NULL,
    "nom" "text" NOT NULL,
    "email" "text" NOT NULL,
    "telephone" "text",
    "adresse" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."clients" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."companies" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."companies" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."quotes" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "company_id" "uuid" NOT NULL,
    "client_id" "uuid",
    "title" "text" NOT NULL,
    "description" "text" NOT NULL,
    "amount" numeric(10,2) DEFAULT 0 NOT NULL,
    "status" "public"."quote_status" DEFAULT 'DRAFT'::"public"."quote_status",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."quotes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."searches" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "user_id" "uuid",
    "company_id" "uuid" NOT NULL,
    "location" "text" NOT NULL,
    "description" "text" NOT NULL,
    "observations" "text",
    "latitude" numeric(10,8),
    "longitude" numeric(11,8),
    "status" "public"."search_status" DEFAULT 'ACTIVE'::"public"."search_status",
    "photos" "jsonb" DEFAULT '[]'::"jsonb",
    "timestamp" timestamp with time zone DEFAULT "now"(),
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."searches" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users" (
    "id" "uuid" NOT NULL,
    "email" "text" NOT NULL,
    "nom" "text" NOT NULL,
    "prenom" "text" NOT NULL,
    "role" "public"."user_role" NOT NULL,
    "company_id" "uuid",
    "actif" boolean DEFAULT true,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."users" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."worksites" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "title" "text" NOT NULL,
    "client_id" "uuid",
    "client_name" "text" DEFAULT ''::"text",
    "quote_id" "uuid",
    "company_id" "uuid" NOT NULL,
    "source" "public"."worksite_source" DEFAULT 'MANUAL'::"public"."worksite_source",
    "status" "public"."worksite_status" DEFAULT 'PLANNED'::"public"."worksite_status",
    "description" "text" DEFAULT ''::"text",
    "address" "text" DEFAULT ''::"text",
    "amount" numeric(10,2) DEFAULT 0.0,
    "start_date" "date",
    "end_date" "date",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."worksites" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."company_stats" AS
 SELECT "c"."id",
    "c"."name",
    "count"(DISTINCT "u"."id") AS "total_users",
    "count"(DISTINCT "s"."id") AS "total_searches",
    "count"(DISTINCT "cl"."id") AS "total_clients",
    "count"(DISTINCT "q"."id") AS "total_quotes",
    "count"(DISTINCT "w"."id") AS "total_worksites"
   FROM ((((("public"."companies" "c"
     LEFT JOIN "public"."users" "u" ON (("c"."id" = "u"."company_id")))
     LEFT JOIN "public"."searches" "s" ON (("c"."id" = "s"."company_id")))
     LEFT JOIN "public"."clients" "cl" ON (("c"."id" = "cl"."company_id")))
     LEFT JOIN "public"."quotes" "q" ON (("c"."id" = "q"."company_id")))
     LEFT JOIN "public"."worksites" "w" ON (("c"."id" = "w"."company_id")))
  GROUP BY "c"."id", "c"."name";


ALTER VIEW "public"."company_stats" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."materials" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "company_id" "uuid" NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "category" "text",
    "qr_code" "text" NOT NULL,
    "location" "text",
    "status" "text" DEFAULT 'DISPONIBLE'::"text",
    "assigned_to" "uuid",
    "assigned_date" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "materials_status_check" CHECK (("status" = ANY (ARRAY['DISPONIBLE'::"text", 'INDISPONIBLE'::"text", 'ASSIGNED'::"text"])))
);


ALTER TABLE "public"."materials" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."reports" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "search_id" "uuid" NOT NULL,
    "user_id" "uuid",
    "company_id" "uuid" NOT NULL,
    "title" "text" NOT NULL,
    "content" "text" NOT NULL,
    "pdf_url" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."reports" OWNER TO "postgres";


ALTER TABLE ONLY "public"."clients"
    ADD CONSTRAINT "clients_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."companies"
    ADD CONSTRAINT "companies_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."materials"
    ADD CONSTRAINT "materials_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."materials"
    ADD CONSTRAINT "materials_qr_code_key" UNIQUE ("qr_code");



ALTER TABLE ONLY "public"."quotes"
    ADD CONSTRAINT "quotes_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."reports"
    ADD CONSTRAINT "reports_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."searches"
    ADD CONSTRAINT "searches_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_email_key" UNIQUE ("email");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."worksites"
    ADD CONSTRAINT "worksites_pkey" PRIMARY KEY ("id");



CREATE INDEX "idx_clients_company_id" ON "public"."clients" USING "btree" ("company_id");



CREATE INDEX "idx_materials_company_id" ON "public"."materials" USING "btree" ("company_id");



CREATE INDEX "idx_materials_qr_code" ON "public"."materials" USING "btree" ("qr_code");



CREATE INDEX "idx_quotes_client_id" ON "public"."quotes" USING "btree" ("client_id");



CREATE INDEX "idx_quotes_company_id" ON "public"."quotes" USING "btree" ("company_id");



CREATE INDEX "idx_searches_company_id" ON "public"."searches" USING "btree" ("company_id");



CREATE INDEX "idx_searches_status" ON "public"."searches" USING "btree" ("status");



CREATE INDEX "idx_searches_user_id" ON "public"."searches" USING "btree" ("user_id");



CREATE INDEX "idx_users_company_id" ON "public"."users" USING "btree" ("company_id");



CREATE INDEX "idx_users_company_id_id" ON "public"."users" USING "btree" ("company_id", "id");



CREATE INDEX "idx_users_email" ON "public"."users" USING "btree" ("email");



CREATE INDEX "idx_users_id" ON "public"."users" USING "btree" ("id");



CREATE INDEX "idx_worksites_company_id" ON "public"."worksites" USING "btree" ("company_id");



CREATE OR REPLACE TRIGGER "update_clients_updated_at" BEFORE UPDATE ON "public"."clients" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_companies_updated_at" BEFORE UPDATE ON "public"."companies" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_materials_updated_at" BEFORE UPDATE ON "public"."materials" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_quotes_updated_at" BEFORE UPDATE ON "public"."quotes" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_reports_updated_at" BEFORE UPDATE ON "public"."reports" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_searches_updated_at" BEFORE UPDATE ON "public"."searches" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_users_updated_at" BEFORE UPDATE ON "public"."users" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_worksites_updated_at" BEFORE UPDATE ON "public"."worksites" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



ALTER TABLE ONLY "public"."clients"
    ADD CONSTRAINT "clients_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."materials"
    ADD CONSTRAINT "materials_assigned_to_fkey" FOREIGN KEY ("assigned_to") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."materials"
    ADD CONSTRAINT "materials_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."quotes"
    ADD CONSTRAINT "quotes_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "public"."clients"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."quotes"
    ADD CONSTRAINT "quotes_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."reports"
    ADD CONSTRAINT "reports_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."reports"
    ADD CONSTRAINT "reports_search_id_fkey" FOREIGN KEY ("search_id") REFERENCES "public"."searches"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."reports"
    ADD CONSTRAINT "reports_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."searches"
    ADD CONSTRAINT "searches_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."searches"
    ADD CONSTRAINT "searches_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."worksites"
    ADD CONSTRAINT "worksites_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "public"."clients"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."worksites"
    ADD CONSTRAINT "worksites_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."worksites"
    ADD CONSTRAINT "worksites_quote_id_fkey" FOREIGN KEY ("quote_id") REFERENCES "public"."quotes"("id") ON DELETE SET NULL;



ALTER TABLE "public"."clients" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "clients_delete" ON "public"."clients" FOR DELETE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "clients_insert" ON "public"."clients" FOR INSERT TO "authenticated" WITH CHECK (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "clients_select" ON "public"."clients" FOR SELECT TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "clients_update" ON "public"."clients" FOR UPDATE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"())) WITH CHECK (("company_id" = "public"."get_current_company_id"()));



ALTER TABLE "public"."companies" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "company_admin_all" ON "public"."companies" TO "authenticated" USING (("id" IN ( SELECT "users"."company_id"
   FROM "public"."users"
  WHERE (("users"."id" = ( SELECT "auth"."uid"() AS "uid")) AND ("users"."role" = 'ADMIN'::"public"."user_role")))));



CREATE POLICY "company_select" ON "public"."companies" FOR SELECT TO "authenticated" USING (("id" = "public"."get_current_company_id"()));



ALTER TABLE "public"."materials" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "materials_delete" ON "public"."materials" FOR DELETE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "materials_insert" ON "public"."materials" FOR INSERT TO "authenticated" WITH CHECK (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "materials_select" ON "public"."materials" FOR SELECT TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "materials_update" ON "public"."materials" FOR UPDATE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"())) WITH CHECK (("company_id" = "public"."get_current_company_id"()));



ALTER TABLE "public"."quotes" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "quotes_delete" ON "public"."quotes" FOR DELETE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "quotes_insert" ON "public"."quotes" FOR INSERT TO "authenticated" WITH CHECK (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "quotes_select" ON "public"."quotes" FOR SELECT TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "quotes_update" ON "public"."quotes" FOR UPDATE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"())) WITH CHECK (("company_id" = "public"."get_current_company_id"()));



ALTER TABLE "public"."reports" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "reports_delete" ON "public"."reports" FOR DELETE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "reports_insert" ON "public"."reports" FOR INSERT TO "authenticated" WITH CHECK (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "reports_select" ON "public"."reports" FOR SELECT TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "reports_update" ON "public"."reports" FOR UPDATE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"())) WITH CHECK (("company_id" = "public"."get_current_company_id"()));



ALTER TABLE "public"."searches" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "searches_delete" ON "public"."searches" FOR DELETE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "searches_insert" ON "public"."searches" FOR INSERT TO "authenticated" WITH CHECK (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "searches_select" ON "public"."searches" FOR SELECT TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "searches_update" ON "public"."searches" FOR UPDATE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"())) WITH CHECK (("company_id" = "public"."get_current_company_id"()));



ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "users_admin_manage" ON "public"."users" TO "authenticated" USING (("company_id" IN ( SELECT "users_1"."company_id"
   FROM "public"."users" "users_1"
  WHERE (("users_1"."id" = ( SELECT "auth"."uid"() AS "uid")) AND ("users_1"."role" = 'ADMIN'::"public"."user_role")))));



CREATE POLICY "users_select_same_company" ON "public"."users" FOR SELECT TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



ALTER TABLE "public"."worksites" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "worksites_delete" ON "public"."worksites" FOR DELETE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "worksites_insert" ON "public"."worksites" FOR INSERT TO "authenticated" WITH CHECK (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "worksites_select" ON "public"."worksites" FOR SELECT TO "authenticated" USING (("company_id" = "public"."get_current_company_id"()));



CREATE POLICY "worksites_update" ON "public"."worksites" FOR UPDATE TO "authenticated" USING (("company_id" = "public"."get_current_company_id"())) WITH CHECK (("company_id" = "public"."get_current_company_id"()));



GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



REVOKE ALL ON FUNCTION "public"."get_current_company_id"() FROM PUBLIC;
GRANT ALL ON FUNCTION "public"."get_current_company_id"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_current_company_id"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "service_role";



GRANT ALL ON TABLE "public"."clients" TO "anon";
GRANT ALL ON TABLE "public"."clients" TO "authenticated";
GRANT ALL ON TABLE "public"."clients" TO "service_role";



GRANT ALL ON TABLE "public"."companies" TO "anon";
GRANT ALL ON TABLE "public"."companies" TO "authenticated";
GRANT ALL ON TABLE "public"."companies" TO "service_role";



GRANT ALL ON TABLE "public"."quotes" TO "anon";
GRANT ALL ON TABLE "public"."quotes" TO "authenticated";
GRANT ALL ON TABLE "public"."quotes" TO "service_role";



GRANT ALL ON TABLE "public"."searches" TO "anon";
GRANT ALL ON TABLE "public"."searches" TO "authenticated";
GRANT ALL ON TABLE "public"."searches" TO "service_role";



GRANT ALL ON TABLE "public"."users" TO "anon";
GRANT ALL ON TABLE "public"."users" TO "authenticated";
GRANT ALL ON TABLE "public"."users" TO "service_role";



GRANT ALL ON TABLE "public"."worksites" TO "anon";
GRANT ALL ON TABLE "public"."worksites" TO "authenticated";
GRANT ALL ON TABLE "public"."worksites" TO "service_role";



GRANT ALL ON TABLE "public"."company_stats" TO "anon";
GRANT ALL ON TABLE "public"."company_stats" TO "authenticated";
GRANT ALL ON TABLE "public"."company_stats" TO "service_role";



GRANT ALL ON TABLE "public"."materials" TO "anon";
GRANT ALL ON TABLE "public"."materials" TO "authenticated";
GRANT ALL ON TABLE "public"."materials" TO "service_role";



GRANT ALL ON TABLE "public"."reports" TO "anon";
GRANT ALL ON TABLE "public"."reports" TO "authenticated";
GRANT ALL ON TABLE "public"."reports" TO "service_role";



ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";







