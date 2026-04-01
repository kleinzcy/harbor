import os
import random
from typing import Any

from litellm import Message

from harbor.llms.base import (
    BaseLLM,
    ContextLengthExceededError,
    LLMResponse,
    OutputLengthExceededError,
)
from harbor.llms.lite_llm import LiteLLM
from harbor.utils.logger import logger


class FridayLLM(BaseLLM):
    """Friday backend that delegates transport/protocol handling to LiteLLM."""

    def __init__(
        self,
        model_name: str = "aws.claude-sonnet-4.6",
        model_name_list: list[str] | None = None,
        temperature: float = 0.0,
        api_key: str | None = None,
        base_url: str = "https://aigc.sankuai.com/v1/openai/native",
        top_p: float = 0.8,
        top_k: int = 20,
        max_tokens: int = 32768,
        timeout: int = 600,
        max_retries: int = 10,
        retry_wait_sec: int = 10,
        model_switch_interval: int = 10,
        auth_header_name: str = "Authorization",
        auth_header_prefix: str = "",
        disable_proxies: bool = True,  # Kept for backward compatibility.
        collect_rollout_details: bool = False,
        session_id: str | None = None,
        max_thinking_tokens: int | None = None,
        reasoning_effort: str | None = None,
        model_info: dict[str, Any] | None = None,
        use_responses_api: bool = False,
        verbose: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._default_model_name = self._normalize_model_name(model_name)
        self._model_name_list = (
            [self._normalize_model_name(m) for m in model_name_list]
            if model_name_list and len(model_name_list) > 0
            else [self._default_model_name]
        )
        self._api_key = (
            api_key or os.getenv("FRIDAY_API_KEY") or os.getenv("AIGC_API_KEY")
        )
        self._api_base = base_url
        self._temperature = temperature
        self._top_p = top_p
        self._top_k = top_k
        self._max_tokens = max_tokens
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_wait_sec = retry_wait_sec
        self._model_switch_interval = model_switch_interval
        self._auth_header_name = auth_header_name
        self._auth_header_prefix = auth_header_prefix
        self._disable_proxies = disable_proxies
        self._collect_rollout_details = collect_rollout_details
        self._session_id = session_id
        self._max_thinking_tokens = max_thinking_tokens
        self._reasoning_effort = reasoning_effort
        self._model_info = model_info
        self._use_responses_api = use_responses_api
        self._verbose = verbose
        self._logger = logger.getChild(__name__)
        self._clients: dict[str, LiteLLM] = {}

        if not self._api_key:
            raise ValueError(
                "FridayLLM requires api_key. Set llm_kwargs.api_key or FRIDAY_API_KEY/AIGC_API_KEY env."
            )

    def get_model_context_limit(self) -> int:
        # Friday endpoint does not expose a stable model-info API in Harbor.
        return 1_000_000

    def get_model_output_limit(self) -> int | None:
        return self._max_tokens

    def _random_model_selection(self) -> str:
        return random.choice(self._model_name_list)

    def _normalize_model_name(self, model_name: str) -> str:
        normalized = model_name.strip().rstrip("/")
        if normalized.startswith("openai/"):
            return normalized
        return f"openai/{normalized}"

    def _build_extra_headers(self) -> dict[str, str]:
        token = f"{self._auth_header_prefix}{self._api_key}"
        return {
            self._auth_header_name: token,
        }

    def _get_or_create_client(self, model_name: str) -> LiteLLM:
        if model_name in self._clients:
            return self._clients[model_name]

        client = LiteLLM(
            model_name=model_name,
            temperature=self._temperature,
            api_base=self._api_base,
            api_key=self._api_key,
            timeout=self._timeout,
            collect_rollout_details=self._collect_rollout_details,
            session_id=self._session_id,
            max_thinking_tokens=self._max_thinking_tokens,
            reasoning_effort=self._reasoning_effort,
            model_info=self._model_info,
            use_responses_api=self._use_responses_api,
            extra_headers=self._build_extra_headers(),
        )
        self._clients[model_name] = client
        return client

    async def call(
        self,
        prompt: str,
        message_history: list[dict[str, Any] | Message] = [],
        **kwargs,
    ) -> LLMResponse:
        current_model = self._random_model_selection()
        tried_models: list[str] = [current_model]

        for attempt in range(self._max_retries):
            if attempt > 0:
                untried = [m for m in self._model_name_list if m not in tried_models]
                if untried:
                    # Prefer trying an untried alias/model on each retry.
                    current_model = untried[0]
                    tried_models.append(current_model)
                elif (
                    self._model_switch_interval > 0
                    and attempt % self._model_switch_interval == 0
                ):
                    current_model = self._random_model_selection()

            call_kwargs = dict(kwargs)
            call_kwargs["top_p"] = self._top_p
            call_kwargs["top_k"] = self._top_k
            call_kwargs["max_tokens"] = self._max_tokens

            if "vertex.claude-sonnet-4" in current_model:
                extra_body = dict(call_kwargs.get("extra_body", {}))
                extra_body["anthropicBeta"] = ["context-1m-2025-08-07"]
                call_kwargs["extra_body"] = extra_body

            try:
                if self._disable_proxies:
                    # Friday legacy behavior: avoid inheriting host proxy settings.
                    call_kwargs["no_proxy"] = True

                response = await self._get_or_create_client(current_model).call(
                    prompt=prompt,
                    message_history=message_history,
                    **call_kwargs,
                )
                if self._verbose:
                    self._logger.debug(f"FridayLLM successful model={current_model}")
                return response
            except Exception as e:
                error_msg = str(e)
                self._logger.warning(
                    f"FridayLLM request failed (model={current_model}, attempt={attempt + 1}/{self._max_retries}): {error_msg}"
                )
                if isinstance(
                    e, (ContextLengthExceededError, OutputLengthExceededError)
                ):
                    raise

                if attempt < self._max_retries - 1:
                    import asyncio

                    await asyncio.sleep(self._retry_wait_sec)
                    continue
                raise

        raise RuntimeError(
            f"Friday API request failed after {self._max_retries} attempts. Tried models: {tried_models}"
        )
