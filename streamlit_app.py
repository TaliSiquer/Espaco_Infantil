import streamlit as st
from datetime import datetime
import gspread

import streamlit.components.v1 as components
import time

from google.oauth2.service_account import Credentials

# --- 🔐 Lê as credenciais do secrets.toml ---
config = dict(st.secrets["gcp_service_account"])  # copia o conteúdo
config["private_key"] = config["private_key"].replace("\\n", "\n")  # corrige o formato da chave

# --- 🔗 Conexão com Google Sheets ---
creds = Credentials.from_service_account_info(
    config,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(creds)

# (depois disso você pode abrir a planilha normalmente)
planilha = client.open("Controle de Presença 2026")
aba_base = planilha.worksheet("BaseDeCriancas")
aba_presencas = planilha.worksheet("Presencas")

# ======================================
# 🔐 AUTENTICAÇÃO ANTES DE QUALQUER COISA
# ======================================

SENHA_CORRETA = "CCB@2026_espacoinfantil"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Solicita a senha se ainda não autenticou
if not st.session_state.autenticado:
    senha_digitada = st.text_input("🔐 Digite a senha para acessar o formulário:", type="password")

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
# 🎨 TODA INTERFACE A PARTIR DAQUI
# Só é executada se já estiver autenticado
# ======================================

# --- Carrega CSS ---
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if st.session_state.autenticado:


    
    # --- CSS EMBUTIDO ---
    st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], section.main {
        background-color: #fafafa !important;
        color: #000 !important;
        font-family: "Segoe UI", sans-serif !important;
    }

    h1 {
        text-align: center;
        font-size: 2.4rem !important;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    h2 {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }

    .stForm {
        background: #ffffff;
        border: 2px solid #000000;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
    }

    input, textarea, select {
        background-color: #fff !important;
        color: #000 !important;
        border: 1.8px solid #000 !important;
        border-radius: 10px !important;
        padding: 0.6rem !important;
        font-size: 16px !important;
    }

    input:focus, textarea:focus, select:focus {
        border-color: #28a745 !important;
        box-shadow: 0 0 8px rgba(40, 167, 69, 0.35) !important;
        outline: none !important;
    }

    div[data-baseweb="select"], div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000 !important;
        border: 1.8px solid #000 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] svg {
        color: #000 !important;
    }

    div[data-baseweb="select"]:hover {
        border-color: #28a745 !important;
        box-shadow: 0 0 8px rgba(40, 167, 69, 0.25) !important;
    }

    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1.5px solid #000000 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        z-index: 9999 !important;
    }

    ul[role="listbox"] > li {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 15px !important;
        padding: 10px 16px !important;
        border-bottom: 1px solid #eee !important;
    }

    ul[role="listbox"] > li:hover {
        background-color: #f0f0f0 !important;
        color: #000 !important;
    }

    div.stButton {
        display: flex !important;
        justify-content: center !important;
        margin-top: 2rem;
    }

    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border-radius: 12px !important;
        border: 1.5px solid #000000 !important;
        padding: 0.6em 1.8em !important;
        cursor: pointer !important;
        transition: 0.3s ease-in-out !important;
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        transform: translateY(-1px) !important;
    }

    header, div[data-testid="stHeader"], section[data-testid="stHeader"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- JS dos dropdowns ---
    import streamlit.components.v1 as components
    components.html("""
     aplicarEstiloDropdown();
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

      const observer = new MutationObserver(() => {
        for (let i = 0; i < 20; i++) {
          setTimeout(aplicarEstiloDropdown, i * 100);
        }
      });
      observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, height=0)
    # 🔄 Agora seu app segue normalmente: conexão com Sheets, layout, formulário etc.

# --- Conexão com Google Sheets ---
config = dict(st.secrets["gcp_service_account"])
config["private_key"] = config["private_key"].replace("\\n", "\n")

from google.oauth2.service_account import Credentials
import gspread

creds = Credentials.from_service_account_info(
    config,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(creds)

planilha = client.open("Controle de Presença 2026")
aba_base = planilha.worksheet("BaseDeCriancas")
aba_presencas = planilha.worksheet("Presencas")


# --- Cache da base ---
@st.cache_data(ttl=60)
def carregar_base():
    dados = aba_base.get_all_records()
    nomes = [str(linha["Nome Completo"]).strip() for linha in dados if linha.get("Nome Completo")]
    return dados, nomes

# --- Tela de carregamento ---
with st.spinner("🔄 Carregando dados do Google Sheets..."):
    dados_base, nomes_existentes = carregar_base()
    time.sleep(1)  # deixa o spinner visível por 1 segundo para suavizar a transição

# --- SOMENTE APÓS O CARREGAMENTO, EXIBE O APP COMPLETO ---
if dados_base:
    # ======= CONTEÚDO VISUAL DO TOPO =======
    st.markdown('<h1 class="ccb-header">Congregação Cristã no Brasil</h1>', unsafe_allow_html=True)
    st.markdown("<h2>Espaço Infantil – CCB Vila Formosa</h2>", unsafe_allow_html=True)
    st.markdown('<div class="ccb-section-title">👶👧🧒 Controle de Presença</div>', unsafe_allow_html=True)

    # (todo o resto do seu código vem a partir daqui)
 
# --- Limpeza automática no início (se sinalizado) ---
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

# --- Exibe feedback temporário ---
if st.session_state.get("feedback"):
    placeholder = st.empty()  # cria um espaço temporário
    placeholder.success(st.session_state.feedback)
    time.sleep(3)  # tempo em segundos que a mensagem fica visível
    placeholder.empty()  # remove a mensagem
    st.session_state.feedback = None
 
# --- Estado persistente ---
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
 
# --- Tipo de cadastro (fora do forms) ---
tipo_cadastro = st.selectbox(
    "📋 Tipo de Cadastro",
    ["Cadastro Existente", "Novo Cadastro"],
    index=0 if st.session_state.tipo_cadastro == "Cadastro Existente" else 1,
)
st.session_state.tipo_cadastro = tipo_cadastro

# --- Se mudar o tipo de cadastro, limpa os campos visuais (sem afetar a lógica atual) ---
if "ultimo_tipo_cadastro" not in st.session_state:
    st.session_state.ultimo_tipo_cadastro = tipo_cadastro

# Detecta troca (de "existente" → "novo" ou vice-versa)
if st.session_state.ultimo_tipo_cadastro != tipo_cadastro:
    for campo in [
        "idade_field", "responsavel_field", "telefone_field", "comum_field",
        "pulseira_crianca", "pulseira_resp", "nome_novo", "select_nome",
        "nome_selecionado", "registro_atual", "last_loaded_name"
    ]:
        if campo in st.session_state:
            st.session_state[campo] = ""  # zera campos visuais
    st.session_state.ultimo_tipo_cadastro = tipo_cadastro
novo_cadastro = tipo_cadastro == "Novo Cadastro"
 
# --- Seleção da criança (com visual limpo e responsivo) ---
if not novo_cadastro:
    nomes_filtrados = [str(n).strip() for n in nomes_existentes if n and str(n).strip()]
    nome_selecionado = st.selectbox(
        "Selecione a criança",
        [""] + nomes_filtrados,
        index=(nomes_filtrados.index(st.session_state.select_nome.strip()) + 1
               if st.session_state.select_nome and st.session_state.select_nome.strip() in nomes_filtrados else 0),
        key="select_nome",
    )
  
    st.session_state.nome_selecionado = nome_selecionado
    # Carrega os dados automaticamente da base, sem piscar
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
 
# --- Agora sim, o restante dentro do form ---
with st.form("form_presenca", clear_on_submit=False):
    st.text_input("🎂 Idade", key="idade_field")
    st.text_input("👨‍👩 Responsável", key="responsavel_field")
    st.text_input("📞 Telefone para Contato", key="telefone_field")
    st.text_input("Comum Congregação", key="comum_field")
    st.text_input("🧷 Número da Pulseira da Criança", key="pulseira_crianca")
    st.text_input("🧷 Número da Pulseira do Responsável", key="pulseira_resp")
 
    enviar = st.form_submit_button("✅ Registrar Presença")
 
# --- Foco automático só pra existentes ---
if st.session_state.nome_selecionado:
    st.markdown(
        """
        <script>
        const campo = window.parent.document.querySelector('input[id^="pulseira_crianca"]');
        if (campo) { campo.focus(); }
        </script>
        """,
        unsafe_allow_html=True
    )
 
# --- Processamento após submit ---
if enviar:
    nome_final = (st.session_state.get("nome_selecionado") or st.session_state.get("nome_novo", "")).strip()
    if not nome_final:
        st.warning("⚠️ Informe o nome da criança antes de registrar.")
    else:
        datahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
 
        # Grava presença
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
 
                # --- Atualiza ou insere cadastro ---
        datahora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
 
        if novo_cadastro:
            # Novo cadastro → adiciona nova linha na aba base com data/hora
            aba_base.append_row([
                nome_final,
                st.session_state.idade_field,
                st.session_state.responsavel_field,
                st.session_state.telefone_field,
                st.session_state.comum_field,
                datahora_atual  # salva a data e hora do cadastro
            ])
            st.warning("🆕 Novo cadastro salvo na base de dados.")
        else:
            # Cadastro existente → atualiza se houve mudança
            for i, linha in enumerate(dados_base):
                if linha["Nome Completo"] == nome_final:
                    novos = [
                        str(st.session_state.idade_field).strip(),
                        str(st.session_state.responsavel_field).strip(),
                        str(st.session_state.telefone_field).strip(),
                        str(st.session_state.comum_field).strip(),
                        datahora_atual  # atualiza a data/hora da modificação
                    ]
                    antigos = [
                        str(linha.get("Idade", "")).strip(),
                        str(linha.get("Responsável", "")).strip(),
                        str(linha.get("Telefone para Contato", "")).strip(),
                        str(linha.get("Comum Congregação", "")).strip(),
                        str(linha.get("Data Última Atualização", "")).strip()
                    ]
                    if novos[:-1] != antigos[:-1]:  # ignora diferença de data
                        aba_base.update(f"B{i+2}:F{i+2}", [novos])
                        st.info("🔄 Cadastro existente atualizado com data/hora.")
                    break
 
        # --- Feedback e limpeza após envio ---
        st.session_state.feedback = "✅ Presença registrada com sucesso!"
        st.session_state.tipo_cadastro = "Cadastro Existente"
        st.session_state.limpar = True
 
        # Limpeza segura
        for campo in ["select_nome", "nome_novo", "nome_selecionado", "last_loaded_name"]:
            if campo in st.session_state:
                del st.session_state[campo]
 
        time.sleep(0.3)
        st.rerun()