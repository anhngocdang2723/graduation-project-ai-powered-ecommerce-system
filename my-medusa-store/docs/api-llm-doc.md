import os
from openai import OpenAI


client = OpenAI(
    # If the environment variable is not set, replace the following line with: api_key="sk-xxx"
    # API keys for the Singapore and Beijing regions are different. To get an API key, see https://www.alibabacloud.com/help/zh/model-studio/get-api-key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    # The following is the base_url for the Singapore region. If you use a model in the Beijing region, replace the base_url with: https://dashscope.aliyuncs.com/compatible-mode/v1
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",  
)

completion = client.chat.completions.create(
    # This example uses qwen-plus. You can change the model name as needed. For a list of models, see https://www.alibabacloud.com/help/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"},
    ],
    # For Qwen3 models, use the enable_thinking parameter to control the thinking process (default is True for open source models, False for commercial models).
    # When using a Qwen3 open source model without streaming output, uncomment the following line to avoid errors.
    # extra_body={"enable_thinking": False},
)
print(completion.model_dump_json())