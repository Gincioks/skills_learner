## Mistral OpenOrca

Smart Model: python3 -m llama_cpp.server --model ./models/mistral_orca/mistral_orca_smart.gguf --n_ctx 8192 --chat_format mistral-orca --n_gpu_layers 1

## Mistral OmniMix

OmniMix Model: python3 -m llama_cpp.server --model ./models/mistral_orca/mistral_omni_mix.gguf --n_ctx 4096 --chat_format mistral-orca --n_gpu_layers 1

## Stable Beluga

Stable_Beluga_7b: python3 -m llama_cpp.server --model ./models/stable_ai/stable_beluga_7b_q8.gguf --n_ctx 4096 --chat_format stable-beluga --n_gpu_layers 1

Stable_Beluga_13b_Q6: python3 -m llama_cpp.server --model ./models/stable_ai/stable_beluga_13b_q6.gguf --n_ctx 4096 --chat_format stable-beluga --n_gpu_layers 1

Stable_Beluga_13b_Q4: python3 -m llama_cpp.server --model ./models/stable_ai/stable_beluga_13b_q4.gguf --n_ctx 4096 --chat_format stable-beluga --n_gpu_layers 1

## CasualLM

CasualLM: python3 -m llama_cpp.server --model ./models/casual_lm/casual_lm_14b_q5.gguf --n_ctx 4096 --chat_format mistral-orca --n_gpu_layers 1
