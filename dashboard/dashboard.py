import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(layout="wide")
st.markdown(
    """
    <h1 style='text-align: center;'>
        📊 Dashboard Pelanggan dan RFM
    </h1>
    """, 
    unsafe_allow_html=True
)

main_df = pd.read_csv('dashboard/main_data.csv')

st.header('Kalkulasi Berdasarkan Metrik')
options = ['rata-rata', 'total']
selected_metric = st.selectbox("Pilih Opsi Metrik:", options)

if selected_metric == 'rata-rata':
    metric = 'mean'

else:
    metric = 'sum'

# 3. Create 4 Streamlit Columns
col1, col2, col3 = st.columns(3)

with col1:

    st.header(f'{selected_metric} jumlah transaksi per user id di top 5 negara bagian terpadat')
    negara_aktif = main_df.groupby('customer_state')\
                             .agg(jumlah_transaksi=('customer_id', 'count'))\
                             .reset_index()\
                             .sort_values('jumlah_transaksi',
                                          ascending=False)\
                             ['customer_state'].head().tolist()
    
    df = main_df[main_df['customer_state'].isin(negara_aktif)]
    df = df.groupby(by=['customer_state', 'customer_id'])\
            .agg(metrik=('payment_value', 'sum'))\
            .reset_index()\
            .groupby('customer_state')\
            .agg({'metrik':metric})\
            .reset_index()\
            .sort_values('metrik',
                        ascending=False)

    bars = alt.Chart(df)\
                .mark_bar(color='#5dade2').encode(
                            x=alt.X('customer_state:N', sort='-y'), # Sort by value descending
                            y=alt.Y('metrik:Q')
                        )

    text = bars.mark_text(
                    align='center',
                    baseline='middle',
                    dy=-10  # Nudges the text 10 pixels above the bar
                ).encode(
                    text='metrik:Q'
                )

    chart = (bars + text).properties(
                            width=400,
                            height=400
                        ).interactive()

    st.altair_chart(chart, use_container_width=True)

with col2:

    st.header(f'{selected_metric} jumlah transaksi per user id di bagian pesisir vs pedalaman')
    coastal_states = ['SP', 'PR', 'RJ', 'RS', 'SC', 'ES', 'BA', 'PE', 'AL']
    inland_states = ['GO', 'MG', 'DF', 'MT', 'MS']

    df = main_df[['customer_id', 'customer_state', 'payment_value']]
    df['wilayah'] = df['customer_state'].apply(lambda x: 'Pesisir' if x in coastal_states else 'Pedalaman')
    df = df.groupby(by=['wilayah', 'customer_id'])\
            .agg(metrik=('payment_value', 'sum'))\
            .reset_index()\
            .groupby('wilayah')\
            .agg(metrik=('metrik', metric))\
            .reset_index()
    

    bars = alt.Chart(df)\
                .mark_bar(color='#5dade2').encode(
                            x=alt.X('wilayah:N', sort='-y'), # Sort by value descending
                            y=alt.Y('metrik:Q')
                        )

    text = bars.mark_text(
                    align='center',
                    baseline='middle',
                    dy=-10  # Nudges the text 10 pixels above the bar
                ).encode(
                    text='metrik:Q'
                )

    chart = (bars + text).properties(
                            width=500,
                            height=450
                        ).interactive()

    st.altair_chart(chart, use_container_width=True)

with col3:

    st.header(f'Top 5 negara bagian dengan frekuensi terrendah namun dengan {selected_metric} tertinggi')
    df = main_df.groupby('customer_state')\
                .agg(frequency=('customer_id', 'count'),
                     metrik=('payment_value', metric))\
                .reset_index()\
                .sort_values(by=['metrik', 'frequency'],
                            ascending=[False, True])\
                .head()
    

    bars = alt.Chart(df)\
                .mark_bar(color='#5dade2').encode(
                            x=alt.X('customer_state:N', sort='-y'), # Sort by value descending
                            y=alt.Y('metrik:Q')
                        )

    text = bars.mark_text(
                    align='center',
                    baseline='middle',
                    dy=-10  # Nudges the text 10 pixels above the bar
                ).encode(
                    text='metrik:Q'
                )

    chart = (bars + text).properties(
                            width=400,
                            height=400
                        ).interactive()

    st.altair_chart(chart, use_container_width=True)

st.header(f'Visualisasi RFM pelanggan berdasarkan 2 metrik')

option_1 = ['Recency', 'Frequency', 'Monetary']
rfm_option_1 = st.selectbox("Select a Segment to Highlight:", option_1)

option_2 = [i for i in option_1 if i != rfm_option_1]
rfm_option_2 = st.selectbox("Select a Segment to Highlight:", option_2)

df = main_df.groupby('Segment')\
            .agg(Recency=('recency', 'mean'),
                 Frequency=('frequency', 'mean'),
                 Monetary=('monetary', 'mean'),
                 customer_count=('customer_id', 'count'))\
            .reset_index()

bubble_chart = alt.Chart(df).mark_circle().encode(
    x=f'{rfm_option_1}:Q',
    y=f'{rfm_option_2}:Q',
    size='customer_count:Q',
    color='Segment:N',
    tooltip=[
        alt.Tooltip('Segment:N', title='Customer Segment'),
        alt.Tooltip(f'{rfm_option_1}:Q', title=f'Avg {rfm_option_1}'),
        alt.Tooltip(f'{rfm_option_2}:Q', title=f'Avg {rfm_option_2}')
    ]
).properties(
    width="container",
    height=500,
    title="Interactive RFM Segment Quadrants"
).interactive()

final_chart = (bubble_chart)

st.altair_chart(final_chart, use_container_width=True)

st.header(f'Visualisasi total penjualan di seluruh negara bagian')
df = main_df.groupby('customer_state')\
            .agg(total_penjualan=('price', 'sum'))\
            .sort_values('total_penjualan',
                            ascending=False)\
            .reset_index()

bars = alt.Chart(df)\
            .mark_bar(color='#5dade2').encode(
                        x=alt.X('customer_state:N', sort='-y'), # Sort by value descending
                        y=alt.Y('total_penjualan:Q')
                    )

text = bars.mark_text(
                align='center',
                baseline='middle',
                dy=-10  # Nudges the text 10 pixels above the bar
            ).encode(
                text='total_penjualan:Q'
            )

chart = (bars + text).properties(
                        width=800,
                        height=500
                    ).interactive()

st.altair_chart(chart, use_container_width=True)

