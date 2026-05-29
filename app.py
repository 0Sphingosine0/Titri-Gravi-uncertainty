import streamlit as st
import math

st.set_page_config(page_title="Estimasi Ketidakpastian Pengukuran", layout="wide")

st.title("🧪 Estimasi Ketidakpastian Pengukuran")
st.markdown("**Titrimetri & Gravimetri** — Politeknik AKA Bogor")
st.markdown("---")

metode = st.sidebar.radio(
    "Pilih Metode",
    ["⚗️ Titrimetri", "⚖️ Gravimetri"]
)

# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
SQRT3 = math.sqrt(3)
SQRT2 = math.sqrt(2)

def u_alat(U, k=SQRT3):
    return U / k

def u_temp(V_mL, delta_T, k=SQRT3, koef=2.1e-4):
    return (V_mL * delta_T * koef) / k

def u_volume(U_kal, V_mL, delta_T, koef=2.1e-4):
    u_k = u_alat(U_kal)
    u_t = u_temp(V_mL, delta_T, koef=koef)
    return math.sqrt(u_k**2 + u_t**2)

def u_bm(atoms: dict):
    """
    atoms = {simbol: (Ar, U, jumlah_atom)}
    returns (BM, mu_BM)
    """
    BM = sum(Ar * n for _, (Ar, _, n) in atoms.items())
    sum_sq = sum(n * (U / SQRT3)**2 for _, (_, U, n) in atoms.items())
    return BM, math.sqrt(sum_sq)

def format_result(nilai, u, satuan, desimal=4):
    return f"**({round(nilai, desimal)} ± {round(u, desimal)}) {satuan}**"

def section(title):
    st.markdown(f"#### {title}")

# ─────────────────────────────────────────────
# TITRIMETRI
# ─────────────────────────────────────────────
if metode == "⚗️ Titrimetri":
    jenis = st.sidebar.selectbox(
        "Jenis Analisis",
        [
            "Standarisasi NaOH (asam oksalat)",
            "Penetapan Kadar Asam Asetat",
            "Standarisasi HCl (boraks)",
        ]
    )

    # ── STANDARISASI NaOH ────────────────────
    if jenis == "Standarisasi NaOH (asam oksalat)":
        st.subheader("Standarisasi Larutan NaOH dengan Asam Oksalat")

        col1, col2 = st.columns(2)
        with col1:
            section("Data Primer")
            P   = st.number_input("Kemurnian asam oksalat (%)", value=99.0, step=0.1)
            W   = st.number_input("Bobot asam oksalat (mg)", value=629.7)
            VLT = st.number_input("Volume labu takar (mL)", value=100.0)
            VP  = st.number_input("Volume pipet (mL)", value=25.0)

            section("Data Titrasi")
            v1 = st.number_input("Volume titran ulangan 1 (mL)", value=24.7)
            v2 = st.number_input("Volume titran ulangan 2 (mL)", value=24.0)

        with col2:
            section("Data Sekunder (Ketidakpastian Alat)")
            U_neraca  = st.number_input("U kalibrasi neraca (mg)", value=2e-4, format="%.5f")
            U_buret   = st.number_input("U spek buret 50 mL (mL)", value=0.05)
            U_LT      = st.number_input("U spek labu takar 100 mL (mL)", value=0.05)
            U_pipet   = st.number_input("U spek pipet 25 mL (mL)", value=0.005)
            delta_T   = st.number_input("Perbedaan suhu ΔT (°C)", value=0.0)
            koef_muai = st.number_input("Koefisien muai air (°C⁻¹)", value=2.1e-4, format="%.6f")

        if st.button("🔬 Hitung Ketidakpastian"):
            VT = (v1 + v2) / 2
            BE = 63.03272  # mg/mgrek asam oksalat (tetap)

            # N NaOH
            N_NaOH = (P/100 * W * VP) / (BE * VLT * VT)

            st.markdown("---")
            st.subheader("📊 Hasil Perhitungan")
            st.write(f"Rata-rata volume titran (VT) = {VT:.4f} mL")
            st.write(f"BE asam oksalat = {BE} mg/mgrek")
            st.write(f"N NaOH = {N_NaOH:.7f} N")

            # Komponen ketidakpastian
            # a. Kemurnian
            mu_P = 1.0 / SQRT3  # U=1%

            # b. Bobot
            mu_W = math.sqrt(2) * (U_neraca / 2)

            # c. BE asam oksalat
            atoms_oks = {
                "H": (1.00794, 7e-5, 6),
                "C": (12.0107, 8e-4, 2),
                "O": (15.9994, 3e-4, 6),
            }
            _, mu_BE_BM = u_bm(atoms_oks)
            mu_BE = mu_BE_BM / 2  # dibagi valensi 2

            # d. Labu takar
            mu_VLT = u_volume(U_LT, VLT, delta_T, koef_muai)

            # e. Pipet
            mu_VP = u_volume(U_pipet, VP, delta_T, koef_muai)

            # f. Buret
            mu_VT = u_volume(U_buret, VT, delta_T, koef_muai)

            # Gabungkan (propagasi relatif)
            rel2 = (mu_P/P)**2 + (mu_W/W)**2 + (mu_BE/BE)**2 + \
                   (mu_VLT/VLT)**2 + (mu_VP/VP)**2 + (mu_VT/VT)**2
            mu_gab = N_NaOH * math.sqrt(rel2)
            U_exp  = 2 * mu_gab

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Komponen Ketidakpastian Baku:**")
                data = {
                    "Simbol": ["P", "W", "BE", "VLT", "VP", "VT"],
                    "Uraian": ["Kemurnian", "Bobot", "BE Oks", "Labu Takar", "Pipet", "Buret"],
                    "Nilai": [P, W, BE, VLT, VP, VT],
                    "µ(x)": [mu_P, mu_W, mu_BE, mu_VLT, mu_VP, mu_VT],
                    "µ(x)/x": [mu_P/P, mu_W/W, mu_BE/BE, mu_VLT/VLT, mu_VP/VP, mu_VT/VT],
                }
                import pandas as pd
                df = pd.DataFrame(data)
                df["(µ/x)²"] = df["µ(x)/x"] ** 2
                st.dataframe(df.set_index("Simbol").style.format("{:.6e}"), use_container_width=True)

            with col2:
                st.markdown("**Ketidakpastian Gabungan:**")
                st.write(f"∑(µ/x)² = {rel2:.8f}")
                st.write(f"µ gabungan N NaOH = {mu_gab:.7f} N")
                st.write(f"U (k=2, 95%) = {U_exp:.7f} N")
                st.markdown("---")
                N_rounded = round(N_NaOH, 4)
                U_rounded = round(U_exp, 3)
                st.success(f"**HASIL UJI:**  N NaOH = ({N_rounded} ± {U_rounded}) N")

    # ── KADAR ASAM ASETAT ────────────────────
    elif jenis == "Penetapan Kadar Asam Asetat":
        st.subheader("Penetapan Kadar Asam Asetat (CH₃COOH) dalam Cuka")

        col1, col2 = st.columns(2)
        with col1:
            section("Data Primer")
            VP1  = st.number_input("Volume pipet sampel cuka (mL)", value=5.0)
            VLT  = st.number_input("Volume labu takar (mL)", value=250.0)
            VP2  = st.number_input("Volume pipet larutan encer titrat (mL)", value=25.0)
            N_NaOH = st.number_input("Normalitas NaOH (N)", value=0.1025672445, format="%.7f")

            section("Data Titrasi")
            v1 = st.number_input("Volume buret ulangan 1 (mL)", value=18.9)
            v2 = st.number_input("Volume buret ulangan 2 (mL)", value=19.4)

        with col2:
            section("Data Sekunder")
            U_neraca = st.number_input("U kalibrasi neraca (g)", value=2e-4, format="%.5f")
            U_buret  = st.number_input("U spek buret 50 mL (mL)", value=0.05)
            U_LT     = st.number_input("U spek labu takar 250 mL (mL)", value=0.12)
            U_pip1   = st.number_input("U spek pipet 5 mL (mL)", value=0.01)
            U_pip2   = st.number_input("U spek pipet 25 mL (mL)", value=0.03)
            U_N      = st.number_input("U Normalitas NaOH (N)", value=2e-4, format="%.5f")
            delta_T  = st.number_input("Perbedaan suhu ΔT (°C)", value=0.0)
            koef_muai= st.number_input("Koefisien muai air (°C⁻¹)", value=2.1e-4, format="%.6f")

        if st.button("🔬 Hitung Ketidakpastian"):
            VB   = (v1 + v2) / 2
            BE   = 60.05196   # g/mol asam asetat
            Fp   = VLT / VP1  # faktor pengenceran

            # Kadar
            kadar = (VB * N_NaOH * BE * Fp) / (VP2 * 10)  # %b/v

            st.markdown("---")
            st.subheader("📊 Hasil Perhitungan")
            st.write(f"Rata-rata volume buret (VB) = {VB:.4f} mL")
            st.write(f"Faktor pengenceran (Fp) = {Fp}")
            st.write(f"Kadar CH₃COOH = {kadar:.6f} % b/v")

            # Komponen
            mu_VP1 = u_volume(U_pip1, VP1, delta_T, koef_muai)
            mu_VLT = u_volume(U_LT, VLT, delta_T, koef_muai)
            mu_VP2 = u_volume(U_pip2, VP2, delta_T, koef_muai)
            mu_VB  = u_volume(U_buret, VB, delta_T, koef_muai)
            mu_N   = U_N / SQRT3
            atoms_aa = {
                "H": (1.00794, 7e-5, 4),
                "C": (12.0107, 8e-4, 2),
                "O": (15.9994, 3e-4, 2),
            }
            _, mu_BE_BM = u_bm(atoms_aa)
            mu_BE  = mu_BE_BM / 1
            # replikasi duplo
            half_range = abs(v1 - v2) / 2
            mu_rep = half_range / SQRT2

            rel2 = (mu_VP1/VP1)**2 + (mu_VLT/VLT)**2 + (mu_VP2/VP2)**2 + \
                   (mu_VB/VB)**2 + (mu_N/N_NaOH)**2 + (mu_BE/BE)**2 + \
                   (mu_rep/kadar)**2 if kadar > 0 else 0

            mu_gab = kadar * math.sqrt(rel2)
            U_exp  = 2 * mu_gab

            col1, col2 = st.columns(2)
            with col1:
                import pandas as pd
                data = {
                    "Simbol": ["VP1", "VLT", "VP2", "VB", "N NaOH", "BE", "Replikasi"],
                    "Nilai": [VP1, VLT, VP2, VB, N_NaOH, BE, kadar],
                    "µ(x)": [mu_VP1, mu_VLT, mu_VP2, mu_VB, mu_N, mu_BE, mu_rep],
                }
                df = pd.DataFrame(data)
                df["µ(x)/x"] = df["µ(x)"] / df["Nilai"]
                df["(µ/x)²"] = df["µ(x)/x"] ** 2
                st.dataframe(df.set_index("Simbol").style.format("{:.6e}"), use_container_width=True)

            with col2:
                st.write(f"∑(µ/x)² = {rel2:.8f}")
                st.write(f"µ gabungan = {mu_gab:.6f} % b/v")
                st.write(f"U (k=2, 95%) = {U_exp:.6f} % b/v")
                st.markdown("---")
                st.success(f"**HASIL UJI:**  CH₃COOH = ({round(kadar,1)} ± {round(U_exp,1)}) % b/v")

    # ── STANDARISASI HCl ─────────────────────
    elif jenis == "Standarisasi HCl (boraks)":
        st.subheader("Standarisasi Larutan HCl dengan Boraks")

        col1, col2 = st.columns(2)
        with col1:
            section("Data Primer")
            P   = st.number_input("Kemurnian boraks (%)", value=101.25)
            W   = st.number_input("Bobot boraks (mg)", value=1508.0)
            VP  = st.number_input("Volume pipet boraks (mL)", value=25.0)
            VLT = st.number_input("Volume labu takar (mL)", value=100.0)

            section("Data Titrasi")
            v1 = st.number_input("Volume titran ulangan 1 (mL)", value=23.53)
            v2 = st.number_input("Volume titran ulangan 2 (mL)", value=23.55)

        with col2:
            section("Data Sekunder")
            U_neraca = st.number_input("U kalibrasi neraca (mg)", value=2e-4, format="%.5f")
            U_buret  = st.number_input("U spek buret 50 mL (mL)", value=0.05)
            U_LT     = st.number_input("U spek labu takar 100 mL (mL)", value=0.05)
            U_pipet  = st.number_input("U spek pipet 25 mL (mL)", value=0.005)
            delta_T  = st.number_input("Perbedaan suhu ΔT (°C)", value=0.0)
            koef_muai= st.number_input("Koefisien muai air", value=2.1e-4, format="%.6f")

        if st.button("🔬 Hitung Ketidakpastian"):
            VT   = (v1 + v2) / 2
            BE_boraks = 190.70 / 2  # mg/mgrek

            N_HCl = (P/100 * W * VP) / (BE_boraks * VLT * VT)

            st.markdown("---")
            st.subheader("📊 Hasil Perhitungan")
            st.write(f"Rata-rata VT = {VT:.4f} mL")
            st.write(f"BE boraks = {BE_boraks:.5f} mg/mgrek")
            st.write(f"N HCl = {N_HCl:.7f} N")

            mu_P   = 1.0 / SQRT3
            mu_W   = math.sqrt(2) * (U_neraca / 2)

            atoms_boraks = {
                "Na": (22.98977, 2e-5, 2),
                "B":  (10.811,   7e-4, 4),
                "O":  (15.9994,  3e-4, 7),
                "H":  (1.00794,  7e-5, 20),
            }
            BM_boraks, mu_BM_boraks = u_bm(atoms_boraks)
            mu_BE  = mu_BM_boraks / 2

            mu_VLT = u_volume(U_LT, VLT, delta_T, koef_muai)
            mu_VP  = u_volume(U_pipet, VP, delta_T, koef_muai)
            mu_VT  = u_volume(U_buret, VT, delta_T, koef_muai)

            rel2 = (mu_P/P)**2 + (mu_W/W)**2 + (mu_BE/BE_boraks)**2 + \
                   (mu_VLT/VLT)**2 + (mu_VP/VP)**2 + (mu_VT/VT)**2
            mu_gab = N_HCl * math.sqrt(rel2)
            U_exp  = 2 * mu_gab

            col1, col2 = st.columns(2)
            with col1:
                import pandas as pd
                data = {
                    "Simbol": ["P", "W", "BE", "VLT", "VP", "VT"],
                    "Nilai": [P, W, BE_boraks, VLT, VP, VT],
                    "µ(x)": [mu_P, mu_W, mu_BE, mu_VLT, mu_VP, mu_VT],
                }
                df = pd.DataFrame(data)
                df["µ(x)/x"] = df["µ(x)"] / df["Nilai"]
                df["(µ/x)²"] = df["µ(x)/x"] ** 2
                st.dataframe(df.set_index("Simbol").style.format("{:.6e}"), use_container_width=True)
            with col2:
                st.write(f"µ gabungan = {mu_gab:.7f} N")
                st.write(f"U (k=2, 95%) = {U_exp:.7f} N")
                st.markdown("---")
                st.success(f"**HASIL UJI:**  N HCl = ({round(N_HCl,4)} ± {round(U_exp,3)}) N")


# ─────────────────────────────────────────────
# GRAVIMETRI
# ─────────────────────────────────────────────
elif metode == "⚖️ Gravimetri":
    jenis = st.sidebar.selectbox(
        "Jenis Analisis",
        [
            "Kadar Air",
            "Kadar Abu",
            "Kadar Sulfat (Garam Glauber)",
        ]
    )

    # ── KADAR AIR ────────────────────────────
    if jenis == "Kadar Air":
        st.subheader("Penetapan Kadar Air dalam Tepung Terigu")

        col1, col2 = st.columns(2)
        with col1:
            section("Data Penimbangan")
            W0 = st.number_input("Wadah kosong W₀ (g)", value=18.5231, format="%.4f")
            W1 = st.number_input("Wadah + sampel sebelum W₁ (g)", value=20.5287, format="%.4f")
            W2 = st.number_input("Wadah + sampel sesudah W₂ (g)", value=20.2503, format="%.4f")
        with col2:
            section("Data Kalibrasi Neraca")
            U_kal = st.number_input("U kalibrasi neraca (g)", value=2e-4, format="%.5f")

        if st.button("🔬 Hitung Ketidakpastian"):
            bobot_awal   = W1 - W0
            bobot_akhir  = W2 - W0
            bobot_uap    = bobot_awal - bobot_akhir
            kadar        = (bobot_uap / bobot_awal) * 100

            st.markdown("---")
            st.subheader("📊 Hasil Perhitungan")
            st.write(f"(W₁-W₀) = {bobot_awal:.4f} g")
            st.write(f"(W₂-W₀) = {bobot_akhir:.4f} g")
            st.write(f"Bobot teruapkan = {bobot_uap:.4f} g")
            st.write(f"Kadar Air = {kadar:.8f} %")

            mu_kal       = U_kal / 2
            mu_bobot_uap = math.sqrt(2) * mu_kal * math.sqrt(2)
            mu_bobot_uap = 2 * mu_kal   # √(µ²+µ²) = √2·µ  ×2 karena 2 timbang
            mu_bobot_awal= math.sqrt(2) * mu_kal

            rel2   = (mu_bobot_uap/bobot_uap)**2 + (mu_bobot_awal/bobot_awal)**2
            mu_Y   = kadar * math.sqrt(rel2)
            U_exp  = 2 * mu_Y

            col1, col2 = st.columns(2)
            with col1:
                import pandas as pd
                data = {
                    "Simbol": ["(W₁-W₀)-(W₂-W₀)", "(W₁-W₀)"],
                    "Uraian": ["Bobot teruapkan", "Bobot sampel awal"],
                    "Nilai (g)": [bobot_uap, bobot_awal],
                    "µ(x) (g)": [mu_bobot_uap, mu_bobot_awal],
                }
                df = pd.DataFrame(data)
                df["µ(x)/x"] = df["µ(x) (g)"] / df["Nilai (g)"]
                df["(µ/x)²"] = df["µ(x)/x"] ** 2
                st.dataframe(df.set_index("Simbol").style.format("{:.8f}"), use_container_width=True)
            with col2:
                st.write(f"µ gabungan = {mu_Y:.8f} %")
                st.write(f"U (k=2, 95%) = {U_exp:.8f} %")
                st.markdown("---")
                st.success(f"**HASIL UJI:**  Kadar Air = ({round(kadar,2)} ± {round(U_exp,2)}) %")

    # ── KADAR ABU ────────────────────────────
    elif jenis == "Kadar Abu":
        st.subheader("Penetapan Kadar Abu dalam Tepung Terigu")

        col1, col2 = st.columns(2)
        with col1:
            section("Data Penimbangan")
            W0 = st.number_input("Wadah kosong W₀ (g)", value=28.2648, format="%.4f")
            W1 = st.number_input("Wadah + sampel W₁ (g)", value=31.2648, format="%.4f")
            W2 = st.number_input("Wadah + abu W₂ (g)", value=28.2783, format="%.4f")
        with col2:
            section("Data Kalibrasi Neraca")
            U_kal = st.number_input("U kalibrasi neraca (g)", value=2e-4, format="%.5f")

        if st.button("🔬 Hitung Ketidakpastian"):
            bobot_sampel = W1 - W0
            bobot_abu    = W2 - W0
            kadar        = (bobot_abu / bobot_sampel) * 100

            st.markdown("---")
            st.subheader("📊 Hasil Perhitungan")
            st.write(f"(W₁-W₀) bobot sampel = {bobot_sampel:.4f} g")
            st.write(f"(W₂-W₀) bobot abu    = {bobot_abu:.4f} g")
            st.write(f"Kadar Abu = {kadar:.8f} %")

            mu_kal       = U_kal / 2
            mu_bs        = math.sqrt(2) * mu_kal
            mu_ba        = math.sqrt(2) * mu_kal

            rel2   = (mu_ba/bobot_abu)**2 + (mu_bs/bobot_sampel)**2
            mu_Y   = kadar * math.sqrt(rel2)
            U_exp  = 2 * mu_Y

            col1, col2 = st.columns(2)
            with col1:
                import pandas as pd
                data = {
                    "Simbol": ["(W₁-W₀)", "(W₂-W₀)"],
                    "Uraian": ["Bobot sampel", "Bobot abu"],
                    "Nilai (g)": [bobot_sampel, bobot_abu],
                    "µ(x) (g)": [mu_bs, mu_ba],
                }
                df = pd.DataFrame(data)
                df["µ(x)/x"] = df["µ(x) (g)"] / df["Nilai (g)"]
                df["(µ/x)²"] = df["µ(x)/x"] ** 2
                st.dataframe(df.set_index("Simbol").style.format("{:.8f}"), use_container_width=True)
            with col2:
                st.write(f"µ gabungan = {mu_Y:.8f} %")
                st.write(f"U (k=2, 95%) = {U_exp:.8f} %")
                st.markdown("---")
                st.success(f"**HASIL UJI:**  Kadar Abu = ({round(kadar,2)} ± {round(U_exp,2)}) %")

    # ── KADAR SULFAT ─────────────────────────
    elif jenis == "Kadar Sulfat (Garam Glauber)":
        st.subheader("Penetapan Kadar Sulfat dalam Garam Glauber")

        col1, col2 = st.columns(2)
        with col1:
            section("Data Penimbangan")
            W0 = st.number_input("Wadah kosong W₀ (g)", value=30.4492, format="%.4f")
            W1 = st.number_input("Bobot sampel garam glauber W₁ (g)", value=30.9515, format="%.4f")
            W2 = st.number_input("Wadah + residu BaSO₄ W₂ (g)", value=31.2573, format="%.4f")
        with col2:
            section("Data Kalibrasi & Bobot Atom")
            U_kal = st.number_input("U kalibrasi neraca (g)", value=2e-4, format="%.5f")
            st.markdown("*(Bobot atom diambil dari IUPAC, dapat diubah)*")
            Ar_S  = st.number_input("Ar Sulfur", value=32.065, format="%.3f")
            Ar_O  = st.number_input("Ar Oksigen", value=15.9994, format="%.4f")
            Ar_Ba = st.number_input("Ar Barium", value=137.327, format="%.3f")

        if st.button("🔬 Hitung Ketidakpastian"):
            bobot_sampel = W1 - W0
            bobot_BaSO4  = W2 - W0
            BM_SO4  = Ar_S + 4*Ar_O
            BM_BaSO4= Ar_Ba + Ar_S + 4*Ar_O
            kadar   = (bobot_BaSO4 / bobot_sampel) * (BM_SO4 / BM_BaSO4) * 100

            st.markdown("---")
            st.subheader("📊 Hasil Perhitungan")
            st.write(f"Bobot sampel = {bobot_sampel:.4f} g")
            st.write(f"Bobot residu BaSO₄ = {bobot_BaSO4:.4f} g")
            st.write(f"BM SO₄ = {BM_SO4:.4f} | BM BaSO₄ = {BM_BaSO4:.4f}")
            st.write(f"Kadar SO₄ = {kadar:.6f} %")

            mu_kal = U_kal / 2
            mu_W1  = math.sqrt(2) * mu_kal
            mu_W2  = math.sqrt(2) * mu_kal

            # BM SO4
            atoms_SO4 = {
                "S": (Ar_S, 0.005, 1),
                "O": (Ar_O, 3e-4, 4),
            }
            _, mu_BM_SO4 = u_bm(atoms_SO4)

            # BM BaSO4
            atoms_BaSO4 = {
                "Ba": (Ar_Ba, 0.007, 1),
                "S":  (Ar_S,  0.005, 1),
                "O":  (Ar_O,  3e-4,  4),
            }
            _, mu_BM_BaSO4 = u_bm(atoms_BaSO4)

            rel2 = (mu_W1/bobot_sampel)**2 + (mu_W2/bobot_BaSO4)**2 + \
                   (mu_BM_SO4/BM_SO4)**2 + (mu_BM_BaSO4/BM_BaSO4)**2
            mu_Y = kadar * math.sqrt(rel2)
            U_exp= 2 * mu_Y

            col1, col2 = st.columns(2)
            with col1:
                import pandas as pd
                data = {
                    "Simbol": ["(W₁-W₀)", "(W₂-W₀)", "BM SO₄", "BM BaSO₄"],
                    "Nilai": [bobot_sampel, bobot_BaSO4, BM_SO4, BM_BaSO4],
                    "µ(x)": [mu_W1, mu_W2, mu_BM_SO4, mu_BM_BaSO4],
                }
                df = pd.DataFrame(data)
                df["µ(x)/x"] = df["µ(x)"] / df["Nilai"]
                df["(µ/x)²"] = df["µ(x)/x"] ** 2
                st.dataframe(df.set_index("Simbol").style.format("{:.8f}"), use_container_width=True)
            with col2:
                st.write(f"µ gabungan = {mu_Y:.6f} %")
                st.write(f"U (k=2, 95%) = {U_exp:.6f} %")
                st.markdown("---")
                st.success(f"**HASIL UJI:**  Kadar SO₄ = ({round(kadar,2)} ± {round(U_exp,2)}) %")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("📌 Estimasi ketidakpastian mengacu pada GUM (Guide to the Expression of Uncertainty in Measurement) | k=2, tingkat kepercayaan 95%")
