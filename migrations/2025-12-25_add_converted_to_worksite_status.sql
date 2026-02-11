-- Migration: Ajouter le statut CONVERTED_TO_WORKSITE à l'enum quote_status
-- Date: 2025-12-25
-- Description: Permet de marquer un devis comme converti en chantier

-- Ajouter la nouvelle valeur à l'enum
ALTER TYPE public.quote_status ADD VALUE IF NOT EXISTS 'CONVERTED_TO_WORKSITE';
