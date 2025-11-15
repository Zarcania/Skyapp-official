-- Create invitations table for company invitations management
CREATE TABLE IF NOT EXISTS public.invitations (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL PRIMARY KEY,
    company_id uuid NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    email text NOT NULL,
    role public.user_role NOT NULL,
    invited_by uuid REFERENCES public.users(id) ON DELETE SET NULL,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'expired')),
    token text UNIQUE NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Add index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_invitations_email ON public.invitations(email);

-- Add index on token for validation
CREATE INDEX IF NOT EXISTS idx_invitations_token ON public.invitations(token);

-- Add index on company_id for filtering
CREATE INDEX IF NOT EXISTS idx_invitations_company_id ON public.invitations(company_id);

-- Add trigger for updated_at
CREATE TRIGGER update_invitations_updated_at 
    BEFORE UPDATE ON public.invitations 
    FOR EACH ROW 
    EXECUTE FUNCTION public.update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view invitations for their company
CREATE POLICY "Users can view company invitations" 
    ON public.invitations 
    FOR SELECT 
    USING (company_id = public.get_current_company_id());

-- Policy: Users can insert invitations for their company
CREATE POLICY "Users can create company invitations" 
    ON public.invitations 
    FOR INSERT 
    WITH CHECK (company_id = public.get_current_company_id());

-- Policy: Users can update invitations for their company
CREATE POLICY "Users can update company invitations" 
    ON public.invitations 
    FOR UPDATE 
    USING (company_id = public.get_current_company_id());

-- Policy: Users can delete invitations for their company
CREATE POLICY "Users can delete company invitations" 
    ON public.invitations 
    FOR DELETE 
    USING (company_id = public.get_current_company_id());

-- Grant permissions
GRANT ALL ON public.invitations TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.invitations TO authenticated;
GRANT SELECT ON public.invitations TO anon;
