from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

def load_prompt(key: str) -> str:
    try:
        prompt_path = get_abs_path(prompts_conf[key])
    except KeyError:
        logger.error(f"缺少{key}配置项")
        raise

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取{key}失败：{e}")
        raise


def load_system_prompts():
    return load_prompt("main_prompt_path")


def load_rag_summarize_prompts():
    return load_prompt("rag_summarize_prompt_path")


def load_report_prompts():
    return load_prompt("report_prompt_path")

system_prompt = load_system_prompts()
rag_prompt = load_rag_summarize_prompts()
report_prompt = load_report_prompts()

if __name__ == "__main__":
    print(load_system_prompts())
    print(load_rag_summarize_prompts())
    print(load_report_prompts())