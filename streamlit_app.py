import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
import time

# ======================================
# 🔐 SENHA DO APP (ANTES DE QUALQUER COISA)
# ======================================

SENHA_CORRETA = "CCB@2026_espacoinfantil"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    senha_digitada = st.text_input(
        "🔐 Digite a senha para acessar o formulário:",
        type="password"
    )

    if senha_digitada == SENHA_CORRETA:
        st.session_state.autenticado = True
        st.success("✅ Acesso autorizado!")
        time.sleep(1.2)
        st.rerun()
    elif senha_digitada:
        st.error("❌ Senha incorreta. Tente novamente.")
        st.stop()
    else:
        st.stop()

# ======================================
# 🎨 INTERFACE SÓ APÓS AUTENTICAR
# ======================================

# CSS externo (se existir)
#try:
    #with open("style.css") as f:
        #st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#except FileNotFoundError:
    #pass

#if st.session_state.autenticado: #

if st.session_state.autenticado:

    # 1) CSS EXTERNO → carrega primeiro
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    # 2) CSS INLINE → sobrescreve o style.css
    st.markdown("""
    <style>
        .ccb-titulo {
            font-size: 3.4rem !important;
            font-weight: 900 !important;
            text-align: center !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }

        h2 {
            text-align: center !important;
            font-size: 1.6rem !important;
            font-weight: 600 !important;
            margin-bottom: 1.2rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    # --- JS dos dropdowns ---
    components.html("""
    <script>
    function aplicarEstiloDropdown() {
      const dropdown = document.querySelector('ul[data-testid="stSelectboxVirtualDropdown"]');
      if (dropdown) {
        dropdown.style.backgroundColor = "#ffffff";
        dropdown.style.border = "2px solid #000000";
        dropdown.style.borderRadius = "12px";
        dropdown.style.boxShadow = "0 6px 12px rgba(0,0,0,0.1)";
        dropdown.style.zIndex = "9999";

        const options = dropdown.querySelectorAll('li[role="option"]');
        options.forEach(opt => {
          opt.style.backgroundColor = "#ffffff";
          opt.style.color = "#000000";
          opt.style.padding = "10px 16px";
          opt.style.fontSize = "16px";
          opt.style.borderBottom = "1px solid #eee";
          opt.style.cursor = "pointer";

          opt.addEventListener("mouseenter", () => {
            opt.style.backgroundColor = "#f2f2f2";
          });
          opt.addEventListener("mouseleave", () => {
            opt.style.backgroundColor = "#ffffff";
          });
        });
      }
    }

    const observer = new MutationObserver(() => {
      for (let i = 0; i < 20; i++) {
        setTimeout(aplicarEstiloDropdown, i * 100);
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    aplicarEstiloDropdown();
    </script>
    """, height=0)

# ======================================
# 🔗 CONEXÃO COM GOOGLE SHEETS (via st.secrets)
# ======================================

config = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(
    config,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
client = gspread.authorize(creds)

planilha = client.open("Controle de Presença 2026")
aba_base = planilha.worksheet("BaseDeCriancas")
aba_presencas = planilha.worksheet("Presencas")

# ======================================
# 🔄 CACHE DA BASE
# ======================================
@st.cache_data(ttl=60)
def carregar_base():
    dados = aba_base.get_all_records()
    nomes = [str(linha["Nome Completo"]).strip()
             for linha in dados if linha.get("Nome Completo")]
    return dados, nomes

with st.spinner("🔄 Carregando dados do Google Sheets..."):
    dados_base, nomes_existentes = carregar_base()
    time.sleep(1)

if not dados_base:
    st.error("Não foi possível carregar a base de crianças.")
    st.stop()

# ======= TOPO VISUAL =======
st.markdown('<h1 class="ccb-titulo">Congregação Cristã no Brasil</h1>', unsafe_allow_html=True)
st.markdown("<h2>Espaço Bíblico Infantil – Vila Formosa</h2>", unsafe_allow_html=True)
st.markdown('<div class="ccb-section-title">👶👧🧒 Controle de Presença</div>', unsafe_allow_html=True)

# --- LIMPEZA AUTOMÁTICA ---
if st.session_state.get("limpar", False):
    for campo in [
        "idade_field", "responsavel_field", "telefone_field", "comum_field",
        "pulseira_crianca", "pulseira_resp", "nome_novo", "select_nome",
        "nome_selecionado", "registro_atual", "last_loaded_name"
    ]:
        if campo in st.session_state:
            st.session_state[campo] = ""
    st.session_state.tipo_cadastro = "Cadastro Existente"
    st.session_state.limpar = False

# --- FEEDBACK TEMPORÁRIO ---
if st.session_state.get("feedback"):
    placeholder = st.empty()
    placeholder.success(st.session_state.feedback)
    time.sleep(3)
    placeholder.empty()
    st.session_state.feedback = None

# --- ESTADO DEFAULT ---
defaults = {
    "tipo_cadastro": "Cadastro Existente",
    "nome_selecionado": "",
    "registro_atual": None,
    "last_loaded_name": None,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

for k in ["idade_field", "responsavel_field", "telefone_field", "comum_field",
          "pulseira_crianca", "pulseira_resp", "nome_novo", "select_nome"]:
    st.session_state.setdefault(k, "")

# --- TIPO DE CADASTRO ---
tipo_cadastro = st.selectbox(
    "📋 Tipo de Cadastro",
    ["Cadastro Existente", "Novo Cadastro"],
    index=0 if st.session_state.tipo_cadastro == "Cadastro Existente" else 1,
)
st.session_state.tipo_cadastro = tipo_cadastro

if "ultimo_tipo_cadastro" not in st.session_state:
    st.session_state.ultimo_tipo_cadastro = tipo_cadastro

if st.session_state.ultimo_tipo_cadastro != tipo_cadastro:
    for campo in [
        "idade_field", "responsavel_field", "telefone_field", "comum_field",
        "pulseira_crianca", "pulseira_resp", "nome_novo", "select_nome",
        "nome_selecionado", "registro_atual", "last_loaded_name"
    ]:
        if campo in st.session_state:
            st.session_state[campo] = ""
    st.session_state.ultimo_tipo_cadastro = tipo_cadastro

novo_cadastro = tipo_cadastro == "Novo Cadastro"

# --- SELEÇÃO DA CRIANÇA ---
if not novo_cadastro:
    nomes_filtrados = [str(n).strip() for n in nomes_existentes if n and str(n).strip()]
    nome_atual = st.session_state.get("select_nome", "").strip()

    nome_selecionado = st.selectbox(
        "Selecione a criança",
        [""] + nomes_filtrados,
        index=(nomes_filtrados.index(nome_atual) + 1
               if nome_atual and nome_atual in nomes_filtrados else 0),
        key="select_nome",
    )

    st.session_state.nome_selecionado = nome_selecionado

    if nome_selecionado and st.session_state.last_loaded_name != nome_selecionado:
        registro = next((l for l in dados_base if l["Nome Completo"] == nome_selecionado), None)
        if registro:
            st.session_state.idade_field = str(registro.get("Idade", "")).strip()
            st.session_state.responsavel_field = str(registro.get("Responsável", "")).strip()
            st.session_state.telefone_field = str(registro.get("Telefone para Contato", "")).strip()
            st.session_state.comum_field = str(registro.get("Comum Congregação", "")).strip()
        st.session_state.pulseira_crianca = ""
        st.session_state.pulseira_resp = ""
        st.session_state.last_loaded_name = nome_selecionado
else:
    st.text_input("✍️ Nome completo da nova criança", key="nome_novo")

# --- FORMULÁRIO ---
with st.form("form_presenca", clear_on_submit=False):
    st.text_input("🎂 Idade", key="idade_field")
    st.text_input("👨‍👩 Responsável", key="responsavel_field")
    st.text_input("📞 Telefone para Contato", key="telefone_field")
    st.text_input("Comum Congregação", key="comum_field")
    st.text_input("🧷 Número da Pulseira da Criança", key="pulseira_crianca")
    st.text_input("🧷 Número da Pulseira do Responsável", key="pulseira_resp")

    enviar = st.form_submit_button("✅ Registrar Presença")

# --- FOCO AUTOMÁTICO NO CAMPO DE PULSEIRA ---
if st.session_state.get("nome_selecionado"):
    st.markdown(
        """
        <script>
        const campo = window.parent.document.querySelector('input[id^="pulseira_crianca"]');
        if (campo) { campo.focus(); }
        </script>
        """,
        unsafe_allow_html=True
    )

# --- PROCESSAMENTO DO SUBMIT ---
if enviar:
    nome_final = (st.session_state.get("nome_selecionado") or st.session_state.get("nome_novo", "")).strip()
    if not nome_final:
        st.warning("⚠️ Informe o nome da criança antes de registrar.")
    else:
        datahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Presença
        aba_presencas.append_row([
            datahora,
            nome_final,
            st.session_state.idade_field,
            st.session_state.responsavel_field,
            st.session_state.telefone_field,
            st.session_state.comum_field,
            st.session_state.pulseira_crianca,
            st.session_state.pulseira_resp,
            "Sim" if novo_cadastro else ""
        ])

        # Cadastro / atualização
        datahora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if novo_cadastro:
            aba_base.append_row([
                nome_final,
                st.session_state.idade_field,
                st.session_state.responsavel_field,
                st.session_state.telefone_field,
                st.session_state.comum_field,
                datahora_atual
            ])
            st.warning("🆕 Novo cadastro salvo na base de dados.")
        else:
            for i, linha in enumerate(dados_base):
                if linha["Nome Completo"] == nome_final:
                    novos = [
                        str(st.session_state.idade_field).strip(),
                        str(st.session_state.responsavel_field).strip(),
                        str(st.session_state.telefone_field).strip(),
                        str(st.session_state.comum_field).strip(),
                        datahora_atual
                    ]
                    antigos = [
                        str(linha.get("Idade", "")).strip(),
                        str(linha.get("Responsável", "")).strip(),
                        str(linha.get("Telefone para Contato", "")).strip(),
                        str(linha.get("Comum Congregação", "")).strip(),
                        str(linha.get("Data Última Atualização", "")).strip()
                    ]
                    if novos[:-1] != antigos[:-1]:
                        aba_base.update(f"B{i+2}:F{i+2}", [novos])
                        st.info("🔄 Cadastro existente atualizado com data/hora.")
                    break

        st.session_state.feedback = "✅ Presença registrada com sucesso!"
        st.session_state.tipo_cadastro = "Cadastro Existente"
        st.session_state.limpar = True

        for campo in ["select_nome", "nome_novo", "nome_selecionado", "last_loaded_name"]:
            if campo in st.session_state:
                del st.session_state[campo]

        time.sleep(0.3)
        st.rerun()
