import langchain

import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import systems
try:
    from advanced_multi_agent_system import get_advanced_multi_agent_system as get_openai_system
    from enhanced_inventory_manager import get_inventory_manager
    from demo_car_sales_system import get_demo_multi_agent_system
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

try:
    from advanced_multi_agent_system_groq import get_advanced_multi_agent_system as get_groq_system
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# --- Page Configuration ---
st.set_page_config(
    page_title="CarBot Pro - AI Car Salesman", 
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sales-metric {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3c72;
    }
    .car-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .agent-status {
        background: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #28a745;
    }
    .agent-communication {
        background: #fff3cd;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #ffc107;
        margin: 0.2rem 0;
        font-size: 0.8rem;
        color: #503e00; /* Darker text for yellow background */
    }
    .log-entry {
        background: #f8f9fa;
        padding: 0.3rem;
        border-radius: 3px;
        margin: 0.1rem 0;
        font-family: monospace;
        font-size: 0.7rem;
        color: #212529; /* Darker text for light gray background */
    }
    .customer-profile {
        background: #e7f3ff; /* Light blue background */
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        color: #002b5c; /* Dark blue text for good contrast */
    }
    .customer-profile p,
    .customer-profile li {
        color: #002b5c; /* Ensure p and li elements also inherit/use dark color */
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🚗 CarBot Pro - Sistema Multiagente Avanzado</h1>
    <p>Demo Profesional para AI Agents Day - Eduardo Hilario, CTO IA For Transport</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("🔧 Configuración del Sistema")
    
    # Agent Type Selection
    st.markdown("**🤖 Sistema Multiagente Profesional**")
    st.markdown("- **Carlos**: Vendedor experto")
    st.markdown("- **María**: Especialista en investigación")
    st.markdown("- **Edu**: Coordinador de negocio")
    
    st.markdown("---")
    
    # Mode Selection
    st.subheader("🎛️ Modo del Sistema")
    mode_options = ["demo", "groq", "openai"] if GROQ_AVAILABLE else ["demo", "openai"]
    mode_labels = {
        "demo": "🎮 Demo (sin API keys)",
        "groq": "⚡ Groq (gratis, con IA real)",
        "openai": "🤖 OpenAI (de pago)",
    }
    selected_mode = st.radio(
        "Elige cómo quieres ejecutar el sistema",
        options=mode_options,
        format_func=lambda k: mode_labels[k],
        index=0,
        help=(
            "Demo: respuestas simuladas, pero con coches reales del inventario. No necesita nada.\n\n"
            "Groq: IA real y gratuita (https://console.groq.com/keys).\n\n"
            "OpenAI: IA real, de pago."
        ),
    )

    st.markdown("---")
    
    # API Keys (solo si el modo lo requiere)
    openai_api_key = ""
    groq_api_key = ""
    serpapi_api_key = ""

    if selected_mode != "demo":
        st.subheader("🔑 Claves API")
        default_serpapi_key = os.getenv('SERPAPI_API_KEY', '')

        if selected_mode == "groq":
            default_groq_key = os.getenv('GROQ_API_KEY', '')
            groq_api_key = st.text_input(
                "Groq API Key",
                value=default_groq_key,
                type="password",
                placeholder="gsk_...",
                help="Gratis en https://console.groq.com/keys"
            )
        elif selected_mode == "openai":
            default_openai_key = os.getenv('OPENAI_API_KEY', '')
            openai_api_key = st.text_input(
                "OpenAI API Key",
                value=default_openai_key,
                type="password",
                placeholder="sk-...",
                help="Requerida para los modelos de OpenAI"
            )

        serpapi_api_key = st.text_input(
            "SerpAPI Key",
            value=default_serpapi_key,
            type="password",
            placeholder="Opcional para búsqueda web",
            help="Opcional: permite a María hacer investigación web en tiempo real"
        )
    
    # Initialize Agent Button
    can_initialize = (
        selected_mode == "demo"
        or (selected_mode == "groq" and groq_api_key)
        or (selected_mode == "openai" and openai_api_key)
    )
    if st.button("🚀 Inicializar Sistema Avanzado", type="primary"):
        if can_initialize:
            with st.spinner("Inicializando sistema multiagente avanzado..."):
                try:
                    if selected_mode == "demo":
                        st.session_state.agent_system = get_demo_multi_agent_system()
                    elif selected_mode == "groq":
                        st.session_state.agent_system = get_groq_system(groq_api_key, serpapi_api_key)
                    else:
                        st.session_state.agent_system = get_openai_system(openai_api_key, serpapi_api_key)

                    st.session_state.agent_type = f"advanced_multiagent_{selected_mode}"
                    st.session_state.system_initialized = True
                    
                    st.success("✅ Sistema avanzado inicializado correctamente!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error al inicializar: {e}")
                    st.session_state.system_initialized = False
        else:
            st.error(f"❌ Falta la API key requerida para el modo {mode_labels[selected_mode]}")
    
    st.markdown("---")
    
    # System Status
    st.subheader("📊 Estado del Sistema")
    if st.session_state.get('system_initialized', False):
        st.markdown('<div class="agent-status">🟢 Sistema Operativo</div>', unsafe_allow_html=True)
        st.write(f"**Tipo:** {st.session_state.get('agent_type', 'Unknown')}")
        
        st.write("**Agentes Activos:**")
        st.write("- 🎯 Carlos (Ventas)")
        st.write("- 🔍 María (Investigación)")
        st.write("- 👔 Edu (Coordinación)")
        
        # Show system analytics if available
        if hasattr(st.session_state.agent_system, 'get_conversation_analytics'):
            analytics = st.session_state.agent_system.get_conversation_analytics()
            st.write("**Estadísticas:**")
            st.write(f"- Interacciones: {analytics.get('total_interactions', 0)}")
            st.write(f"- Comunicaciones entre agentes: {analytics.get('agent_communications', 0)}")
            st.write(f"- Etapa de venta: {analytics.get('current_sales_stage', 'N/A')}")
            st.write(f"- Perfil completado: {analytics.get('customer_profile_completeness', 0):.1f}%")
    else:
        st.warning("⚠️ Sistema no inicializado")
    
    st.markdown("---")
    
    # Debug Mode Toggle
    st.subheader("🔧 Modo Debug")
    debug_mode = st.checkbox("Mostrar logs detallados del sistema", value=True)
    show_agent_comms = st.checkbox("Mostrar comunicaciones entre agentes", value=True)

# Initialize demo_concluded state if not present
if 'demo_concluded' not in st.session_state:
    st.session_state.demo_concluded = False

# --- Main Content ---
if not st.session_state.get('system_initialized', False):
    # Welcome Screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ## 🎯 Bienvenido a CarBot Pro Avanzado
        
        ### ¿Qué hace especial a este sistema?
        
        **🤖 Arquitectura Multiagente Profesional:**
        - **Carlos** - Vendedor experto con 15 años de experiencia
        - **María** - Especialista en investigación automotriz
        - **Edu** - Coordinador de negocio y políticas
        
        **🔧 Capacidades Avanzadas:**
        - ✅ Búsqueda inteligente en inventario enriquecido
        - ✅ Investigación web en tiempo real
        - ✅ Perfilado automático de clientes
        - ✅ Negociación entre agentes
        - ✅ Logs detallados y analytics
        - ✅ Manejo profesional de objeciones
        
        **📈 Flujo de Venta Profesional:**
        1. **Saludo y Rapport** - Carlos construye confianza
        2. **Descubrimiento** - Identifica necesidades del cliente
        3. **Consulta a Edu** - Obtiene prioridades de inventario
        4. **Presentación** - Muestra vehículos relevantes
        5. **Investigación** - María proporciona datos técnicos
        6. **Negociación** - Edu autoriza descuentos
        7. **Cierre** - Finalización profesional
        
        **🎯 Demo Script Incluido:**
        - Escenarios de venta realistas
        - Casos de uso familiares
        - Manejo de objeciones
        - Negociación de precios
        
        👈 **Elige un modo (Demo, Groq o OpenAI) e inicializa el sistema en el panel lateral.
        El modo Demo no requiere ninguna API key.**
        """)

else:
    # Main Application Layout
    col1, col2 = st.columns([2, 1]) # Define columns for the main layout

    with col1: # Chat Area
        st.subheader("💬 Chat con CarBot Pro")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            welcome_msg = """¡Hola! Soy **Carlos**, tu vendedor de coches personal con IA avanzada. 
Tengo 15 años de experiencia ayudando a familias a encontrar el vehículo perfecto. Trabajo en equipo con **María** (nuestra especialista en investigación) y **Edu** (nuestro Manager) para ofrecerte el mejor servicio.
¿En qué puedo ayudarte hoy? ¿Buscas algo específico o quieres que te recomiende opciones basadas en tus necesidades?
💡 *Tip: Puedes decirme cosas como "busco un coche seguro para mi familia" o "necesito un sedan rojo de menos de 2 años"*"""
            st.session_state.messages.append({
                "role": "assistant", "content": welcome_msg,
                "timestamp": datetime.now(), "agent": "Carlos"
            })

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if not st.session_state.get('demo_concluded', False):
            if user_input := st.chat_input("¿Qué estás buscando hoy?", key="customer_chat_input_active"):
                st.session_state.messages.append({
                    "role": "user", "content": user_input,
                    "timestamp": datetime.now(), "agent": "Cliente"
                })
                
                with st.spinner("Carlos está pensando..."):
                    if hasattr(st.session_state, 'agent_system') and st.session_state.agent_system:
                        try:
                            carlos_response = st.session_state.agent_system.process_customer_input(user_input)
                            st.session_state.messages.append({
                                "role": "assistant", "content": carlos_response,
                                "timestamp": datetime.now(), "agent": "Carlos"
                            })
                            if "ha sido reservado exitosamente" in carlos_response or \
                               "proceso de compra ha concluido" in carlos_response:
                                st.session_state.demo_concluded = True
                                if hasattr(st.session_state.agent_system, 'inventory_manager'):
                                    st.session_state.agent_system.inventory_manager.load_inventory()
                                st.rerun() 
                        except Exception as e:
                            st.error(f"Error al procesar la entrada: {e}")
                            st.session_state.messages.append({"role": "assistant", "content": f"Lo siento, ocurrió un error interno: {e}"})
                        if not st.session_state.get('demo_concluded', False): # Rerun if not concluded by this response
                           st.rerun()
                    else:
                        st.error("El sistema de agentes no está inicializado.")
        
        elif st.session_state.get('demo_concluded', False): # Chat input area when demo is concluded
            st.info("Chat deshabilitado. La demo ha concluido.")

        # Sale conclusion message and Restart button (still within col1, below chat area)
        if st.session_state.get('demo_concluded', False):
            st.success("🎉 ¡Venta Concluida! El vehículo ha sido reservado.")
            st.info("Para una nueva demo, por favor reinicia.")
            if st.button("🔁 Reiniciar Demo", key="restart_demo_button_col1"):
                keys_to_reset = ['messages', 'agent_system', 'system_initialized', 'demo_concluded', 'agent_type']
                for key in keys_to_reset:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    # Information Panel (col2) - should always render if system is initialized
    if st.session_state.get('system_initialized', False):
        with col2:
            st.subheader("⚙️ Información del Sistema y Cliente")

            # Display Customer Profile
            if st.session_state.get('system_initialized', False) and hasattr(st.session_state.agent_system, 'customer_profile'):
                profile = st.session_state.agent_system.customer_profile
                with st.expander("👤 Perfil del Cliente (detectado por Carlos)", expanded=True):
                    st.markdown('<div class="customer-profile">', unsafe_allow_html=True)
                    if profile.name: st.markdown(f"**Nombre:** {profile.name}")
                    if profile.budget_min or profile.budget_max:
                        budget_str = "Presupuesto: "
                        if profile.budget_min: budget_str += f"desde €{profile.budget_min:,} "
                        if profile.budget_max: budget_str += f"hasta €{profile.budget_max:,}"
                        st.markdown(f"**{budget_str.strip()}**")
                    if profile.preferred_make: st.markdown(f"**Marca Preferida:** {profile.preferred_make}")
                    if profile.preferred_color: st.markdown(f"**Color Preferido:** {profile.preferred_color}")
                    if profile.body_style_preference: st.markdown(f"**Estilo Preferido:** {profile.body_style_preference}")
                    if profile.fuel_type_preference: st.markdown(f"**Combustible:** {profile.fuel_type_preference}")
                    if profile.family_size: st.markdown(f"**Tamaño Familiar:** {profile.family_size}")
                    if profile.primary_use: st.markdown(f"**Uso Principal:** {profile.primary_use}")
                    
                    prefs = []
                    if profile.safety_priority: prefs.append("Alta Seguridad")
                    if profile.luxury_preference: prefs.append("Lujo")
                    if profile.eco_friendly: prefs.append("Ecológico")
                    if prefs: st.markdown(f"**Prioridades:** {', '.join(prefs)}")
                    
                    if profile.needs:
                        st.markdown("**Necesidades Detectadas:**")
                        for need in profile.needs: st.markdown(f"- {need}")
                    if profile.objections:
                        st.markdown("**Objeciones/Preocupaciones:**")
                        for obj in profile.objections: st.markdown(f"- {obj}")
                
                    if not any([profile.name, profile.budget_min, profile.budget_max, profile.preferred_make, 
                                profile.preferred_color, profile.body_style_preference, profile.fuel_type_preference,
                                profile.family_size, profile.primary_use, prefs, profile.needs, profile.objections]):
                        st.markdown("Aún no se ha detectado información específica del perfil.")
                    st.markdown('</div>', unsafe_allow_html=True)

            # Display Carlos's Customer Notes
            if st.session_state.get('system_initialized', False) and hasattr(st.session_state.agent_system, 'carlos_customer_notes'):
                notes = st.session_state.agent_system.carlos_customer_notes
                with st.expander("📝 Notas de Carlos sobre el Cliente", expanded=False):
                    if notes:
                        st.markdown('<div class="agent-communication" style="border-left-color: #6f42c1; background-color: #f3e8ff; color: #3d236b;">', unsafe_allow_html=True) # Purple-ish theme
                        for i, note in enumerate(notes, 1):
                            st.markdown(f"**Nota {i}:** {note}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("Carlos aún no ha tomado notas personales sobre este cliente.")
            
            # Display Recent Inventory (Simplified)
            if st.session_state.get('system_initialized', False):
                st.subheader("📊 Inventario de Vehículos")
                if hasattr(st.session_state, 'agent_system') and st.session_state.agent_system and hasattr(st.session_state.agent_system, 'inventory_manager'):
                    inventory_df_display = st.session_state.agent_system.inventory_manager.inventory_df.copy()
                    if 'status' not in inventory_df_display.columns:
                         inventory_df_display['status'] = 'Available'
                    
                    def highlight_status(row):
                        if row['status'] == 'Reserved':
                            return ['background-color: lightcoral'] * len(row)
                        return [''] * len(row)

                    display_columns = ['make', 'model', 'year', 'price', 'mileage', 'status', 'vin']
                    display_columns = [col for col in display_columns if col in inventory_df_display.columns]
                    
                    if display_columns:
                        st.dataframe(
                            inventory_df_display[display_columns].style.apply(highlight_status, axis=1), 
                            height=300, width='stretch'
                        )
                    else:
                        st.warning("Columnas de inventario no encontradas.")
                else:
                    st.info("Inventario no disponible.")

            if debug_mode or show_agent_comms:
                st.subheader("📡 Comunicaciones Recientes entre Agentes")
                if show_agent_comms and hasattr(st.session_state, 'agent_system') and \
                   st.session_state.agent_system and st.session_state.agent_system.agent_communications:
                    if st.session_state.agent_system.agent_communications:
                        for comm in reversed(st.session_state.agent_system.agent_communications[-10:]):
                            with st.expander(f"{comm.timestamp.strftime('%H:%M:%S')}: {comm.from_agent.value} ➡️ {comm.to_agent.value} ({comm.message_type})", expanded=False):
                                st.markdown(f"<div class='agent-communication'>{comm.content}</div>", unsafe_allow_html=True)
                    else:
                        st.info("Sin comunicaciones entre agentes.")
                elif show_agent_comms:
                    st.info("Comunicaciones no disponibles.")

            if debug_mode:
                st.subheader("⚙️ Log del Sistema (Últimas Acciones)")
                if hasattr(st.session_state, 'agent_system') and \
                   st.session_state.agent_system and st.session_state.agent_system.conversation_log:
                    if st.session_state.agent_system.conversation_log:
                        for log in reversed(st.session_state.agent_system.conversation_log[-15:]):
                            log_content = f"{log['timestamp'].strftime('%H:%M:%S')} | {log['agent']} | {log['action']} | {str(log['details'])[:100]}"
                            st.markdown(f"<div class='log-entry'>{log_content}</div>", unsafe_allow_html=True)
                    else:
                        st.info("Sin logs del sistema.")
                else:
                    st.info("Logs del sistema no disponibles.")

# --- Footer ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🎯 Demo para AI Agents Day**")
    st.markdown("Presentado por Eduardo Hilario")
    st.markdown("CTO - IA For Transport")

with col2:
    st.markdown("**🔧 Tecnologías Utilizadas**")
    st.markdown("GPT-5 • LangChain • Streamlit • Python")
    st.markdown("Sistema Multiagente Avanzado")

with col3:
    st.markdown("**📊 Estado del Sistema**")
    if st.session_state.get('system_initialized', False):
        st.markdown("🟢 **Sistema Operativo**")
        st.markdown("✅ **Todos los agentes activos**")
    else:
        st.markdown("🔴 **Sistema Inactivo**")
        st.markdown("⚠️ **Requiere inicialización**") 