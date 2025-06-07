from supabase import create_client

SUPABASE_URL = "https://oziwendirtmqquvqkree.supabase.co/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im96aXdlbmRpcnRtcXF1dnFrcmVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcwOTA4MzksImV4cCI6MjA2MjY2NjgzOX0.PjysWhT8Y32PldsP3OsAefhiKfxjF8naRDhrrSddRVQ"  # Nunca expor publicamente


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_alerts(nome, emails, mensagem, lat=None, lon=None):
    for email in emails:
        data_to_insert = {
            "title": mensagem.split(':')[0] + " - " + nome, # Pega o tipo de alerta do início da mensagem
            "message": mensagem,
            "email_notification": email,
            "lat": lat,
            "long": lon
        }
        try:
            supabase.table("alerts").insert(data_to_insert).execute()
            print("\n✨ Dados enviados ao Supabase com sucesso! ✨")
            print("---------------------------------------------")
            for key, value in data_to_insert.items():
                print(f"  {key}: {value}")
            print("---------------------------------------------\n")
        except Exception as e:
            print(f"\n❌ Erro ao enviar dados ao Supabase: {e}\n")