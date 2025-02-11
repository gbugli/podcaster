import google.generativeai as genai
from podcaster.config import config
from podcaster.writer.prompts import prompts


google_api_key = config.get('secretKeys')['googleApiKey']
genai.configure(api_key=google_api_key)


text_example = prompts.get('script_example')
prompt = prompts.get('script_prompt')
prompt_multi = prompts.get('script_prompt_multi')

sections = config.get('sections')
hosts = config.get('hostsPersonas')

def generate_script(articles, topic, section='middle'):
    if isinstance(articles, list):
        articles = '\n'.join(articles)
    
    podcast_section = sections[section]
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt.format(topic=topic, text_example=text_example, articles=articles, podcast_section=podcast_section))
    output = response.text
    return output

def generate_script_multi(articles, topic, section='middle'):
    if isinstance(articles, list):
        articles = '\n'.join(articles)

    podcast_section = sections[section]
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(
        prompt_multi.format(
            topic=topic, 
            text_example=text_example, 
            articles=articles, 
            podcast_section=podcast_section,
            hosts=hosts,
            host_num=len(hosts)
        )
    )
    output = response.text
    return output