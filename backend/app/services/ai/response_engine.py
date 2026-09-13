import time
import logging
from langchain_core.messages import HumanMessage, SystemMessage

from app.services.ai.llm import get_llm
from app.services.ai.prompt_builder import build_system_prompt
from app.services.ai.fallbacks import get_fallback_response
from app.services.knowledge_service import kb_service
from app.services.language_detection_service import LanguageDetectionService

logger = logging.getLogger(__name__)


class AIResponseEngine:

    @staticmethod
    async def generate_reply(
        user_message: str,
        conversation_history: list[dict] | None = None,
        organization_name: str = "Mteja AI",
    ) -> dict:
        start_time = time.time()
        detection = LanguageDetectionService.detect(user_message)

        try:
            knowledge_context = kb_service.search(user_message, k=2)

            system_prompt = build_system_prompt(
                user_message=user_message,
                conversation_history=conversation_history,
                knowledge_context=knowledge_context,
                organization_name=organization_name,
            )

            llm = get_llm()
            if llm is None:
                reply = get_fallback_response(detection["language"])
                return {
                    "reply": reply,
                    "success": False,
                    "fallback": True,
                    "language": detection["language"],
                    "latency_ms": int((time.time() - start_time) * 1000),
                }

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message),
            ]

            response = await llm.ainvoke(messages)
            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"AI reply generated | language={detection['language']} | latency={latency_ms}ms"
            )

            return {
                "reply": response.content,
                "success": True,
                "fallback": False,
                "language": detection["language"],
                "is_sheng": detection["is_sheng"],
                "is_code_switching": detection["is_code_switching"],
                "latency_ms": latency_ms,
            }

        except Exception as e:
            logger.error(f"AI response failed: {str(e)}")
            reply = get_fallback_response(detection["language"])
            return {
                "reply": reply,
                "success": False,
                "fallback": True,
                "language": detection["language"],
                "error": str(e),
                "latency_ms": int((time.time() - start_time) * 1000),
            }