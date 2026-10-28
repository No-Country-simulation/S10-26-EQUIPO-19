import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

raw_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_KEY", "")

supabase_url = raw_url.replace("/rest/v1/", "").replace("/rest/v1", "").rstrip("/")

supabase: Client | None = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo conectar a Supabase: {e}")
        supabase = None
else:
    print("⚠️ Advertencia: Variables de entorno SUPABASE_URL o SUPABASE_KEY no configuradas.")


def get_supabase_client() -> Client | None:
    """Retorna la instancia del cliente de Supabase para realizar consultas."""
    return supabase