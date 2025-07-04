from fastapi import FastAPI
import pandas as pd

app = FastAPI()
df = pd.read_csv("ventas_inventario_diario.csv", parse_dates=["fecha"])

@app.get("/predict")
def predict(tienda_id: str, producto_nombre: str):
    df_tp = df[
        (df['id_tienda'] == tienda_id) &
        (df['producto_nombre'] == producto_nombre)
    ].sort_values('fecha')

    if df_tp.empty or len(df_tp) < 5:
        return {"error": "Datos insuficientes para predicción"}

    media_ventas = df_tp.tail(14)['ventas_unidades'].mean()
    latest = df_tp.iloc[-1]
    stock_actual = latest['stock_actual']
    lead_time = latest['lead_time_dias']
    buffer = latest['buffer_seguridad']
    demanda_esperada = media_ventas * lead_time
    pedido_sugerido = max(0, round(demanda_esperada - stock_actual + buffer))

    return {
        "tienda": tienda_id,
        "producto": producto_nombre,
        "stock_actual": stock_actual,
        "lead_time_dias": lead_time,
        "buffer": buffer,
        "demanda_esperada_hasta_entrega": round(demanda_esperada, 2),
        "pedido_sugerido": pedido_sugerido
    }
