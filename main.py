import socketio
import time
import ssl
import os
from supabase import create_client

# --- BYPASS DE SEGURIDAD SSL ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- CONFIGURACIÓN SEGURA ---
# Railway leerá estas variables de su propia configuración, no del código
URL_SUPABASE = os.getenv("SUPABASE_URL", "https://arpezfnlcdmbltcmctrv.supabase.co")
KEY_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not KEY_SERVICE_ROLE:
    print("❌ Error: No se encontró la llave 'SUPABASE_SERVICE_ROLE_KEY' en las variables.")

supabase = create_client(URL_SUPABASE, KEY_SERVICE_ROLE)
sio = socketio.Client(reconnection=True, reconnection_attempts=0, reconnection_delay=5)

@sio.on('serverDataExt')
def procesar_todo(data):
    print(f"📊 {time.strftime('%H:%M:%S')} - Procesando {len(data)} activos...")
    lote_completo = []
    for a in data:
        ticker = a.get("COD_SIMB")
        if not ticker: continue
        logo_url = f"https://bolsadecaracas.com/wp-content/themes/bvc/assets/img/logos/{ticker}.png"
        lote_completo.append({
            "symbol": ticker,
            "description": a.get("DESC_SIMB"),
            "logo_url": logo_url,
            "last_price": a.get("PRECIO"),
            "prev_close": a.get("PRECIO_ANT"),
            "open_price": a.get("PRECIO_APERT"),
            "high_price": a.get("PRECIO_MAX"),
            "low_price": a.get("PRECIO_MIN"),
            "avg_price": a.get("PRECIO_PROM"),
            "change_abs": a.get("VAR_ABS"),
            "change_pct": a.get("VAR_REL"),
            "volume": a.get("VOLUMEN"),
            "total_amount": a.get("MONTO_EFECTIVO"),
            "total_ops": a.get("TOT_OP_NEGOC"),
            "bid_price": a.get("COMPRA"),
            "ask_price": a.get("VENTA"),
            "status": a.get("ESTADO"),
            "market_segment": a.get("MERCADO"),
            "currency": a.get("MONEDA", "VES"),
            "last_update_bvc": a.get("HORA"),
            "updated_at": "now()"
        })

    try:
        supabase.table("bvc_market_data").upsert(lote_completo).execute()
        print(f"✅ Sincronización exitosa: {len(lote_completo)} registros.")
    except Exception as e:
        print(f"❌ Error en Supabase: {e}")

@sio.event
def connect():
    print("🚀 NODO EN LÍNEA: Conexión con Bolsa de Caracas establecida.")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Origin": "https://market.bolsadecaracas.com"
}

if __name__ == "__main__":
    try:
        sio.connect("https://market.bolsadecaracas.com", socketio_path='/socket.io/', transports=['websocket'], headers=headers)
        sio.wait()
    except Exception as e:
        print(f"🛑 Error crítico: {e}")