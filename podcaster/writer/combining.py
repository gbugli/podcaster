import os
from podcaster.writer.summarising import generate_summaries
from podcaster.writer.scripting import generate_script, generate_script_multi

def generate_summaries_and_scripts(topic_thresholds, date_obj, multi_host=True, root_path=None, logger=None):

    date_str = date_obj.strftime('%Y%m%d')

    if not root_path:
        root_path = os.get_cwd()

    for i, (topic, threshold) in enumerate(topic_thresholds.items()):
        summaries_path = f'{root_path}/summaries/{date_obj.year}/{date_obj.month}/{date_obj.day}'
        topic_path = f'{summaries_path}/{date_str}.{topic}.md'

        logger.info(f"Summarizing articles for topic: {topic}")
        summarized_documents = generate_summaries(topic, score_threshold=threshold, max_k_returned=10)

        logger.info(f'Retrieved {len(summarized_documents)} articles for {topic}')

        final_docs = '\n'.join(summarized_documents)
        os.makedirs(summaries_path, exist_ok=True)
        logger.info(f"Saving generated summaries to {summaries_path}")
        with open(topic_path, 'w', encoding='utf-8') as f:
            f.write(final_docs)

        if i==0:
            section='start'
        elif i==len(topic_thresholds)-1:
            section='end'
        else:
            section='middle'

        logger.info(f"Generating script for topic: {topic}")
        if multi_host:
            script = generate_script_multi(final_docs, topic, section=section)
            scripts_path = f'{root_path}/scripts/multi_host/{date_obj.year}/{date_obj.month}/{date_obj.day}'
        else:
            script = generate_script(final_docs, topic, section=section)
            scripts_path = f'{root_path}/scripts/single_host/{date_obj.year}/{date_obj.month}/{date_obj.day}'
        os.makedirs(scripts_path, exist_ok=True)
        logger.info(f"Saving generated script to {scripts_path}")
        with open(f'{scripts_path}/{date_str}.{topic}.md', 'w', encoding='utf-8') as f:
            f.write(script)