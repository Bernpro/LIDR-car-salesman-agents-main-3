"""
Versión "demo" del sistema de ventas de coches que NO requiere ninguna API key.

No llama a OpenAI ni a SerpAPI: usa reglas simples (regex / palabras clave) para
extraer el perfil del cliente y generar respuestas de Carlos con plantillas.
Sirve para poder probar la interfaz de Streamlit sin tener que configurar nada,
y comparte la misma "forma" (mismos métodos públicos) que el sistema real
(`AdvancedCarSalesSystem`) para que `streamlit_app.py` pueda usar uno u otro
sin cambiar el resto del código.
"""

import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from enhanced_inventory_manager import get_inventory_manager


# ---------------------------------------------------------------------------
# Copias mínimas y autocontenidas de las clases de datos que usa el sistema
# real (car_sales_system.py), para que el modo demo no dependa de langchain
# ni de enhanced_inventory_manager.py (que no siempre está disponible).
# ---------------------------------------------------------------------------
class SalesStage(Enum):
    GREETING = "greeting"
    DISCOVERY = "discovery"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


class AgentRole(Enum):
    CARLOS_SALES = "carlos_sales"
    MARIA_RESEARCH = "maria_research"
    MANAGER_COORDINATOR = "manager_coordinator"


@dataclass
class CustomerProfile:
    name: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    preferred_make: Optional[str] = None
    preferred_color: Optional[str] = None
    body_style_preference: Optional[str] = None
    fuel_type_preference: Optional[str] = None
    family_size: Optional[int] = None
    primary_use: Optional[str] = None
    safety_priority: bool = False
    luxury_preference: bool = False
    eco_friendly: bool = False
    needs: List[str] = field(default_factory=list)
    objections: List[str] = field(default_factory=list)
    interaction_history: List[Dict] = field(default_factory=list)


class DemoCarSalesSystem:
    """Sustituto sin API keys de AdvancedCarSalesSystem, con respuestas simuladas."""

    def __init__(self):
        self.customer_profile = CustomerProfile()
        self.sales_stage = SalesStage.GREETING
        self.conversation_log: List[Dict] = []
        self.agent_communications: List[Dict] = []
        self.carlos_customer_notes: List[str] = []
        # El motor de inventario real no necesita ninguna API key (usa pandas/regex),
        # así que el modo demo puede mostrar coches de verdad del CSV.
        self.inventory_manager = get_inventory_manager()

    # ------------------------------------------------------------------
    # Extracción de perfil (misma lógica simplificada que la versión real,
    # basada en reglas, sin necesidad de ningún LLM)
    # ------------------------------------------------------------------
    def _update_customer_profile_from_text(self, text: str) -> None:
        text_lower = text.lower()

        budget_patterns = [
            r"entre\s+(\d+)\s*(?:k|mil|\.000)?\s*(?:y|-)\s*(\d+)\s*(?:k|mil|\.000)?",
            r"(?:menos de|hasta|máximo|max)\s*(\d+)\s*(?:k|mil|\.000)?",
            r"(\d+)\s*(?:k|mil)?\s*(?:€|euros?)",
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                try:
                    if len(groups) == 1 and groups[0]:
                        self.customer_profile.budget_max = int(groups[0]) * (
                            1000 if "k" in match.group(0) or "mil" in match.group(0) else 1
                        )
                    elif len(groups) == 2 and groups[0] and groups[1]:
                        self.customer_profile.budget_min = int(groups[0])
                        self.customer_profile.budget_max = int(groups[1])
                except ValueError:
                    pass
                break

        if any(w in text_lower for w in ["familia", "bebé", "niños", "hijos"]):
            self.customer_profile.safety_priority = True
            if "bebé" in text_lower and "seguridad_infantil" not in self.customer_profile.needs:
                self.customer_profile.needs.append("seguridad_infantil")

        if any(w in text_lower for w in ["trabajo", "oficina", "commute"]):
            self.customer_profile.primary_use = "trabajo"
        elif any(w in text_lower for w in ["familia", "weekend", "viajes"]):
            self.customer_profile.primary_use = "familiar"

        for color in ["rojo", "negro", "blanco", "azul", "gris", "verde"]:
            if color in text_lower:
                self.customer_profile.preferred_color = color.capitalize()
                break

        for style in ["suv", "sedán", "sedan", "hatchback", "coupé", "coupe", "furgoneta"]:
            if style in text_lower:
                self.customer_profile.body_style_preference = style.upper()
                break

        for make in ["toyota", "volkswagen", "seat", "ford", "bmw", "audi", "renault", "peugeot", "hyundai", "kia"]:
            if make in text_lower:
                self.customer_profile.preferred_make = make.capitalize()
                break

        if any(w in text_lower for w in ["eléctrico", "electrico", "híbrido", "hibrido", "ecológico"]):
            self.customer_profile.eco_friendly = True

        if any(w in text_lower for w in ["lujo", "premium", "gama alta"]):
            self.customer_profile.luxury_preference = True

        self.customer_profile.interaction_history.append(
            {"timestamp": datetime.now(), "content": text, "extracted_info": "profile_update"}
        )

    def _get_customer_profile_summary(self) -> str:
        p = self.customer_profile
        parts = []
        if p.budget_max:
            parts.append(f"Presupuesto: hasta €{p.budget_max:,}")
        if p.preferred_make:
            parts.append(f"Marca: {p.preferred_make}")
        if p.preferred_color:
            parts.append(f"Color: {p.preferred_color}")
        if p.body_style_preference:
            parts.append(f"Tipo: {p.body_style_preference}")
        if p.safety_priority:
            parts.append("Prioridad: Seguridad")
        if p.eco_friendly:
            parts.append("Prioridad: Ecológico")
        if p.luxury_preference:
            parts.append("Prioridad: Lujo")
        if p.needs:
            parts.append(f"Necesidades: {', '.join(p.needs)}")
        return "; ".join(parts) if parts else "Perfil básico"

    # ------------------------------------------------------------------
    # Progresión de etapas de venta (simplificada)
    # ------------------------------------------------------------------
    _STAGE_ORDER = [
        SalesStage.GREETING,
        SalesStage.DISCOVERY,
        SalesStage.PRESENTATION,
        SalesStage.OBJECTION_HANDLING,
        SalesStage.NEGOTIATION,
        SalesStage.CLOSING,
    ]

    def _advance_stage(self, text_lower: str) -> None:
        idx = self._STAGE_ORDER.index(self.sales_stage)

        if any(w in text_lower for w in ["caro", "precio", "descuento", "no me alcanza"]):
            self.sales_stage = SalesStage.OBJECTION_HANDLING
            return
        if any(w in text_lower for w in ["comprar", "cerrar", "trato", "acuerdo", "sí, lo quiero", "me lo llevo"]):
            self.sales_stage = SalesStage.CLOSING
            return
        if any(w in text_lower for w in ["precio final", "mejor precio", "financiación", "financiacion", "cuotas"]):
            self.sales_stage = SalesStage.NEGOTIATION
            return

        if idx < len(self._STAGE_ORDER) - 1:
            self.sales_stage = self._STAGE_ORDER[idx + 1]

    # ------------------------------------------------------------------
    # Generación de respuestas simuladas (plantillas, sin LLM)
    # ------------------------------------------------------------------
    _TEMPLATES = {
        SalesStage.GREETING: [
            "¡Hola! Soy Carlos 😊 Cuéntame, ¿qué tipo de coche estás buscando?",
            "¡Bienvenido/a! Encantado de ayudarte a encontrar tu próximo coche. ¿Qué tienes en mente?",
        ],
        SalesStage.DISCOVERY: [
            "Entendido. Para ayudarte mejor, ¿cuál es tu presupuesto aproximado y para qué usarás el coche principalmente?",
            "Perfecto, voy tomando nota. ¿Tienes alguna marca o color preferido?",
        ],
        SalesStage.PRESENTATION: [
            "Con lo que me cuentas, tengo un par de opciones en mente que podrían encajarte muy bien.",
            "Basándome en tus preferencias, creo que tenemos varios modelos que te van a encantar.",
        ],
        SalesStage.OBJECTION_HANDLING: [
            "Entiendo tu preocupación por el precio. Déjame ver qué opciones de financiación o descuentos podemos ofrecerte.",
            "Es una objeción muy común, y tiene solución: podemos hablar de planes de pago flexibles.",
        ],
        SalesStage.NEGOTIATION: [
            "Vamos a ver los números con calma. ¿Qué rango de cuota mensual te resultaría cómodo?",
            "Puedo consultar con mi manager para ver qué margen tenemos en el precio.",
        ],
        SalesStage.CLOSING: [
            "¡Excelente decisión! Vamos a preparar el papeleo para formalizar la compra.",
            "Genial, me alegra que hayas decidido dar el paso. Empecemos con los detalles finales.",
        ],
    }

    def process_customer_input(self, user_input: str) -> str:
        text_lower = user_input.lower()
        self._update_customer_profile_from_text(user_input)
        self._advance_stage(text_lower)

        base_response = random.choice(self._TEMPLATES[self.sales_stage])
        profile_summary = self._get_customer_profile_summary()

        response = base_response
        if profile_summary != "Perfil básico":
            response += f"\n\n_(Perfil detectado hasta ahora: {profile_summary})_"

        # A partir de la etapa de presentación, mostramos coches reales del inventario
        if self.sales_stage in (
            SalesStage.PRESENTATION,
            SalesStage.OBJECTION_HANDLING,
            SalesStage.NEGOTIATION,
            SalesStage.CLOSING,
        ):
            try:
                results = self.inventory_manager.intelligent_search(user_input, max_results=3)
                if results:
                    formatted = self.inventory_manager.format_search_results_for_agent(
                        results, max_display=3
                    )
                    response += f"\n\n{formatted}"
                    note = f"Cliente interesado, {len(results)} coches mostrados en base a: '{user_input[:60]}'"
                    self.carlos_customer_notes.append(note)
            except Exception:
                pass  # Si la búsqueda falla, seguimos con la respuesta base

        response += (
            "\n\n⚠️ *Estás en modo demo: el texto de Carlos es simulado (no usa ningún modelo de IA), "
            "aunque los coches mostrados sí vienen del inventario real. Configura una API key en la "
            "barra lateral para hablar con el Carlos con IA real.*"
        )

        self.conversation_log.append(
            {
                "timestamp": datetime.now(),
                "agent": AgentRole.CARLOS_SALES.value,
                "action": "response_to_customer",
                "details": response,
            }
        )
        return response

    def get_conversation_analytics(self) -> Dict[str, Any]:
        return {
            "total_interactions": len(self.conversation_log),
            "agent_communications": len(self.agent_communications),
            "current_sales_stage": self.sales_stage.value,
            "customer_profile_completeness": self._calculate_profile_completeness(),
            "recent_actions": [log["action"] for log in self.conversation_log[-5:]],
            "communication_flow": [],
        }

    def _calculate_profile_completeness(self) -> float:
        p = self.customer_profile
        total_fields = 10
        filled = sum(
            [
                bool(p.budget_max),
                bool(p.preferred_make),
                bool(p.preferred_color),
                bool(p.body_style_preference),
                bool(p.fuel_type_preference),
                bool(p.family_size),
                bool(p.primary_use),
                bool(p.needs),
                bool(p.safety_priority),
                bool(p.interaction_history),
            ]
        )
        return (filled / total_fields) * 100


def get_demo_multi_agent_system() -> DemoCarSalesSystem:
    """Factory function para el modo demo, sin API keys."""
    return DemoCarSalesSystem()
