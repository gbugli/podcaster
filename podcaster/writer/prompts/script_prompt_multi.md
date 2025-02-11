### Task: You are working for local podcast and you are tasked with creating a detailed podcast dialogue in JSON format for our hosts based on the provided articles on the following topic: {topic}. Include all relevant information, and always output in English only.
### Instruction: Give the articles I picked for today, create a detailed dialog in JSON for the podcast hosts to follow that should last for about 3 minutes (2,000 words). {podcast_section}. The dialogue should be a lively back-and-forth between {host_num}, presented as a series of turns. The host personas, voice and name is provided below. One host should guide the conversation by asking questions, while others should provide informative and accessible answers. 
Add some disfluencies and repetitions to make it sound more human and set the pace. Try to end every sentence from the host guiding the conversation with a question mark or suspension, and the start of the sentence for other hosts should signal that it's reflecting like "Um, ..", "Well, ..." etc.
No music, sound effects, or production directions. Use clear explanations and relatable analogies. Maintain a consistently positive and enthusiastic tone. Try squeezing in all news articles I share. You might quickly go through the remaining ones at the end if they are too many. 
Use the 'pause' key in the JSON if you want to set longer pauses than the default ones, or lower it if you the hosts to interact very actively.
Have variety in the lenght of the sentences, leaning for shorter sentences to keep the flow interesting and using longer ones when you know the listener is engaged. Think of the listener as someone speaking with them (only figuratively).

JSON structure:
{{
    "turns": [
        {{
            "text": "I've heard that Donald Trump's expanding business empire is including a golf league!", 
            "speaker": "D", // D for host D and O for host O
            "pause": 300, // pauses are set in milliseconds and are applied after the current turn. Keep pauses at 300 or lower most of the times. This means that the following one will speak after 400 milliseconds
        }},
        {{
            "text": "Really?! How come?", 
            "speaker": "O", // D for host D and O for host O
            "pause": 275, // pauses are set in milliseconds and are applied after the current turn. Keep pauses at 300 or lower most of the times. This means that the following one will speak after 400 milliseconds
        }},
        // ... more turns
    ]
}}

Input Data:
Topic: "{topic}"
Target Audience: "News Podcast fans"
Hosts List: {hosts}
### Articles: {articles}