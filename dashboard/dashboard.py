import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

# ==========================================
# 1. CONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Smart Financial Monitoring",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_theme(style="whitegrid")

# ==========================================
# 2. LOAD & CACHE 4 MASTER DATASET
# ==========================================
@st.cache_data
def load_all_datasets():
    # 1. Dataset Transaksi
    df_transaksi = pd.read_csv('dashboard/dataset_transaksi.csv')
    df_transaksi['transaction_date'] = pd.to_datetime(df_transaksi['transaction_date'])
    
    # 2. Dataset Pengguna
    df_users = pd.read_csv('dashboard/dataset_pengguna.csv')
    
    # 3. Dataset Anggaran
    df_budgets = pd.read_csv('dashboard/dataset_budgets.csv')
    
    # 4. Dataset Tantangan
    df_challenges = pd.read_csv('dashboard/dataset_challenge.csv')
    
    return df_transaksi, df_users, df_budgets, df_challenges

df_transaksi, df_users, df_budgets, df_challenges = load_all_datasets()

# ==========================================
# 3. SIDEBAR NAVIGATION & SIMULASI LOGIN
# ==========================================
st.sidebar.title("💳 Smart Finance App")

# Simulasi "Login" Pengguna
user_list = df_users['user_id'].tolist()
logged_in_user = st.sidebar.selectbox("👤 Simulasi Login Sebagai:", user_list)

# Mengambil profil user yang sedang login
user_profile = df_users[df_users['user_id'] == logged_in_user].iloc[0]

st.sidebar.markdown("---")
st.sidebar.markdown("### Profil Pengguna")
st.sidebar.markdown(f"**Avatar:** {user_profile['avatar_aktif']}")
st.sidebar.markdown(f"**Pendapatan:** Rp {user_profile['pendapatan_bulanan']:,.0f}")

# Menampilkan Badge Premium jika True
if user_profile['status_premium']:
    st.sidebar.success("👑 Akun Premium Aktif")
else:
    st.sidebar.info("👤 Akun Regular")
    
st.sidebar.markdown(f"**Tema Tampilan:** {user_profile['tema_aktif']}")
st.sidebar.markdown(f"**Group A/B Test:** Group {user_profile['ab_test_group']}")

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Pilih Menu/Fitur:",
    ["📊 Ringkasan Eksekutif", "📈 Analisis Pengeluaran (Global)", "🤖 Smart AI Recommendation (Personal)", "🏆 Financial Challenge Mode (Personal)"]
)

# ==========================================
# MENU 1: RINGKASAN EKSEKUTIF
# ==========================================
if menu == "📊 Ringkasan Eksekutif":
    st.title("📊 Ringkasan Eksekutif Finansial")
    st.markdown("Ikhtisar data dari seluruh ekosistem aplikasi.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transaksi", f"{len(df_transaksi):,}")
    with col2:
        st.metric("Total Perputaran Dana", f"Rp {df_transaksi['amount'].sum():,.0f}")
    with col3:
        st.metric("Pengguna Aktif", f"{len(df_users):,}")
    with col4:
        total_anomaly = df_transaksi['is_anomaly'].sum()
        pct_anomaly = (total_anomaly / len(df_transaksi)) * 100
        st.metric("Deteksi Anomali", f"{total_anomaly} trans.", delta=f"{pct_anomaly:.1f}% dari total", delta_color="inverse")

    st.markdown("---")
    st.subheader("💡 Fokus Pengembangan Solusi")
    st.write("Sistem dirancang untuk menyelesaikan masalah pencatatan manual, kesulitan memantau transaksi mikro, dan kurangnya kontrol pengeluaran Generasi Z.")

# ==========================================
# MENU 2: ANALISIS PENGELUARAN (EDA GLOBAL)
# ==========================================
elif menu == "📈 Analisis Pengeluaran (Global)":
    st.title("📈 Analisis Pengeluaran Mendalam (Data Global)")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Kategori Kumulatif", "Waktu Transaksi", "Tren Harian", "Lokasi vs Nominal", "Analisis Cashback", "Sebaran Transaksi"
    ])
    
    with tab1:
        st.subheader("Di mana Uang Paling Banyak Dihabiskan?")
        cat_nominal = df_transaksi.groupby('product_category')['amount'].sum().reset_index().sort_values(by='amount', ascending=False)
        total_all = cat_nominal['amount'].sum()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=cat_nominal, x='amount', y='product_category', palette='viridis', ax=ax)
        for p in ax.patches:
            width = p.get_width()
            pct = (width / total_all) * 100
            ax.text(width + (total_all * 0.01), p.get_y() + p.get_height() / 2, f'{pct:.1f}%', va='center', fontsize=9)
        plt.title('Total Pengeluaran Kumulatif per Kategori', fontsize=12)
        sns.despine()
        st.pyplot(fig)

    with tab2:
        st.subheader("Kapan Pengguna Paling Sering Bertransaksi?")
        order_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = df_transaksi.groupby(['day_name', 'hour']).size().unstack(fill_value=0).reindex(order_days)
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        sns.heatmap(heatmap_data, cmap='YlOrRd', ax=ax2)
        plt.title('Intensitas Waktu Transaksi (Hari vs Jam)', fontsize=12)
        st.pyplot(fig2)

    with tab3:
        st.subheader("Bagaimana Tren Pengeluaran Harian?")
        daily_spend = df_transaksi.groupby('date_only')['amount'].sum().reset_index()
        daily_spend_chart = daily_spend.set_index('date_only')
        st.line_chart(daily_spend_chart['amount'], color="#DC143C")

    with tab4:
        st.subheader("Sebaran Pengeluaran Berdasarkan Lokasi")
        geo_spend = df_transaksi.groupby('location').agg({'amount': 'sum', 'user_id': 'nunique'}).rename(columns={'amount': 'Total_Pengeluaran'}).sort_values(by='Total_Pengeluaran', ascending=False)
        col_tabel, col_grafik = st.columns([1, 2])
        with col_tabel:
            st.dataframe(geo_spend)
        with col_grafik:
            fig4, ax4 = plt.subplots(figsize=(8, 5))
            sns.barplot(x=geo_spend.index, y=geo_spend['Total_Pengeluaran'], palette='magma', ax=ax4)
            st.pyplot(fig4)

    with tab5:
        st.subheader("Merchant dengan Cashback Terbaik")
        top_merchants = df_transaksi['merchant_name'].value_counts().head(10).index
        df_top_merchants = df_transaksi[df_transaksi['merchant_name'].isin(top_merchants)]
        fig5, ax5 = plt.subplots(figsize=(12, 6))
        sns.barplot(data=df_top_merchants, x='cashback', y='merchant_name', estimator=np.mean, palette='coolwarm', ax=ax5)
        st.pyplot(fig5)

    with tab6:
        st.subheader("Deteksi Outlier/Anomali Transaksi")
        if 'is_statistical_outlier' in df_transaksi.columns:
            fig6, ax6 = plt.subplots(figsize=(14, 6))
            sns.scatterplot(data=df_transaksi, x='transaction_date', y='amount', hue='is_statistical_outlier', palette={False: 'gray', True: 'red'}, alpha=0.6, ax=ax6)
            st.pyplot(fig6)
        else:
            st.warning("Kolom 'is_statistical_outlier' tidak ditemukan.")

# ==========================================
# MENU 3: SMART AI RECOMMENDATION (PERSONAL)
# ==========================================
elif menu == "🤖 Smart AI Recommendation (Personal)":
    st.title(f"🤖 Smart AI Recommendation")
    st.markdown(f"Insight personal khusus untuk **{logged_in_user}**.")
    
    # 1. Cek Anggaran/Target Tabungan User dari Budgets Data
    user_budget_data = df_budgets[df_budgets['user_id'] == logged_in_user]
    
    if user_budget_data.empty:
        st.warning("Anda belum mengatur Target Tabungan (Saving Plan). Silakan atur di menu pengaturan.")
    else:
        target_savings = user_budget_data.iloc[0]['target_tabungan']
        st.info(f"🎯 Target Tabungan Anda bulan ini: **Rp {target_savings:,.0f}**")
        st.markdown("---")
        
        # 2. Cek Riwayat Pengeluaran Tersier
        user_trans = df_transaksi[df_transaksi['user_id'] == logged_in_user]
        tertiary_spend = user_trans[user_trans['is_discretionary'] == True].groupby('product_category')['amount'].sum().sort_values(ascending=False)
        
        st.subheader("📋 Analisis Pengeluaran Tersier (Discretionary)")
        
        if len(tertiary_spend) > 0:
            total_tertiary = tertiary_spend.sum()
            st.write(f"Total pengeluaran yang bisa dihemat: **Rp {total_tertiary:,.0f}**")
            
            if total_tertiary >= target_savings:
                st.success("✅ Target tabungan Anda realistis! Berikut rencana optimasi otomatis dari AI:")
                savings_accumulated = 0
                for cat, amount_val in tertiary_spend.items():
                    cut = amount_val * 0.20  # Potong 20%
                    savings_accumulated += cut
                    st.markdown(f"* **Batasi {cat}:** Kurangi sebesar 20% (Potensi Hemat: **Rp {cut:,.0f}**)")
                    if savings_accumulated >= target_savings:
                        break
            else:
                st.warning("⚠️ Pengeluaran sekunder Anda terlalu kecil untuk menutupi tingginya target tabungan. Cari tambahan penghasilan (Income).")
        else:
            st.info("Anda belum memiliki pengeluaran sekunder/tersier yang tercatat bulan ini. Pertahankan!")

# ==========================================
# MENU 4: FINANCIAL CHALLENGE MODE (PERSONAL)
# ==========================================
elif menu == "🏆 Financial Challenge Mode (Personal)":
    st.title("🏆 Financial Challenge Mode")
    st.markdown(f"Pelacakan tantangan aktif untuk **{logged_in_user}**.")
    
    # 1. Cek Tantangan yang Diikuti User dari Challenges Data
    user_challenges = df_challenges[df_challenges['user_id'] == logged_in_user]
    
    if user_challenges.empty:
        st.info("Anda tidak sedang mengikuti tantangan finansial apapun bulan ini. Berani mencoba?")
    else:
        st.subheader("Status Tantangan Anda:")
        
        # Mengevaluasi setiap tantangan yang diikuti user secara dinamis
        for _, row in user_challenges.iterrows():
            tipe = row['tipe_tantangan']
            status = row['status_tantangan']
            
            # Pengecekan real-time ke tabel transaksi
            user_trans = df_transaksi[df_transaksi['user_id'] == logged_in_user]
            
            if tipe == "No Midnight Spending Challenge":
                pelanggaran = len(user_trans[user_trans['is_midnight'] == True])
                if pelanggaran > 0:
                    st.error(f"❌ **{tipe}**: GAGAL. Terdeteksi {pelanggaran} transaksi di jam larut malam.")
                else:
                    st.success(f"✅ **{tipe}**: BERHASIL! Belum ada pelanggaran.")
                    
            elif tipe == "No Coffee Challenge":
                pelanggaran_kopi = len(user_trans[user_trans['product_category'] == 'Coffee Shop'])
                if pelanggaran_kopi > 0:
                    total_habis = user_trans[user_trans['product_category'] == 'Coffee Shop']['amount'].sum()
                    st.error(f"❌ **{tipe}**: GAGAL. Anda jajan kopi sebanyak {pelanggaran_kopi} kali (Total Rp {total_habis:,.0f}).")
                else:
                    st.success(f"✅ **{tipe}**: BERHASIL! Anda menahan godaan kopi dengan sangat baik.")
