from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()

# Cargar CSV
csv_path = os.path.join(os.path.dirname(__file__), "ventas_inventario_diario.csv")
df = pd.read_csv(csv_path, parse_dates=["fecha"])

def generar_alertas(tienda_id, producto_nombre, stock_actual, demanda_esperada, quiebre_stock, pedido_sugerido):
    alertas = []

    if pedido_sugerido == 0 and stock_actual < demanda_esperada:
        alertas.append({
            "alerta": "Stock bajo sin pedido programado",
            "nivel": "media"
        })

    if quiebre_stock:
        alertas.append({
            "alerta": "Quiebre de stock detectado",
            "nivel": "alta"
        })

    if pedido_sugerido > 100:  # ejemplo: exceso por error de predicción
        alertas.append({
            "alerta": "Pedido sugerido muy alto, verificar capacidad",
            "nivel": "media"
        })

    return alertas

@app.get("/predict")
def predict(tienda_id: str, producto_nombre: str):
    try:
        df_tp = df[
            (df['id_tienda'] == tienda_id) &
            (df['producto_nombre'] == producto_nombre)
        ].sort_values('fecha')

        if df_tp.empty or len(df_tp) < 5:
            return {"error": "Datos insuficientes para predicción"}

        media_ventas = df_tp.tail(14)['ventas_unidades'].mean()
        latest = df_tp.iloc[-1]

        stock_actual = int(latest['stock_actual'])
        lead_time = int(latest['lead_time_dias'])
        buffer = int(latest['buffer_seguridad'])
        quiebre_stock = bool(latest['quiebre_stock'])

        demanda_esperada = float(media_ventas * lead_time)
        pedido_sugerido = max(0, round(demanda_esperada - stock_actual + buffer))

        # Agente 3: generar alertas
        alertas = generar_alertas(
            tienda_id,
            producto_nombre,
            stock_actual,
            demanda_esperada,
            quiebre_stock,
            pedido_sugerido
        )

        return {
            "tienda": tienda_id,
            "producto": producto_nombre,
            "stock_actual": stock_actual,
            "lead_time_dias": lead_time,
            "buffer": buffer,
            "demanda_esperada_hasta_entrega": round(demanda_esperada, 2),
            "pedido_sugerido": int(pedido_sugerido),
            "alertas": alertas
        }

    except Exception as e:
        return {"error": str(e)}



