from openai import OpenAI
from podcaster.writer.filtering import compare_multilingual_embeddings
from tqdm import tqdm
from datetime import date, timedelta

client = OpenAI(base_url="http://localhost:1206/v1", api_key="lm-studio")

def generate_summaries(topic, lookback=1, score_threshold=0.3, top_k_intact=3, max_k_returned=10):
    instruction = '''Please summarize the input document into one short text, keeping all relevant information.'''
    start_date = date.today() - timedelta(days=lookback)
    end_date = date.today()
    retrieved_documents = compare_multilingual_embeddings(topic, score_threshold=score_threshold, start_date=start_date, end_date=end_date)
    to_summarize_documents = retrieved_documents[top_k_intact:max_k_returned]
    summarized_documents = [f'Title:{article.title}\n{article.content}' for article in retrieved_documents[:top_k_intact]]

    for i, document in tqdm(enumerate(to_summarize_documents), total=len(to_summarize_documents)):
        format_document = f'Title:{document.title}\n{document.content}'
        completion = client.chat.completions.create(
        model="DevQuasar/DISLab.SummLlama3.2-3B-GGUF/DISLab.SummLlama3.2-3B.Q8_0.gguf",
        messages=[
            {"role": "system", 
             "content": "Always do your best. Include only relevant information and discard useless topics. Output only the summary, do not include notes. Always answer in English."},
            {"role": "user",
            "content": f'''Below is an instruction that describes a task. Write a response that appropriately completes the request. Always output in English only.
            \n### Instruction:
            {instruction}
            \n### Input:
            {format_document}\n
            ### Response:\n'''}
        ],
        temperature=0.7,
        max_tokens=400,
        )

        output = completion.choices[0].message.content
        summarized_documents.append(f'Title:{document.title}\n{output}')
    
    return summarized_documents